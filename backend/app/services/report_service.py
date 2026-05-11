from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)

from app.config import settings
from app.models.db_models import (
    DetectionSession,
    VehicleDetection,
    PersonDetection,
    PlateDetection
)


class ReportService:
    def __init__(self):
        settings.REPORT_DIR.mkdir(parents=True, exist_ok=True)

    def safe_text(self, value):
        if value is None or value == "":
            return "N/A"

        return str(value)

    def confidence_text(self, value):
        if value is None:
            return "N/A"

        try:
            return f"{float(value):.2f}"
        except Exception:
            return "N/A"

    def url_to_local_path(self, url: str):
        if not url:
            return None

        try:
            if "/outputs/" in url:
                filename = url.split("/outputs/")[-1]
                return settings.OUTPUT_DIR / filename

            if "/uploads/" in url:
                filename = url.split("/uploads/")[-1]
                return settings.UPLOAD_DIR / filename

            if "/crops/" in url:
                filename = url.split("/crops/")[-1]
                return settings.CROP_DIR / filename

        except Exception:
            return None

        return None

    def create_title_style(self, styles):
        return ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=16
        )

    def create_heading_style(self, styles):
        return ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1E293B"),
            spaceBefore=14,
            spaceAfter=10
        )

    def create_body_style(self, styles):
        return ParagraphStyle(
            "CustomBody",
            parent=styles["BodyText"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155")
        )

    def build_summary_table(self, session: DetectionSession):
        data = [
            ["Field", "Value"],
            ["Session ID", f"#{session.id}"],
            ["Input Type", self.safe_text(session.input_type).capitalize()],
            ["Created At", session.created_at.strftime("%d-%m-%Y %I:%M:%S %p")],
            ["Total Detections", self.safe_text(session.total_detections)],
            ["Total Vehicles", self.safe_text(session.total_vehicles)],
            ["Total Persons", self.safe_text(session.total_persons)],
            ["Total Number Plates", self.safe_text(session.total_number_plates)],
            ["Input File URL", self.safe_text(session.input_file_url)],
            ["Output File URL", self.safe_text(session.output_file_url)],
        ]

        table = Table(data, colWidths=[2.0 * inch, 4.7 * inch])

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        return table

    def build_vehicle_table(self, vehicles):
        data = [
            ["#", "Label", "Confidence", "Model", "Model Conf", "Box"]
        ]

        for index, item in enumerate(vehicles, start=1):
            box = f"({item.x1}, {item.y1}) - ({item.x2}, {item.y2})"

            data.append(
                [
                    index,
                    self.safe_text(item.label),
                    self.confidence_text(item.confidence),
                    self.safe_text(item.vehicle_model),
                    self.confidence_text(item.vehicle_model_confidence),
                    box
                ]
            )

        table = Table(
            data,
            colWidths=[
                0.35 * inch,
                0.85 * inch,
                0.8 * inch,
                1.45 * inch,
                0.9 * inch,
                2.1 * inch
            ]
        )

        table.setStyle(self.default_table_style())

        return table

    def build_person_table(self, persons):
        data = [
            ["#", "Label", "Confidence", "Person Type", "Type Conf", "Box"]
        ]

        for index, item in enumerate(persons, start=1):
            box = f"({item.x1}, {item.y1}) - ({item.x2}, {item.y2})"

            data.append(
                [
                    index,
                    self.safe_text(item.label),
                    self.confidence_text(item.confidence),
                    self.safe_text(item.person_type),
                    self.confidence_text(item.person_type_confidence),
                    box
                ]
            )

        table = Table(
            data,
            colWidths=[
                0.35 * inch,
                0.85 * inch,
                0.8 * inch,
                1.45 * inch,
                0.9 * inch,
                2.1 * inch
            ]
        )

        table.setStyle(self.default_table_style())

        return table

    def build_plate_table(self, plates):
        data = [
            ["#", "Label", "Plate Text", "Detect Conf", "OCR Conf", "Box"]
        ]

        for index, item in enumerate(plates, start=1):
            box = f"({item.x1}, {item.y1}) - ({item.x2}, {item.y2})"

            data.append(
                [
                    index,
                    self.safe_text(item.label),
                    self.safe_text(item.plate_text),
                    self.confidence_text(item.detection_confidence),
                    self.confidence_text(item.ocr_confidence),
                    box
                ]
            )

        table = Table(
            data,
            colWidths=[
                0.35 * inch,
                0.85 * inch,
                1.25 * inch,
                0.9 * inch,
                0.8 * inch,
                2.1 * inch
            ]
        )

        table.setStyle(self.default_table_style())

        return table

    def default_table_style(self):
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )

    def add_output_preview(self, story, session, heading_style, body_style):
        if not session.output_file_url:
            story.append(Paragraph("No output preview available.", body_style))
            return

        if session.input_type == "video":
            story.append(
                Paragraph(
                    "Video output cannot be embedded directly in this PDF. Use the output file URL below:",
                    body_style
                )
            )
            story.append(Spacer(1, 6))
            story.append(Paragraph(self.safe_text(session.output_file_url), body_style))
            return

        local_path = self.url_to_local_path(session.output_file_url)

        if local_path and local_path.exists():
            try:
                img = Image(str(local_path))

                max_width = 6.3 * inch
                max_height = 3.8 * inch

                img_width = img.imageWidth
                img_height = img.imageHeight

                ratio = min(max_width / img_width, max_height / img_height)

                img.drawWidth = img_width * ratio
                img.drawHeight = img_height * ratio

                story.append(img)

            except Exception:
                story.append(
                    Paragraph(
                        "Output preview image could not be added.",
                        body_style
                    )
                )
        else:
            story.append(
                Paragraph(
                    "Output preview file not found locally.",
                    body_style
                )
            )

    def generate_session_report(
        self,
        session: DetectionSession,
        vehicles: list[VehicleDetection],
        persons: list[PersonDetection],
        plates: list[PlateDetection]
    ):
        filename = f"detection_report_session_{session.id}.pdf"
        report_path = settings.REPORT_DIR / filename

        doc = SimpleDocTemplate(
            str(report_path),
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = self.create_title_style(styles)
        heading_style = self.create_heading_style(styles)
        body_style = self.create_body_style(styles)

        story = []

        story.append(Paragraph("AI Vehicle Recognition Detection Report", title_style))
        story.append(
            Paragraph(
                f"Generated on {datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')}",
                body_style
            )
        )
        story.append(Spacer(1, 14))

        story.append(Paragraph("1. Session Summary", heading_style))
        story.append(self.build_summary_table(session))
        story.append(Spacer(1, 14))

        story.append(Paragraph("2. Output Preview", heading_style))
        self.add_output_preview(story, session, heading_style, body_style)
        story.append(Spacer(1, 14))

        story.append(Paragraph("3. Vehicle Detections", heading_style))
        if vehicles:
            story.append(self.build_vehicle_table(vehicles))
        else:
            story.append(Paragraph("No vehicle detections found.", body_style))
        story.append(Spacer(1, 14))

        story.append(Paragraph("4. Person Detections", heading_style))
        if persons:
            story.append(self.build_person_table(persons))
        else:
            story.append(Paragraph("No person detections found.", body_style))
        story.append(Spacer(1, 14))

        story.append(Paragraph("5. Number Plate Detections", heading_style))
        if plates:
            story.append(self.build_plate_table(plates))
        else:
            story.append(Paragraph("No number plate detections found.", body_style))
        story.append(Spacer(1, 14))

        story.append(Paragraph("6. Notes", heading_style))
        story.append(
            Paragraph(
                "This report was generated automatically by the AI Vehicle Recognition System. "
                "Detection and classification results depend on model accuracy, image clarity, "
                "camera angle, lighting conditions, object distance and video quality.",
                body_style
            )
        )

        doc.build(story)

        return report_path


report_service = ReportService()