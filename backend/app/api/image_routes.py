from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.image_utils import validate_image_file, save_uploaded_image, read_image
from app.services.detection_service import detection_service
from app.services.plate_ocr_service import plate_ocr_service
from app.services.history_service import history_service


router = APIRouter()


@router.post("/analyze/image")
async def analyze_image(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        validate_image_file(file)

        uploaded_image_path = await save_uploaded_image(file)

        base_url = str(request.base_url).rstrip("/")

        detection_result = detection_service.detect_from_image(
            image_path=uploaded_image_path,
            base_url=base_url
        )

        input_image_url = f"{base_url}/uploads/{uploaded_image_path.name}"
        output_image_url = f"{base_url}/outputs/{detection_result['output_path'].name}"

        vehicles = detection_result["vehicles"]
        persons = detection_result["persons"]
        number_plates = detection_result["number_plates"]

        saved_session = history_service.save_image_detection_result(
            db=db,
            input_image_url=input_image_url,
            output_image_url=output_image_url,
            vehicles=vehicles,
            persons=persons,
            number_plates=number_plates
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Image detection completed successfully.",
                "session_id": saved_session.id,
                "input_image_url": input_image_url,
                "output_image_url": output_image_url,
                "total_detections": len(vehicles) + len(persons) + len(number_plates),
                "total_vehicles": len(vehicles),
                "total_persons": len(persons),
                "total_number_plates": len(number_plates),
                "vehicles": vehicles,
                "persons": persons,
                "number_plates": number_plates
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
            detail=f"Image detection failed: {str(e)}"
        )


@router.post("/analyze/plate")
async def analyze_plate_only(request: Request, file: UploadFile = File(...)):
    try:
        validate_image_file(file)

        uploaded_image_path = await save_uploaded_image(file)

        image = read_image(uploaded_image_path)

        base_url = str(request.base_url).rstrip("/")

        number_plates = plate_ocr_service.detect_and_read_plates(
            image=image,
            image_path=uploaded_image_path,
            base_url=base_url
        )

        input_image_url = f"{base_url}/uploads/{uploaded_image_path.name}"

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Number plate detection and OCR completed successfully.",
                "input_image_url": input_image_url,
                "total_number_plates": len(number_plates),
                "number_plates": number_plates
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
            detail=f"Plate detection failed: {str(e)}"
        )