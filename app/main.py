import os
import uuid
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.database import get_connection, init_db
from app.routers import enquiries, categories, products, hampers, orders, gallery


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield


app = FastAPI(title="Gift Management API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(enquiries.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(hampers.router)
app.include_router(orders.router)
app.include_router(gallery.router)

app.include_router(enquiries.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(hampers.router)
app.include_router(orders.router)
app.include_router(gallery.router)


@app.get("/api/banners/active")
def get_active_banner():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title, event, note, image_url
        FROM banners
        WHERE is_active = TRUE
        ORDER BY id DESC
        LIMIT 1
    """)

    banner = cursor.fetchone()

    cursor.close()
    connection.close()

    if not banner:
        return {"success": True, "data": None}

    return {
        "success": True,
        "data": {
            "id": banner[0],
            "title": banner[1],
            "event": banner[2],
            "note": banner[3],
            "image_url": banner[4]
        }
    }


@app.post("/api/admin/banners")
async def upload_banner(
    title: Optional[str] = Form(None),
    event: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    image: UploadFile = File(...)
):
    os.makedirs("uploads/banners", exist_ok=True)

    if not image.content_type.startswith("image/"):
        return {
            "success": False,
            "message": "Only image files are allowed"
        }

    extension = os.path.splitext(image.filename)[1] or ".jpg"

    filename = f"{uuid.uuid4()}{extension}"

    file_path = os.path.join("uploads/banners", filename)

    with open(file_path, "wb") as file:
        file.write(await image.read())

    image_url = f"/uploads/banners/{filename}"

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Deactivate all existing banners
        cursor.execute("UPDATE banners SET is_active = FALSE")

        cursor.execute(
            """
            INSERT INTO banners (title, event, note, image_url, is_active)
            VALUES (%s, %s, %s, %s, TRUE)
            RETURNING id
            """,
            (title or event or "Promotional Banner", event, note, image_url)
        )

        banner_id = cursor.fetchone()[0]

        connection.commit()

        return {
            "success": True,
            "message": "New banner uploaded and set active. Previous banner deactivated.",
            "data": {
                "id": banner_id,
                "title": title or event,
                "event": event,
                "note": note,
                "image_url": image_url
            }
        }
    except Exception as err:
        connection.rollback()
        return {
            "success": False,
            "message": f"Database error: {str(err)}"
        }
    finally:
        cursor.close()
        connection.close()


app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

app.mount(
    "/demo",
    StaticFiles(directory="demo", html=True),
    name="demo"
)

app.mount(
    "/",
    StaticFiles(directory="frontend", html=True),
    name="frontend"
)
