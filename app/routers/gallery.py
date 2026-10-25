import os
import uuid
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import Optional
from app.database import get_connection

router = APIRouter(prefix="/api/gallery", tags=["Gallery"])

UPLOAD_DIR = "uploads/gallery"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("", status_code=status.HTTP_200_OK)
def list_gallery_work(category: Optional[str] = None):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        if category:
            cursor.execute("SELECT id, title, category, image_url, description, created_at FROM gallery_work WHERE category = %s ORDER BY created_at DESC", (category,))
        else:
            cursor.execute("SELECT id, title, category, image_url, description, created_at FROM gallery_work ORDER BY created_at DESC")
        rows = cursor.fetchall()
        gallery = [
            {
                "id": r[0],
                "title": r[1],
                "category": r[2],
                "image_url": r[3],
                "description": r[4],
                "created_at": r[5].isoformat() if r[5] else None
            }
            for r in rows
        ]
        return {"success": True, "data": gallery}
    finally:
        cursor.close()
        connection.close()


@router.post("/admin", status_code=status.HTTP_201_CREATED)
async def upload_gallery_work(
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    image: UploadFile = File(...)
):
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed."
        )

    file_extension = os.path.splitext(image.filename)[1] or ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await image.read())

    image_url = f"/uploads/gallery/{unique_filename}"

    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO gallery_work (title, category, image_url, description)
            VALUES (%s, %s, %s, %s)
            RETURNING id, image_url
            """,
            (title, category, image_url, description)
        )
        row = cursor.fetchone()
        connection.commit()
        return {
            "success": True,
            "message": "Work image uploaded successfully",
            "data": {"id": row[0], "image_url": row[1]}
        }
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@router.delete("/admin/{work_id}", status_code=status.HTTP_200_OK)
def delete_gallery_work(work_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM gallery_work WHERE id = %s RETURNING image_url", (work_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work image not found")
        connection.commit()
        return {"success": True, "message": f"Gallery work #{work_id} deleted"}
    finally:
        cursor.close()
        connection.close()
