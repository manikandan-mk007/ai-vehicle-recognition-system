from pathlib import Path
import uuid
import cv2
import subprocess
import imageio_ffmpeg
from fastapi import UploadFile, HTTPException

from app.config import settings


def validate_video_file(file: UploadFile):
    extension = Path(file.filename).suffix.lower()

    valid_content_type = file.content_type in settings.ALLOWED_VIDEO_TYPES
    valid_extension = extension in settings.ALLOWED_VIDEO_EXTENSIONS

    if not valid_content_type and not valid_extension:
        raise HTTPException(
            status_code=400,
            detail="Invalid video type. Only MP4, AVI, MOV and MKV videos are allowed."
        )


def generate_unique_video_filename(original_filename: str) -> str:
    extension = Path(original_filename).suffix.lower()

    if extension == "":
        extension = ".mp4"

    return f"{uuid.uuid4().hex}{extension}"


async def save_uploaded_video(file: UploadFile) -> Path:
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    filename = generate_unique_video_filename(file.filename)
    file_path = settings.UPLOAD_DIR / filename

    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    return file_path


def get_video_info(video_path: Path):
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise ValueError("Unable to open video file.")

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_seconds = total_frames / fps if fps > 0 else 0

    cap.release()

    return {
        "fps": fps,
        "width": width,
        "height": height,
        "total_frames": total_frames,
        "duration_seconds": round(duration_seconds, 2)
    }


def get_raw_output_video_path(input_video_path: Path) -> Path:
    settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_filename = f"raw_processed_{input_video_path.stem}.mp4"
    output_path = settings.OUTPUT_DIR / output_filename

    return output_path


def get_final_output_video_path(input_video_path: Path) -> Path:
    settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_filename = f"processed_{input_video_path.stem}.mp4"
    output_path = settings.OUTPUT_DIR / output_filename

    return output_path


def create_video_writer(output_path: Path, fps: float, width: int, height: int):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        str(output_path),
        fourcc,
        fps,
        (width, height)
    )

    if not writer.isOpened():
        raise ValueError("Unable to create video writer.")

    return writer


def convert_to_browser_mp4(raw_video_path: Path, final_video_path: Path):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    command = [
        ffmpeg_exe,
        "-y",
        "-i",
        str(raw_video_path),
        "-vcodec",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(final_video_path)
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise ValueError(f"FFmpeg conversion failed: {result.stderr}")

    return final_video_path