from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import (
    DetectionSession,
    VehicleDetection,
    PersonDetection,
    PlateDetection
)
from app.services.report_service import report_service


router = APIRouter()


@router.get("/history")
def get_detection_history(db: Session = Depends(get_db)):
    sessions = (
        db.query(DetectionSession)
        .order_by(DetectionSession.created_at.desc())
        .all()
    )

    data = []

    for session in sessions:
        data.append(
            {
                "id": session.id,
                "input_type": session.input_type,
                "input_file_url": session.input_file_url,
                "output_file_url": session.output_file_url,
                "total_detections": session.total_detections,
                "total_vehicles": session.total_vehicles,
                "total_persons": session.total_persons,
                "total_number_plates": session.total_number_plates,
                "created_at": session.created_at.isoformat()
            }
        )

    return {
        "success": True,
        "message": "Detection history fetched successfully.",
        "data": data
    }


@router.get("/history/{session_id}")
def get_detection_details(session_id: int, db: Session = Depends(get_db)):
    session = (
        db.query(DetectionSession)
        .filter(DetectionSession.id == session_id)
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Detection session not found."
        )

    vehicles = (
        db.query(VehicleDetection)
        .filter(VehicleDetection.session_id == session_id)
        .all()
    )

    persons = (
        db.query(PersonDetection)
        .filter(PersonDetection.session_id == session_id)
        .all()
    )

    plates = (
        db.query(PlateDetection)
        .filter(PlateDetection.session_id == session_id)
        .all()
    )

    return {
        "success": True,
        "message": "Detection details fetched successfully.",
        "data": {
            "session": {
                "id": session.id,
                "input_type": session.input_type,
                "input_file_url": session.input_file_url,
                "output_file_url": session.output_file_url,
                "total_detections": session.total_detections,
                "total_vehicles": session.total_vehicles,
                "total_persons": session.total_persons,
                "total_number_plates": session.total_number_plates,
                "created_at": session.created_at.isoformat()
            },
            "vehicles": [
                {
                    "id": item.id,
                    "label": item.label,
                    "confidence": item.confidence,
                    "vehicle_model": item.vehicle_model,
                    "vehicle_model_confidence": item.vehicle_model_confidence,
                    "crop_url": item.crop_url,
                    "box": {
                        "x1": item.x1,
                        "y1": item.y1,
                        "x2": item.x2,
                        "y2": item.y2
                    }
                }
                for item in vehicles
            ],
            "persons": [
                {
                    "id": item.id,
                    "label": item.label,
                    "confidence": item.confidence,
                    "person_type": item.person_type,
                    "person_type_confidence": item.person_type_confidence,
                    "crop_url": item.crop_url,
                    "box": {
                        "x1": item.x1,
                        "y1": item.y1,
                        "x2": item.x2,
                        "y2": item.y2
                    }
                }
                for item in persons
            ],
            "number_plates": [
                {
                    "id": item.id,
                    "label": item.label,
                    "plate_text": item.plate_text,
                    "detection_confidence": item.detection_confidence,
                    "ocr_confidence": item.ocr_confidence,
                    "crop_url": item.crop_url,
                    "box": {
                        "x1": item.x1,
                        "y1": item.y1,
                        "x2": item.x2,
                        "y2": item.y2
                    }
                }
                for item in plates
            ]
        }
    }


@router.get("/history/{session_id}/report")
def download_detection_report(session_id: int, db: Session = Depends(get_db)):
    session = (
        db.query(DetectionSession)
        .filter(DetectionSession.id == session_id)
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Detection session not found."
        )

    vehicles = (
        db.query(VehicleDetection)
        .filter(VehicleDetection.session_id == session_id)
        .all()
    )

    persons = (
        db.query(PersonDetection)
        .filter(PersonDetection.session_id == session_id)
        .all()
    )

    plates = (
        db.query(PlateDetection)
        .filter(PlateDetection.session_id == session_id)
        .all()
    )

    report_path = report_service.generate_session_report(
        session=session,
        vehicles=vehicles,
        persons=persons,
        plates=plates
    )

    return FileResponse(
        path=str(report_path),
        media_type="application/pdf",
        filename=f"detection_report_session_{session_id}.pdf"
    )


@router.delete("/history/{session_id}")
def delete_detection_session(session_id: int, db: Session = Depends(get_db)):
    session = (
        db.query(DetectionSession)
        .filter(DetectionSession.id == session_id)
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Detection session not found."
        )

    db.delete(session)
    db.commit()

    return {
        "success": True,
        "message": "Detection session deleted successfully."
    }