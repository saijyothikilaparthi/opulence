import os
import re
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, status, UploadFile, File
from app.database import get_connection
from app.schemas import EnquiryCreate
from app.services.media_storage import MediaStorageError, delete_media, save_media
from app.services.whatsapp import send_whatsapp_notification

router = APIRouter(prefix="/api/enquiries", tags=["Enquiries"])

ENQUIRY_STATUSES = {"pending", "contacted", "order_confirmed", "order_canceled"}


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_enquiry_references(
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Upload one or more reference photos/files for gifting enquiries.
    Stores them on the configured media backend and returns accessible URLs.
    """
    all_files: List[UploadFile] = []
    if files:
        all_files.extend(files)
    if file:
        all_files.append(file)

    if not all_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided for upload."
        )

    uploaded_urls = []
    # Files are served back from the site's own origin, so the stored extension must be a
    # known-safe type (no .svg/.html, which a browser could execute)
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".heic", ".heif", ".pdf"}

    try:
        for upload_item in all_files:
            ext = os.path.splitext(upload_item.filename or "")[1].lower()

            if ext not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File '{upload_item.filename}' has unsupported format. Only images and PDF files are accepted."
                )

            content = await upload_item.read()
            # Max file size 15MB
            if len(content) > 15 * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File '{upload_item.filename}' exceeds maximum allowed size of 15MB."
                )

            try:
                saved = save_media(
                    content,
                    upload_item.filename,
                    upload_item.content_type,
                    folder="references",
                )
            except MediaStorageError as exc:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Could not store file '{upload_item.filename}': {exc}",
                )
            uploaded_urls.append(saved["url"])
    except Exception:
        # Don't leave earlier files of a failed batch behind
        for url in uploaded_urls:
            delete_media(url)
        raise

    return {
        "success": True,
        "message": f"Successfully uploaded {len(uploaded_urls)} reference file(s)",
        "urls": uploaded_urls,
        "url": uploaded_urls[0] if uploaded_urls else None
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_enquiry(enquiry: EnquiryCreate, background_tasks: BackgroundTasks):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO enquiries (
                enquiry_type, name, phone, email, company_name, place,
                occasion, quantity, budget, required_date, theme,
                customization_details, personalize_hamper, file_url, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
            RETURNING id, created_at
            """,
            (
                enquiry.enquiry_type.value,
                enquiry.name,
                enquiry.phone,
                enquiry.email,
                enquiry.company_name,
                enquiry.place,
                enquiry.occasion,
                enquiry.quantity,
                enquiry.budget,
                enquiry.required_date,
                enquiry.theme,
                enquiry.customization_details,
                enquiry.personalize_hamper,
                enquiry.file_url,
            )
        )

        row = cursor.fetchone()
        enquiry_id = row[0]
        connection.commit()

        enquiry_dict = enquiry.model_dump()
        enquiry_dict["id"] = enquiry_id

        # Send admin WhatsApp after successful DB save; runs in background and never affects the enquiry.
        background_tasks.add_task(send_whatsapp_notification, enquiry_dict)

        return {
            "success": True,
            "message": "Enquiry submitted successfully",
            "data": {
                "enquiry_id": enquiry_id,
                "enquiry_type": enquiry.enquiry_type.value,
                "name": enquiry.name,
                "phone": enquiry.phone,
                "status": "pending"
            }
        }

    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record enquiry: {str(e)}"
        )
    finally:
        cursor.close()
        connection.close()


@router.get("/admin", status_code=status.HTTP_200_OK)
def list_enquiries():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT id, enquiry_type, name, phone, email, company_name, place,
                   occasion, quantity, budget, required_date, theme,
                   customization_details, personalize_hamper, file_url, status, created_at
            FROM enquiries
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()

        enquiries = [
            {
                "id": r[0],
                "enquiry_type": r[1],
                "name": r[2],
                "phone": r[3],
                "email": r[4],
                "company_name": r[5],
                "place": r[6],
                "occasion": r[7],
                "quantity": r[8],
                "budget": float(r[9]) if r[9] is not None else None,
                "required_date": str(r[10]) if r[10] is not None else None,
                "theme": r[11],
                "customization_details": r[12],
                "personalize_hamper": r[13],
                "file_url": r[14],
                "status": r[15],
                "created_at": r[16].isoformat() if r[16] is not None else None
            }
            for r in rows
        ]

        return {
            "success": True,
            "data": enquiries
        }
    finally:
        cursor.close()
        connection.close()


@router.put("/admin/{enquiry_id}/status", status_code=status.HTTP_200_OK)
def update_enquiry_status(enquiry_id: int, status_data: dict):
    new_status = str((status_data or {}).get("status", "")).strip().lower()
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status field is required"
        )
    if new_status not in ENQUIRY_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{new_status}'. Allowed: {', '.join(sorted(ENQUIRY_STATUSES))}"
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE enquiries
            SET status = %s
            WHERE id = %s
            RETURNING id, status
            """,
            (new_status, enquiry_id)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enquiry not found"
            )

        connection.commit()
        return {
            "success": True,
            "message": "Enquiry status updated successfully",
            "data": {
                "enquiry_id": row[0],
                "status": row[1]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update status: {str(e)}"
        )
    finally:
        cursor.close()
        connection.close()


@router.delete("/admin/{enquiry_id}", status_code=status.HTTP_200_OK)
def delete_enquiry(enquiry_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM enquiries WHERE id = %s RETURNING id, file_url", (enquiry_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enquiry not found"
            )

        connection.commit()

        # Remove any uploaded reference files too (external links are skipped)
        for ref in re.split(r"[,|]", row[1] or ""):
            delete_media(ref.strip())

        return {
            "success": True,
            "message": f"Enquiry #{enquiry_id} deleted successfully"
        }
    finally:
        cursor.close()
        connection.close()
