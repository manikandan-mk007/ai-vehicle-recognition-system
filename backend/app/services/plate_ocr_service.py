from pathlib import Path
import re
import cv2
import easyocr
from ultralytics import YOLO

from app.config import settings
from app.utils.bbox_utils import convert_xyxy_to_dict
from app.utils.image_utils import crop_image, save_crop_image


class PlateOCRService:
    def __init__(self):
        self.plate_detector = None
        self.ocr_reader = None

        self.load_plate_detector()
        self.load_ocr_reader()

    def load_plate_detector(self):
        if not settings.PLATE_DETECTOR_PATH.exists():
            raise FileNotFoundError(
                f"plate_detector.pt not found at: {settings.PLATE_DETECTOR_PATH}"
            )

        self.plate_detector = YOLO(str(settings.PLATE_DETECTOR_PATH))

    def load_ocr_reader(self):
        self.ocr_reader = easyocr.Reader(
            ["en"],
            gpu=False
        )

    def clean_plate_text(self, text: str) -> str:
        if not text:
            return ""

        text = text.upper()
        text = re.sub(r"[^A-Z0-9]", "", text)

        return text

    def preprocess_plate_for_ocr(self, plate_crop):
        gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)

        gray = cv2.resize(
            gray,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC
        )

        gray = cv2.bilateralFilter(gray, 11, 17, 17)

        return gray

    def read_plate_text(self, plate_crop):
        processed_crop = self.preprocess_plate_for_ocr(plate_crop)

        ocr_results = self.ocr_reader.readtext(processed_crop)

        if not ocr_results:
            return {
                "plate_text": "",
                "ocr_confidence": 0.0
            }

        best_text = ""
        best_confidence = 0.0

        for result in ocr_results:
            text = result[1]
            confidence = float(result[2])

            cleaned_text = self.clean_plate_text(text)

            if confidence > best_confidence and len(cleaned_text) >= 4:
                best_text = cleaned_text
                best_confidence = confidence

        return {
            "plate_text": best_text,
            "ocr_confidence": round(best_confidence, 4)
        }

    def detect_and_read_plates(self, image, image_path: Path, base_url: str = ""):
        results = self.plate_detector.predict(
            source=str(image_path),
            conf=settings.CONFIDENCE_THRESHOLD,
            save=False,
            verbose=False
        )

        detected_plates = []

        result = results[0]
        class_names = result.names

        for box in result.boxes:
            class_id = int(box.cls[0])
            label = class_names[class_id]
            detection_confidence = float(box.conf[0])

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            bbox = convert_xyxy_to_dict([x1, y1, x2, y2])

            plate_crop = crop_image(
                image=image,
                box=bbox,
                padding=8
            )

            if plate_crop is None or plate_crop.size == 0:
                continue

            crop_path = save_crop_image(
                crop=plate_crop,
                prefix="plate"
            )

            ocr_result = self.read_plate_text(plate_crop)

            crop_url = None

            if base_url:
                crop_url = f"{base_url}/crops/{crop_path.name}"

            detected_plates.append(
                {
                    "label": label,
                    "plate_text": ocr_result["plate_text"],
                    "detection_confidence": round(detection_confidence, 4),
                    "ocr_confidence": ocr_result["ocr_confidence"],
                    "crop_url": crop_url,
                    "box": bbox
                }
            )

        return detected_plates


plate_ocr_service = PlateOCRService()