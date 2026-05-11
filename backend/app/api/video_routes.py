from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.video_utils import validate_video_file, save_uploaded_video
from app.services.video_service import video_service
from app.services.history_service import history_service


router = APIRouter()


@router.post("/analyze/video")
async def analyze_video(
    request: Request,
    file: UploadFile = File(...),
    enable_plate_ocr: bool = Query(False),
    db: Session = Depends(get_db)
):
    try:
        validate_video_file(file)

        uploaded_video_path = await save_uploaded_video(file)

        base_url = str(request.base_url).rstrip("/")

        result = video_service.process_video(
            video_path=uploaded_video_path,
            base_url=base_url,
            enable_plate_ocr=enable_plate_ocr
        )

        input_video_url = f"{base_url}/uploads/{uploaded_video_path.name}"
        output_video_url = result["output_video_url"]

        saved_session = history_service.save_video_detection_result(
            db=db,
            input_video_url=input_video_url,
            output_video_url=output_video_url,
            result=result
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Video detection and tracking completed successfully.",
                "session_id": saved_session.id,
                "input_video_url": input_video_url,
                "output_video_url": output_video_url,
                "video_info": result["video_info"],
                "total_frames_processed": result["total_frames_processed"],
                "total_vehicle_detections": result["total_vehicle_detections"],
                "total_person_detections": result["total_person_detections"],
                "total_plate_detections": result["total_plate_detections"],
                "unique_tracked_objects": result["unique_tracked_objects"],
                "unique_vehicles": result["unique_vehicles"],
                "unique_persons": result["unique_persons"],
                "vehicle_type_counts": result["vehicle_type_counts"],
                "plate_texts": result["plate_texts"]
            }
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Video detection failed: {str(e)}"
        )