from pathlib import Path
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, UploadFile, File, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services.live_service import live_service
from app.services.history_service import history_service


router = APIRouter()


@router.get("/live/status")
def live_status():
    return {
        "success": True,
        "message": "Live monitoring service is running."
    }


@router.websocket("/live/webcam")
async def live_webcam_detection(
    websocket: WebSocket,
    enable_plate_ocr: bool = Query(False),
    save_logs: bool = Query(False)
):
    await websocket.accept()

    host = websocket.headers.get("host", "127.0.0.1:8000")
    base_url = f"http://{host}"

    try:
        while True:
            data = await websocket.receive_json()

            image_data = data.get("image")

            if not image_data:
                await websocket.send_json(
                    {
                        "success": False,
                        "message": "No image frame received."
                    }
                )
                continue

            result = live_service.process_frame(
                image_data=image_data,
                base_url=base_url,
                enable_plate_ocr=enable_plate_ocr,
                save_logs=save_logs
            )

            await websocket.send_json(result)

    except WebSocketDisconnect:
        print("Live webcam client disconnected.")

    except Exception as e:
        await websocket.send_json(
            {
                "success": False,
                "message": f"Live detection failed: {str(e)}"
            }
        )
        await websocket.close()


@router.post("/live/upload-recording")
async def upload_live_recording(
    request: Request,
    file: UploadFile = File(...),
    total_vehicles: int = Query(0),
    total_persons: int = Query(0),
    total_number_plates: int = Query(0),
    db: Session = Depends(get_db)
):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No video file uploaded.")

        extension = Path(file.filename).suffix.lower()

        if extension not in [".webm", ".mp4"]:
            extension = ".webm"

        filename = f"webcam_recording_{uuid.uuid4().hex}{extension}"
        output_path = settings.OUTPUT_DIR / filename

        content = await file.read()

        with open(output_path, "wb") as f:
            f.write(content)

        base_url = str(request.base_url).rstrip("/")
        output_video_url = f"{base_url}/outputs/{output_path.name}"

        session = history_service.save_webcam_video_result(
            db=db,
            output_video_url=output_video_url,
            total_vehicles=total_vehicles,
            total_persons=total_persons,
            total_number_plates=total_number_plates
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Live webcam recording saved successfully.",
                "session_id": session.id,
                "input_type": "webcam_video",
                "output_video_url": output_video_url,
                "total_vehicles": total_vehicles,
                "total_persons": total_persons,
                "total_number_plates": total_number_plates
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload live recording: {str(e)}"
        )