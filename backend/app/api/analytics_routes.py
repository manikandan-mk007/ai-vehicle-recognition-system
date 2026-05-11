from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.analytics_service import analytics_service


router = APIRouter()


@router.get("/analytics/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    data = analytics_service.get_summary(db)

    return {
        "success": True,
        "message": "Analytics summary fetched successfully.",
        "data": data
    }


@router.get("/analytics/charts")
def get_analytics_charts(db: Session = Depends(get_db)):
    return {
        "success": True,
        "message": "Analytics chart data fetched successfully.",
        "data": {
            "vehicle_type_counts": analytics_service.get_vehicle_type_counts(db),
            "vehicle_model_counts": analytics_service.get_vehicle_model_counts(db),
            "person_type_counts": analytics_service.get_person_type_counts(db)
        }
    }


@router.get("/analytics/recent")
def get_recent_detection_sessions(db: Session = Depends(get_db)):
    data = analytics_service.get_recent_sessions(db)

    return {
        "success": True,
        "message": "Recent detection sessions fetched successfully.",
        "data": data
    }