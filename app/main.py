import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.auth import admin_auth_middleware
from app.database import init_db
from app.routers import admin_auth, enquiries, categories, products, hampers, orders, gallery, announcements


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield


app = FastAPI(title="Gift Management API", lifespan=lifespan)

# Registered before CORS so CORS remains the outermost middleware.
app.middleware("http")(admin_auth_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # The site uses no cookies or auth headers; a wildcard origin must not carry credentials
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_auth.router)
app.include_router(enquiries.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(hampers.router)
app.include_router(orders.router)
app.include_router(gallery.router)
app.include_router(announcements.router)


# Admin console lives at /admin. These routes must be registered before the
# static mounts below, otherwise the "/" mount would swallow the request.
@app.get("/admin/login", include_in_schema=False)
def admin_login_page():
    return FileResponse("demo/admin-login.html")


@app.get("/admin", include_in_schema=False)
def admin_console():
    return FileResponse("demo/admin.html")


@app.get("/admin/", include_in_schema=False)
@app.get("/demo/admin.html", include_in_schema=False)
@app.get("/demo/admin", include_in_schema=False)
def admin_console_redirect():
    return RedirectResponse(url="/admin", status_code=301)


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
