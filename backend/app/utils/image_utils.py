from pathlib import Path
import uuid
import cv2
from fastapi import UploadFile, HTTPException

from app.config import settings


def validate_image_file(file: UploadFile):
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPG, JPEG, PNG and WEBP images are allowed."
        )


def generate_unique_filename(original_filename: str) -> str:
    extension = Path(original_filename).suffix.lower()

    if extension == "":
        extension = ".jpg"

    return f"{uuid.uuid4().hex}{extension}"


async def save_uploaded_image(file: UploadFile) -> Path:
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    filename = generate_unique_filename(file.filename)
    file_path = settings.UPLOAD_DIR / filename

    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    return file_path


def read_image(image_path: Path):
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError("Unable to read image. Please upload a valid image file.")

    return image


def draw_box(image, box, label: str, confidence: float, color=(0, 255, 0)):
    x1 = box["x1"]
    y1 = box["y1"]
    x2 = box["x2"]
    y2 = box["y2"]

    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        color,
        2
    )

    text = f"{label} {confidence:.2f}"

    cv2.putText(
        image,
        text,
        (x1, max(y1 - 10, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2
    )

    return image


def save_output_image(image, original_image_path: Path) -> Path:
    settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_filename = f"detected_{original_image_path.name}"
    output_path = settings.OUTPUT_DIR / output_filename

    cv2.imwrite(str(output_path), image)

    return output_path


def crop_image(image, box, padding: int = 5):
    height, width = image.shape[:2]

    x1 = max(0, box["x1"] - padding)
    y1 = max(0, box["y1"] - padding)
    x2 = min(width, box["x2"] + padding)
    y2 = min(height, box["y2"] + padding)

    cropped = image[y1:y2, x1:x2]

    return cropped


def save_crop_image(crop, prefix: str = "crop") -> Path:
    settings.CROP_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{prefix}_{uuid.uuid4().hex}.jpg"
    crop_path = settings.CROP_DIR / filename

    cv2.imwrite(str(crop_path), crop)

    return crop_path