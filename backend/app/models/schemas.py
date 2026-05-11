from pydantic import BaseModel
from typing import List, Optional


class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class VehicleDetectionItem(BaseModel):
    label: str
    confidence: float
    vehicle_model: Optional[str] = None
    vehicle_model_confidence: Optional[float] = None
    crop_url: Optional[str] = None
    box: BoundingBox


class PersonDetectionItem(BaseModel):
    label: str
    confidence: float
    person_type: Optional[str] = None
    person_type_confidence: Optional[float] = None
    crop_url: Optional[str] = None
    box: BoundingBox


class PlateDetectionItem(BaseModel):
    label: str
    plate_text: Optional[str] = None
    detection_confidence: float
    ocr_confidence: Optional[float] = None
    crop_url: Optional[str] = None
    box: BoundingBox


class ImageDetectionResponse(BaseModel):
    success: bool
    message: str
    input_image_url: str
    output_image_url: str
    total_detections: int
    total_vehicles: int
    total_persons: int
    total_number_plates: int
    vehicles: List[VehicleDetectionItem]
    persons: List[PersonDetectionItem]
    number_plates: List[PlateDetectionItem]


class ErrorResponse(BaseModel):
    success: bool
    message: str