from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.db_models import (
    DetectionSession,
    VehicleDetection,
    PersonDetection,
    PlateDetection
)


class AnalyticsService:
    def get_summary(self, db: Session):
        total_sessions = db.query(DetectionSession).count()
        total_vehicles = db.query(VehicleDetection).count()
        total_persons = db.query(PersonDetection).count()
        total_plates = db.query(PlateDetection).count()

        readable_plates = (
            db.query(PlateDetection)
            .filter(PlateDetection.plate_text != None)
            .filter(PlateDetection.plate_text != "")
            .count()
        )

        return {
            "total_sessions": total_sessions,
            "total_vehicles": total_vehicles,
            "total_persons": total_persons,
            "total_plates": total_plates,
            "readable_plates": readable_plates
        }

    def get_vehicle_type_counts(self, db: Session):
        result = (
            db.query(
                VehicleDetection.label,
                func.count(VehicleDetection.id)
            )
            .group_by(VehicleDetection.label)
            .all()
        )

        return [
            {
                "label": label,
                "count": count
            }
            for label, count in result
        ]

    def get_vehicle_model_counts(self, db: Session):
        result = (
            db.query(
                VehicleDetection.vehicle_model,
                func.count(VehicleDetection.id)
            )
            .filter(VehicleDetection.vehicle_model != None)
            .filter(VehicleDetection.vehicle_model != "")
            .group_by(VehicleDetection.vehicle_model)
            .all()
        )

        return [
            {
                "model": model,
                "count": count
            }
            for model, count in result
        ]

    def get_person_type_counts(self, db: Session):
        result = (
            db.query(
                PersonDetection.person_type,
                func.count(PersonDetection.id)
            )
            .filter(PersonDetection.person_type != None)
            .filter(PersonDetection.person_type != "")
            .group_by(PersonDetection.person_type)
            .all()
        )

        return [
            {
                "type": person_type,
                "count": count
            }
            for person_type, count in result
        ]

    def get_recent_sessions(self, db: Session, limit: int = 5):
        sessions = (
            db.query(DetectionSession)
            .order_by(DetectionSession.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
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
            for session in sessions
        ]


analytics_service = AnalyticsService()