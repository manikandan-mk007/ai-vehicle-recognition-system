from pathlib import Path
import cv2
from ultralytics import YOLO

from app.config import settings
from app.utils.video_utils import (
    get_video_info,
    create_video_writer,
    get_raw_output_video_path,
    get_final_output_video_path,
    convert_to_browser_mp4
)
from app.utils.bbox_utils import convert_xyxy_to_dict
from app.utils.image_utils import draw_box, crop_image
from app.services.plate_ocr_service import plate_ocr_service
from app.services.vehicle_classifier_service import vehicle_classifier_service
from app.services.person_classifier_service import person_classifier_service


class VideoService:
    def __init__(self):
        self.vehicle_detector = None
        self.load_vehicle_detector()

    def load_vehicle_detector(self):
        if not settings.VEHICLE_DETECTOR_PATH.exists():
            raise FileNotFoundError(
                f"vehicle_detector.pt not found at: {settings.VEHICLE_DETECTOR_PATH}"
            )

        self.vehicle_detector = YOLO(str(settings.VEHICLE_DETECTOR_PATH))

    def process_video(
        self,
        video_path: Path,
        base_url: str = "",
        enable_plate_ocr: bool = False
    ):
        video_info = get_video_info(video_path)

        if video_info["duration_seconds"] > settings.MAX_VIDEO_SECONDS:
            raise ValueError(
                f"Video is too long. Maximum allowed duration is {settings.MAX_VIDEO_SECONDS} seconds."
            )

        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise ValueError("Unable to open video file.")

        raw_output_path = get_raw_output_video_path(video_path)
        final_output_path = get_final_output_video_path(video_path)

        writer = create_video_writer(
            output_path=raw_output_path,
            fps=video_info["fps"],
            width=video_info["width"],
            height=video_info["height"]
        )

        frame_index = 0

        total_vehicle_detections = 0
        total_person_detections = 0
        total_plate_detections = 0

        unique_track_ids = set()
        vehicle_track_ids = set()
        person_track_ids = set()

        detected_vehicle_types = {}
        detected_vehicle_models = {}
        detected_person_types = {}
        detected_plate_texts = []

        # Cache classification per track_id.
        # This avoids classifying the same vehicle/person again and again every frame.
        vehicle_model_cache = {}
        person_type_cache = {}

        try:
            while True:
                success, frame = cap.read()

                if not success:
                    break

                frame_index += 1

                if frame_index % settings.VIDEO_PROCESS_EVERY_N_FRAMES != 0:
                    writer.write(frame)
                    continue

                results = self.vehicle_detector.track(
                    source=frame,
                    conf=settings.CONFIDENCE_THRESHOLD,
                    persist=True,
                    verbose=False,
                    tracker="bytetrack.yaml"
                )

                result = results[0]
                class_names = result.names

                if result.boxes is not None:
                    for box in result.boxes:
                        class_id = int(box.cls[0])
                        label = class_names[class_id]
                        confidence = float(box.conf[0])

                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        bbox = convert_xyxy_to_dict([x1, y1, x2, y2])

                        track_id = None

                        if box.id is not None:
                            track_id = int(box.id[0])
                            unique_track_ids.add(track_id)

                        if label in settings.VEHICLE_CLASSES:
                            total_vehicle_detections += 1
                            detected_vehicle_types[label] = detected_vehicle_types.get(label, 0) + 1

                            if track_id is not None:
                                vehicle_track_ids.add(track_id)

                            vehicle_model = None
                            vehicle_model_confidence = None

                            # Classify vehicle model only sometimes for speed.
                            # If same track_id already classified, reuse it.
                            if track_id is not None and track_id in vehicle_model_cache:
                                cached = vehicle_model_cache[track_id]
                                vehicle_model = cached["vehicle_model"]
                                vehicle_model_confidence = cached["vehicle_model_confidence"]
                            else:
                                vehicle_crop = crop_image(
                                    image=frame,
                                    box=bbox,
                                    padding=10
                                )

                                if vehicle_crop is not None and vehicle_crop.size != 0:
                                    model_result = vehicle_classifier_service.predict_vehicle_model(
                                        vehicle_crop
                                    )

                                    vehicle_model = model_result["model_name"]
                                    vehicle_model_confidence = model_result["confidence"]

                                    if track_id is not None:
                                        vehicle_model_cache[track_id] = {
                                            "vehicle_model": vehicle_model,
                                            "vehicle_model_confidence": vehicle_model_confidence
                                        }

                            if vehicle_model:
                                detected_vehicle_models[vehicle_model] = (
                                    detected_vehicle_models.get(vehicle_model, 0) + 1
                                )

                            display_label = label

                            if vehicle_model and vehicle_model_confidence is not None and vehicle_model_confidence >= 0.60:
                                display_label = f"{vehicle_model}"
                            elif track_id is not None:
                                display_label = f"{label} ID:{track_id}"

                            frame = draw_box(
                                image=frame,
                                box=bbox,
                                label=display_label,
                                confidence=confidence,
                                color=(0, 255, 0)
                            )

                        elif label == settings.PERSON_CLASS:
                            total_person_detections += 1

                            if track_id is not None:
                                person_track_ids.add(track_id)

                            person_type = None
                            person_type_confidence = None

                            if track_id is not None and track_id in person_type_cache:
                                cached = person_type_cache[track_id]
                                person_type = cached["person_type"]
                                person_type_confidence = cached["person_type_confidence"]
                            else:
                                person_crop = crop_image(
                                    image=frame,
                                    box=bbox,
                                    padding=10
                                )

                                if person_crop is not None and person_crop.size != 0:
                                    person_result = person_classifier_service.predict_person_type(
                                        person_crop
                                    )

                                    person_type = person_result["person_type"]
                                    person_type_confidence = person_result["confidence"]

                                    if track_id is not None:
                                        person_type_cache[track_id] = {
                                            "person_type": person_type,
                                            "person_type_confidence": person_type_confidence
                                        }

                            if person_type:
                                detected_person_types[person_type] = (
                                    detected_person_types.get(person_type, 0) + 1
                                )

                            display_label = "person"

                            if person_type:
                                display_label = person_type
                            elif track_id is not None:
                                display_label = f"person ID:{track_id}"

                            frame = draw_box(
                                image=frame,
                                box=bbox,
                                label=display_label,
                                confidence=confidence,
                                color=(255, 0, 0)
                            )

                if enable_plate_ocr and frame_index % settings.VIDEO_OCR_EVERY_N_FRAMES == 0:
                    temp_frame_path = (
                        settings.CROP_DIR
                        / f"video_frame_{video_path.stem}_{frame_index}.jpg"
                    )

                    cv2.imwrite(str(temp_frame_path), frame)

                    plates = plate_ocr_service.detect_and_read_plates(
                        image=frame,
                        image_path=temp_frame_path,
                        base_url=base_url
                    )

                    for plate in plates:
                        total_plate_detections += 1

                        plate_text = plate.get("plate_text")

                        if plate_text:
                            detected_plate_texts.append(plate_text)

                        plate_label = plate_text if plate_text else "plate"

                        frame = draw_box(
                            image=frame,
                            box=plate["box"],
                            label=plate_label,
                            confidence=plate["detection_confidence"],
                            color=(0, 255, 255)
                        )

                writer.write(frame)

        finally:
            cap.release()
            writer.release()

        output_path = convert_to_browser_mp4(
            raw_video_path=raw_output_path,
            final_video_path=final_output_path
        )

        unique_plate_texts = list(set(detected_plate_texts))

        output_video_url = None

        if base_url:
            output_video_url = f"{base_url}/outputs/{output_path.name}"

        return {
            "input_video_path": str(video_path),
            "output_video_path": str(output_path),
            "output_video_url": output_video_url,
            "video_info": video_info,
            "total_frames_processed": frame_index,
            "total_vehicle_detections": total_vehicle_detections,
            "total_person_detections": total_person_detections,
            "total_plate_detections": total_plate_detections,
            "unique_tracked_objects": len(unique_track_ids),
            "unique_vehicles": len(vehicle_track_ids),
            "unique_persons": len(person_track_ids),
            "vehicle_type_counts": detected_vehicle_types,
            "vehicle_model_counts": detected_vehicle_models,
            "person_type_counts": detected_person_types,
            "plate_texts": unique_plate_texts
        }


video_service = VideoService()