from fastapi import APIRouter, HTTPException, status
from app.database import get_connection
from app.schemas import EnquiryCreate
from app.services.whatsapp import send_whatsapp_notification

router = APIRouter(prefix="/api/enquiries", tags=["Enquiries"])


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
                customization_details, file_url, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
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
                   customization_details, file_url, status, created_at
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
                "file_url": r[12],
                "status": r[13],
                "created_at": r[14].isoformat() if r[14] is not None else None,
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
