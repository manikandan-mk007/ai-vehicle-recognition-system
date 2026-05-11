from pathlib import Path
from ultralytics import YOLO

from app.config import settings
from app.utils.image_utils import (
    read_image,
    draw_box,
    save_output_image,
    crop_image,
    save_crop_image
)
from app.utils.bbox_utils import convert_xyxy_to_dict
from app.services.plate_ocr_service import plate_ocr_service
from app.services.vehicle_classifier_service import vehicle_classifier_service
from app.services.person_classifier_service import person_classifier_service


class DetectionService:
    def __init__(self):
        self.vehicle_detector = None
        self.load_vehicle_detector()

    def load_vehicle_detector(self):
        if not settings.VEHICLE_DETECTOR_PATH.exists():
            raise FileNotFoundError(
                f"vehicle_detector.pt not found at: {settings.VEHICLE_DETECTOR_PATH}"
            )

        self.vehicle_detector = YOLO(str(settings.VEHICLE_DETECTOR_PATH))

    def detect_vehicle_and_person(self, image, image_path: Path, base_url: str = ""):
        results = self.vehicle_detector.predict(
            source=str(image_path),
            conf=settings.CONFIDENCE_THRESHOLD,
            save=False,
            verbose=False
        )

        vehicles = []
        persons = []

        result = results[0]
        class_names = result.names

        for box in result.boxes:
            class_id = int(box.cls[0])
            label = class_names[class_id]
            confidence = float(box.conf[0])

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            bbox = convert_xyxy_to_dict([x1, y1, x2, y2])

            if label in settings.VEHICLE_CLASSES:
                vehicle_crop = crop_image(
                    image=image,
                    box=bbox,
                    padding=10
                )

                crop_url = None

                if vehicle_crop is not None and vehicle_crop.size != 0:
                    crop_path = save_crop_image(
                        crop=vehicle_crop,
                        prefix="vehicle"
                    )

                    if base_url:
                        crop_url = f"{base_url}/crops/{crop_path.name}"

                    classification_result = vehicle_classifier_service.predict_vehicle_model(
                        vehicle_crop
                    )
                else:
                    classification_result = {
                        "model_name": None,
                        "confidence": None
                    }

                detection = {
                    "label": label,
                    "confidence": round(confidence, 4),
                    "vehicle_model": classification_result["model_name"],
                    "vehicle_model_confidence": classification_result["confidence"],
                    "crop_url": crop_url,
                    "box": bbox
                }

                vehicles.append(detection)

                display_label = label

                if classification_result["model_name"]:
                    display_label = classification_result["model_name"]

                image = draw_box(
                    image=image,
                    box=bbox,
                    label=display_label,
                    confidence=confidence,
                    color=(0, 255, 0)
                )

            elif label == settings.PERSON_CLASS:
                person_crop = crop_image(
                    image=image,
                    box=bbox,
                    padding=10
                )

                crop_url = None

                if person_crop is not None and person_crop.size != 0:
                    crop_path = save_crop_image(
                        crop=person_crop,
                        prefix="person"
                    )

                    if base_url:
                        crop_url = f"{base_url}/crops/{crop_path.name}"

                    classification_result = person_classifier_service.predict_person_type(
                        person_crop
                    )
                else:
                    classification_result = {
                        "person_type": None,
                        "confidence": None
                    }

                detection = {
                    "label": label,
                    "confidence": round(confidence, 4),
                    "person_type": classification_result["person_type"],
                    "person_type_confidence": classification_result["confidence"],
                    "crop_url": crop_url,
                    "box": bbox
                }

                persons.append(detection)

                display_label = "person"

                if classification_result["person_type"]:
                    display_label = classification_result["person_type"]

                image = draw_box(
                    image=image,
                    box=bbox,
                    label=display_label,
                    confidence=confidence,
                    color=(255, 0, 0)
                )

        return image, vehicles, persons

    def detect_from_image(self, image_path: Path, base_url: str = ""):
        image = read_image(image_path)

        image, vehicles, persons = self.detect_vehicle_and_person(
            image=image,
            image_path=image_path,
            base_url=base_url
        )

        number_plates = plate_ocr_service.detect_and_read_plates(
            image=image,
            image_path=image_path,
            base_url=base_url
        )

        for plate in number_plates:
            label_text = "plate"

            if plate["plate_text"]:
                label_text = plate["plate_text"]

            image = draw_box(
                image=image,
                box=plate["box"],
                label=label_text,
                confidence=plate["detection_confidence"],
                color=(0, 255, 255)
            )

        output_path = save_output_image(image, image_path)

        return {
            "vehicles": vehicles,
            "persons": persons,
            "number_plates": number_plates,
            "output_path": output_path
        }


detection_service = DetectionService()