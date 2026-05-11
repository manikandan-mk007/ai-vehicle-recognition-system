from sqlalchemy.orm import Session

from app.models.db_models import (
    DetectionSession,
    VehicleDetection,
    PersonDetection,
    PlateDetection
)


class HistoryService:
    def save_image_detection_result(
        self,
        db: Session,
        input_image_url: str,
        output_image_url: str,
        vehicles: list,
        persons: list,
        number_plates: list
    ):
        total_detections = len(vehicles) + len(persons) + len(number_plates)

        session = DetectionSession(
            input_type="image",
            input_file_url=input_image_url,
            output_file_url=output_image_url,
            total_detections=total_detections,
            total_vehicles=len(vehicles),
            total_persons=len(persons),
            total_number_plates=len(number_plates)
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        for vehicle in vehicles:
            box = vehicle["box"]

            db_vehicle = VehicleDetection(
                session_id=session.id,
                label=vehicle.get("label"),
                confidence=vehicle.get("confidence"),
                vehicle_model=vehicle.get("vehicle_model"),
                vehicle_model_confidence=vehicle.get("vehicle_model_confidence"),
                crop_url=vehicle.get("crop_url"),
                x1=box.get("x1"),
                y1=box.get("y1"),
                x2=box.get("x2"),
                y2=box.get("y2")
            )

            db.add(db_vehicle)

        for person in persons:
            box = person["box"]

            db_person = PersonDetection(
                session_id=session.id,
                label=person.get("label"),
                confidence=person.get("confidence"),
                person_type=person.get("person_type"),
                person_type_confidence=person.get("person_type_confidence"),
                crop_url=person.get("crop_url"),
                x1=box.get("x1"),
                y1=box.get("y1"),
                x2=box.get("x2"),
                y2=box.get("y2")
            )

            db.add(db_person)

        for plate in number_plates:
            box = plate["box"]

            db_plate = PlateDetection(
                session_id=session.id,
                label=plate.get("label"),
                plate_text=plate.get("plate_text"),
                detection_confidence=plate.get("detection_confidence"),
                ocr_confidence=plate.get("ocr_confidence"),
                crop_url=plate.get("crop_url"),
                x1=box.get("x1"),
                y1=box.get("y1"),
                x2=box.get("x2"),
                y2=box.get("y2")
            )

            db.add(db_plate)

        db.commit()

        return session
    
    def save_video_detection_result(
        self,
        db,
        input_video_url: str,
        output_video_url: str,
        result: dict
    ):
        session = DetectionSession(
            input_type="video",
            input_file_url=input_video_url,
            output_file_url=output_video_url,
            total_detections=result["total_vehicle_detections"]
            + result["total_person_detections"]
            + result["total_plate_detections"],
            total_vehicles=result["unique_vehicles"],
            total_persons=result["unique_persons"],
            total_number_plates=result["total_plate_detections"]
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session
    
    def save_webcam_video_result(
        self,
        db,
        output_video_url: str,
        total_vehicles: int = 0,
        total_persons: int = 0,
        total_number_plates: int = 0
    ):
        total_detections = total_vehicles + total_persons + total_number_plates

        session = DetectionSession(
            input_type="webcam_video",
            input_file_url=None,
            output_file_url=output_video_url,
            total_detections=total_detections,
            total_vehicles=total_vehicles,
            total_persons=total_persons,
            total_number_plates=total_number_plates
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session


history_service = HistoryService()