from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Vehicle Recognition System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    DATABASE_URL: str = "sqlite:///./vehicle_detection.db"

    BACKEND_BASE_URL: str = "http://127.0.0.1:8000"
    FRONTEND_URL: str = "http://localhost:5173"

    MODEL_DIR: Path = BASE_DIR / "trained_models"

    VEHICLE_DETECTOR_PATH: Path = MODEL_DIR / "vehicle_detector.pt"
    PLATE_DETECTOR_PATH: Path = MODEL_DIR / "plate_detector.pt"

    VEHICLE_MODEL_CLASSIFIER_PATH: Path = MODEL_DIR / "vehicle_model_classifier.pth"
    VEHICLE_MODEL_CLASSES_PATH: Path = MODEL_DIR / "vehicle_model_classes.json"

    PERSON_TYPE_CLASSIFIER_PATH: Path = MODEL_DIR / "person_type_classifier.pth"
    PERSON_TYPE_CLASSES_PATH: Path = MODEL_DIR / "person_type_classes.json"

    STORAGE_DIR: Path = BASE_DIR / "app" / "storage"
    UPLOAD_DIR: Path = STORAGE_DIR / "uploads"
    OUTPUT_DIR: Path = STORAGE_DIR / "outputs"
    CROP_DIR: Path = STORAGE_DIR / "crops"
    REPORT_DIR: Path = STORAGE_DIR / "reports"

    ALLOWED_IMAGE_TYPES: list[str] = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp"
    ]

    ALLOWED_VIDEO_TYPES: list[str] = [
        "video/mp4",
        "video/avi",
        "video/x-msvideo",
        "video/quicktime",
        "video/x-matroska",
        "video/webm"
    ]

    ALLOWED_VIDEO_EXTENSIONS: list[str] = [
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".webm"
    ]

    VEHICLE_CLASSES: list[str] = [
        "bicycle",
        "bus",
        "car",
        "motorcycle",
        "truck"
    ]

    PERSON_CLASS: str = "person"

    CONFIDENCE_THRESHOLD: float = 0.35

    VIDEO_PROCESS_EVERY_N_FRAMES: int = 1
    VIDEO_OCR_EVERY_N_FRAMES: int = 30
    MAX_VIDEO_SECONDS: int = 120

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()