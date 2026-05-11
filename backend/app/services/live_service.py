import base64
import uuid

import cv2
import numpy as np
from ultralytics import YOLO

from app.config import settings
from app.database import SessionLocal
from app.models.db_models import (
    DetectionSession,
    VehicleDetection,
    PersonDetection,
    PlateDetection
)
from app.utils.bbox_utils import convert_xyxy_to_dict
from app.utils.image_utils import draw_box, save_crop_image, crop_image
from app.services.plate_ocr_service import plate_ocr_service
from app.services.vehicle_classifier_service import vehicle_classifier_service
from app.services.person_classifier_service import person_classifier_service


class LiveService:
    def __init__(self):
        self.vehicle_detector = None
        self.load_vehicle_detector()

    def load_vehicle_detector(self):
        if not settings.VEHICLE_DETECTOR_PATH.exists():
            raise FileNotFoundError(
                f"vehicle_detector.pt not found at: {settings.VEHICLE_DETECTOR_PATH}"
            )

        self.vehicle_detector = YOLO(str(settings.VEHICLE_DETECTOR_PATH))

    def decode_base64_image(self, image_data: str):
        if "," in image_data:
            image_data = image_data.split(",")[1]

        image_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)

        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            raise ValueError("Invalid webcam frame received.")

        return frame

    def encode_frame_to_base64(self, frame):
        success, buffer = cv2.imencode(".jpg", frame)

        if not success:
            raise ValueError("Unable to encode processed frame.")

        encoded = base64.b64encode(buffer).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded}"

    def save_live_snapshot(self, frame):
        settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        filename = f"live_{uuid.uuid4().hex}.jpg"
        output_path = settings.OUTPUT_DIR / filename

        cv2.imwrite(str(output_path), frame)

        return output_path

    def save_live_log(
        self,
        output_file_url: str,
        vehicles: list,
        persons: list,
        number_plates: list
    ):
        db = SessionLocal()

        try:
            session = DetectionSession(
                input_type="webcam",
                input_file_url=None,
                output_file_url=output_file_url,
                total_detections=len(vehicles) + len(persons) + len(number_plates),
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

            return session.id

        finally:
            db.close()

    def process_frame(
        self,
        image_data: str,
        base_url: str = "",
        enable_plate_ocr: bool = False,
        save_logs: bool = False
    ):
        frame = self.decode_base64_image(image_data)

        frame_height, frame_width = frame.shape[:2]

        results = self.vehicle_detector.predict(
            source=frame,
            conf=settings.CONFIDENCE_THRESHOLD,
            save=False,
            verbose=False
        )

        vehicles = []
        persons = []
        number_plates = []

        result = results[0]
        class_names = result.names

        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = class_names[class_id]
                confidence = float(box.conf[0])

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                bbox = convert_xyxy_to_dict([x1, y1, x2, y2])

                if label in settings.VEHICLE_CLASSES:
                    vehicle_crop = crop_image(
                        image=frame,
                        box=bbox,
                        padding=10
                    )

                    vehicle_model = None
                    vehicle_model_confidence = None
                    crop_url = None

                    if vehicle_crop is not None and vehicle_crop.size != 0:
                        crop_path = save_crop_image(
                            crop=vehicle_crop,
                            prefix="live_vehicle"
                        )

                        if base_url:
                            crop_url = f"{base_url}/crops/{crop_path.name}"

                        model_result = vehicle_classifier_service.predict_vehicle_model(
                            vehicle_crop
                        )

                        vehicle_model = model_result["model_name"]
                        vehicle_model_confidence = model_result["confidence"]

                    vehicle_data = {
                        "label": label,
                        "confidence": round(confidence, 4),
                        "vehicle_model": vehicle_model,
                        "vehicle_model_confidence": vehicle_model_confidence,
                        "crop_url": crop_url,
                        "box": bbox
                    }

                    vehicles.append(vehicle_data)

                    display_label = vehicle_model if vehicle_model else label

                    frame = draw_box(
                        image=frame,
                        box=bbox,
                        label=display_label,
                        confidence=confidence,
                        color=(0, 255, 0)
                    )

                elif label == settings.PERSON_CLASS:
                    person_crop = crop_image(
                        image=frame,
                        box=bbox,
                        padding=10
                    )

                    person_type = None
                    person_type_confidence = None
                    crop_url = None

                    if person_crop is not None and person_crop.size != 0:
                        crop_path = save_crop_image(
                            crop=person_crop,
                            prefix="live_person"
                        )

                        if base_url:
                            crop_url = f"{base_url}/crops/{crop_path.name}"

                        person_result = person_classifier_service.predict_person_type(
                            person_crop
                        )

                        person_type = person_result["person_type"]
                        person_type_confidence = person_result["confidence"]

                    person_data = {
                        "label": label,
                        "confidence": round(confidence, 4),
                        "person_type": person_type,
                        "person_type_confidence": person_type_confidence,
                        "crop_url": crop_url,
                        "box": bbox
                    }

                    persons.append(person_data)

                    display_label = person_type if person_type else "person"

                    frame = draw_box(
                        image=frame,
                        box=bbox,
                        label=display_label,
                        confidence=confidence,
                        color=(255, 0, 0)
                    )

        if enable_plate_ocr:
            temp_frame_path = settings.CROP_DIR / f"live_temp_{uuid.uuid4().hex}.jpg"
            cv2.imwrite(str(temp_frame_path), frame)

            plates = plate_ocr_service.detect_and_read_plates(
                image=frame,
                image_path=temp_frame_path,
                base_url=base_url
            )

            for plate in plates:
                number_plates.append(plate)

                plate_label = plate.get("plate_text") or "plate"

                frame = draw_box(
                    image=frame,
                    box=plate["box"],
                    label=plate_label,
                    confidence=plate["detection_confidence"],
                    color=(0, 255, 255)
                )

        output_file_url = None
        saved_session_id = None

        if save_logs and (vehicles or persons or number_plates):
            output_path = self.save_live_snapshot(frame)

            if base_url:
                output_file_url = f"{base_url}/outputs/{output_path.name}"

            saved_session_id = self.save_live_log(
                output_file_url=output_file_url,
                vehicles=vehicles,
                persons=persons,
                number_plates=number_plates
            )

        processed_frame = self.encode_frame_to_base64(frame)

        return {
            "success": True,
            "frame_width": frame_width,
            "frame_height": frame_height,
            "processed_frame": processed_frame,
            "saved_session_id": saved_session_id,
            "total_detections": len(vehicles) + len(persons) + len(number_plates),
            "total_vehicles": len(vehicles),
            "total_persons": len(persons),
            "total_number_plates": len(number_plates),
            "vehicles": vehicles,
            "persons": persons,
            "number_plates": number_plates
        }


live_service = LiveService()