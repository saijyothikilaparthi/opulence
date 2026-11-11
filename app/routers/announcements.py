import os
import uuid
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.database import get_connection

router = APIRouter(tags=["Announcements"])

UPLOAD_DIR = "uploads/banners"
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _row_to_item(r):
    return {
        "id": r[0],
        "title": r[1],
        "event": r[2],
        "category": r[3],
        "upcoming_text": r[4],
        "offer_text": r[5],
        "description": r[6],
        "image_url": r[7],
        "upcoming_title": r[8],
        "upcoming_description": r[9],
        "upcoming_image_url": r[10],
        "status": r[11],
        "display_order": r[12],
        "is_active": r[13],
        "created_at": r[14].isoformat() if r[14] else None,
    }

SELECT_COLS = "id, title, event, category, upcoming_text, offer_text, description, image_url, upcoming_title, upcoming_description, upcoming_image_url, status, display_order, is_active, created_at"


@router.get("/api/announcements", status_code=status.HTTP_200_OK)
def list_announcements(status_filter: Optional[str] = None, active_only: bool = False):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        query = f"SELECT {SELECT_COLS} FROM announcements WHERE 1=1"
        params = []
        if active_only:
            query += " AND is_active = TRUE"
        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)
        query += " ORDER BY display_order ASC, created_at DESC, id DESC"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return {"success": True, "data": [_row_to_item(r) for r in rows]}
    finally:
        cursor.close()
        connection.close()


@router.get("/api/banners/active", status_code=status.HTTP_200_OK)
@router.get("/api/announcements/active", status_code=status.HTTP_200_OK)
def get_active_announcement():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"""
            SELECT {SELECT_COLS}
            FROM announcements
            WHERE is_active = TRUE
            ORDER BY CASE WHEN status = 'running' THEN 0 WHEN status = 'upcoming' THEN 1 ELSE 2 END,
                     display_order ASC, created_at DESC, id DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        if not row:
            return {"success": True, "data": None}
        return {"success": True, "data": _row_to_item(row)}
    finally:
        cursor.close()
        connection.close()


@router.post("/api/announcements/admin", status_code=status.HTTP_201_CREATED)
@router.post("/api/banners/admin", status_code=status.HTTP_201_CREATED)
async def create_announcement(
    title: Optional[str] = Form(None),
    event: Optional[str] = Form(None),
    category: Optional[str] = Form("upcoming_event"),
    upcoming_text: Optional[str] = Form(None),
    offer_text: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    upcoming_title: Optional[str] = Form(None),
    upcoming_description: Optional[str] = Form(None),
    status: Optional[str] = Form("upcoming"),
    display_order: Optional[int] = Form(0),
    is_active: Optional[bool] = Form(True),
    image: UploadFile = File(...),
    upcoming_image: Optional[UploadFile] = File(None),
):
    async def save_image(upload: Optional[UploadFile], required: bool = False):
        if not upload or not upload.filename:
            if required:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image is required.")
            return None
        file_extension = os.path.splitext(upload.filename or "")[1].lower()
        if not (upload.content_type or "").startswith("image/") or file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only JPG, PNG, WEBP or GIF images are allowed.")
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        content = await upload.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        return f"/uploads/banners/{unique_filename}", file_path

    image_result = await save_image(image, required=True)
    image_url, image_path = image_result
    upcoming_image_url = None
    upcoming_image_path = None
    upcoming_result = await save_image(upcoming_image, required=False)
    if upcoming_result:
        upcoming_image_url, upcoming_image_path = upcoming_result

    status_value = (status or "upcoming").strip().lower()
    if status_value not in {"upcoming", "running", "archived"}:
        status_value = "upcoming"
    category_value = (category or "upcoming_event").strip().lower()
    if category_value not in {"upcoming_event", "offer", "announcement"}:
        category_value = "upcoming_event"

    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"""
            INSERT INTO announcements (title, event, category, upcoming_text, offer_text, description, image_url, upcoming_title, upcoming_description, upcoming_image_url, status, display_order, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING {SELECT_COLS}
            """,
            (
                title or event,
                event or title,
                category_value,
                upcoming_text,
                offer_text,
                description,
                image_url,
                upcoming_title,
                upcoming_description,
                upcoming_image_url,
                status_value,
                display_order or 0,
                True if is_active is None else bool(is_active),
            ),
        )
        row = cursor.fetchone()
        connection.commit()
        return {"success": True, "message": "Announcement uploaded successfully", "data": _row_to_item(row)}
    except Exception as e:
        connection.rollback()
        for p in [image_path, upcoming_image_path]:
            if p and os.path.exists(p):
                os.remove(p)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@router.put("/api/announcements/admin/{announcement_id}/status", status_code=status.HTTP_200_OK)
@router.put("/api/banners/admin/{announcement_id}/status", status_code=status.HTTP_200_OK)
def update_announcement_status(announcement_id: int, payload: dict):
    new_status = str((payload or {}).get("status", "")).strip().lower()
    if new_status not in {"upcoming", "running", "archived"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    is_active = (payload or {}).get("is_active")
    connection = get_connection()
    cursor = connection.cursor()
    try:
        if is_active is None:
            cursor.execute(
                "UPDATE announcements SET status = %s WHERE id = %s RETURNING id",
                (new_status, announcement_id),
            )
        else:
            cursor.execute(
                "UPDATE announcements SET status = %s, is_active = %s WHERE id = %s RETURNING id",
                (new_status, bool(is_active), announcement_id),
            )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")
        connection.commit()
        return {"success": True, "message": "Announcement updated"}
    finally:
        cursor.close()
        connection.close()


@router.delete("/api/announcements/admin/{announcement_id}", status_code=status.HTTP_200_OK)
@router.delete("/api/banners/admin/{announcement_id}", status_code=status.HTTP_200_OK)
def delete_announcement(announcement_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM announcements WHERE id = %s RETURNING image_url, upcoming_image_url", (announcement_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")
        connection.commit()
        for url in [row[0], row[1]]:
            stored_name = os.path.basename(url or "")
            stored_path = os.path.join(UPLOAD_DIR, stored_name)
            if url and str(url).startswith("/uploads/banners/") and os.path.isfile(stored_path):
                os.remove(stored_path)
        return {"success": True, "message": f"Announcement #{announcement_id} deleted"}
    finally:
        cursor.close()
        connection.close()
