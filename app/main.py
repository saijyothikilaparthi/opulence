from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
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
    # The site uses no cookies or auth headers; a wildcard origin must not carry credentials
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(enquiries.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(hampers.router)
app.include_router(orders.router)
app.include_router(gallery.router)


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
