from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine
from app.models.db_models import Base
from app.config import settings

from app.api import image_routes
from app.api import video_routes
from app.api import live_routes
from app.api import history_routes
from app.api import analytics_routes


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-based vehicle, number plate and person recognition backend"
)

# CORS origins for local + deployed frontend
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

if settings.FRONTEND_URL and settings.FRONTEND_URL not in allowed_origins:
    allowed_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create storage folders
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
settings.CROP_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Create database tables
Base.metadata.create_all(bind=engine)

# Static files
app.mount(
    "/uploads",
    StaticFiles(directory=str(settings.UPLOAD_DIR)),
    name="uploads"
)

app.mount(
    "/outputs",
    StaticFiles(directory=str(settings.OUTPUT_DIR)),
    name="outputs"
)

app.mount(
    "/crops",
    StaticFiles(directory=str(settings.CROP_DIR)),
    name="crops"
)

app.mount(
    "/reports",
    StaticFiles(directory=str(settings.REPORT_DIR)),
    name="reports"
)

# API routes
app.include_router(
    image_routes.router,
    prefix=settings.API_PREFIX,
    tags=["Image Detection"]
)

app.include_router(
    video_routes.router,
    prefix=settings.API_PREFIX,
    tags=["Video Detection"]
)

app.include_router(
    live_routes.router,
    prefix=settings.API_PREFIX,
    tags=["Live Monitoring"]
)

app.include_router(
    history_routes.router,
    prefix=settings.API_PREFIX,
    tags=["Detection History"]
)

app.include_router(
    analytics_routes.router,
    prefix=settings.API_PREFIX,
    tags=["Analytics"]
)


@app.get("/")
def root():
    return {
        "success": True,
        "message": "AI Vehicle Recognition Backend Running Successfully",
        "version": settings.VERSION
    }


@app.get("/health")
@app.get(f"{settings.API_PREFIX}/health")
def health_check():
    return {
        "success": True,
        "message": "Backend is healthy",
        "version": settings.VERSION
    }