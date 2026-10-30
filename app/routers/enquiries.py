import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from app.database import get_connection
from app.schemas import EnquiryCreate
from app.services.whatsapp import send_whatsapp_notification

router = APIRouter(prefix="/api/enquiries", tags=["Enquiries"])

UPLOAD_DIR = "uploads/references"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_enquiry_references(
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Upload one or more reference photos/files for gifting enquiries.
    Saves them in uploads/references and returns accessible static URLs.
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

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    uploaded_urls = []
    # Files are served back from the site's own origin, so the stored extension must be a
    # known-safe type (no .svg/.html, which a browser could execute)
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".heic", ".heif", ".pdf"}

    for upload_item in all_files:
        ext = os.path.splitext(upload_item.filename or "")[1].lower()

        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{upload_item.filename}' has unsupported format. Only images and PDF files are accepted."
            )

        unique_filename = f"{uuid.uuid4()}{ext}"
        target_path = os.path.join(UPLOAD_DIR, unique_filename)

        content = await upload_item.read()
        # Max file size 15MB
        if len(content) > 15 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{upload_item.filename}' exceeds maximum allowed size of 15MB."
            )

        with open(target_path, "wb") as f:
            f.write(content)

        url_path = f"/uploads/references/{unique_filename}"
        uploaded_urls.append(url_path)

    return {
        "success": True,
        "message": f"Successfully uploaded {len(uploaded_urls)} reference file(s)",
        "urls": uploaded_urls,
        "url": uploaded_urls[0] if uploaded_urls else None
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_enquiry(enquiry: EnquiryCreate):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO enquiries (
                enquiry_type, name, phone, email, company_name,
                occasion, quantity, budget, required_date, theme,
                customization_details, personalize_hamper, file_url, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
            RETURNING id, created_at
            """,
            (
                enquiry.enquiry_type.value,
                enquiry.name,
                enquiry.phone,
                enquiry.email,
                enquiry.company_name,
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

        # Trigger isolated notification without blocking
        send_whatsapp_notification(enquiry_dict)

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
            SELECT id, enquiry_type, name, phone, email, company_name,
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
                "occasion": r[6],
                "quantity": r[7],
                "budget": float(r[8]) if r[8] is not None else None,
                "required_date": str(r[9]) if r[9] is not None else None,
                "theme": r[10],
                "customization_details": r[11],
                "personalize_hamper": r[12],
                "file_url": r[13],
                "status": r[14],
                "created_at": r[15].isoformat() if r[15] is not None else None,
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
    new_status = status_data.get("status")
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status field is required"
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
        cursor.execute("DELETE FROM enquiries WHERE id = %s RETURNING id", (enquiry_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enquiry not found"
            )

        connection.commit()
        return {
            "success": True,
            "message": f"Enquiry #{enquiry_id} deleted successfully"
        }
    finally:
        cursor.close()
        connection.close()
