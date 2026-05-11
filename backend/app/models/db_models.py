from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from app.database import Base


def indian_time_now():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)



class DetectionSession(Base):
    __tablename__ = "detection_sessions"

    id = Column(Integer, primary_key=True, index=True)

    input_type = Column(String, nullable=False)  # image / video / webcam
    input_file_url = Column(String, nullable=True)
    output_file_url = Column(String, nullable=True)

    total_detections = Column(Integer, default=0)
    total_vehicles = Column(Integer, default=0)
    total_persons = Column(Integer, default=0)
    total_number_plates = Column(Integer, default=0)

    created_at = Column(DateTime, default=indian_time_now)

    vehicles = relationship(
        "VehicleDetection",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    persons = relationship(
        "PersonDetection",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    plates = relationship(
        "PlateDetection",
        back_populates="session",
        cascade="all, delete-orphan"
    )


class VehicleDetection(Base):
    __tablename__ = "vehicle_detections"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("detection_sessions.id"))

    label = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)

    vehicle_model = Column(String, nullable=True)
    vehicle_model_confidence = Column(Float, nullable=True)

    crop_url = Column(String, nullable=True)

    x1 = Column(Integer)
    y1 = Column(Integer)
    x2 = Column(Integer)
    y2 = Column(Integer)

    created_at = Column(DateTime, default=indian_time_now)

    session = relationship("DetectionSession", back_populates="vehicles")


class PersonDetection(Base):
    __tablename__ = "person_detections"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("detection_sessions.id"))

    label = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)

    person_type = Column(String, nullable=True)
    person_type_confidence = Column(Float, nullable=True)

    crop_url = Column(String, nullable=True)

    x1 = Column(Integer)
    y1 = Column(Integer)
    x2 = Column(Integer)
    y2 = Column(Integer)

    created_at = Column(DateTime, default=indian_time_now)

    session = relationship("DetectionSession", back_populates="persons")


class PlateDetection(Base):
    __tablename__ = "plate_detections"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("detection_sessions.id"))

    label = Column(String, nullable=False)
    plate_text = Column(String, nullable=True)

    detection_confidence = Column(Float, nullable=False)
    ocr_confidence = Column(Float, nullable=True)

    crop_url = Column(String, nullable=True)

    x1 = Column(Integer)
    y1 = Column(Integer)
    x2 = Column(Integer)
    y2 = Column(Integer)

    created_at = Column(DateTime, default=indian_time_now)

    session = relationship("DetectionSession", back_populates="plates")