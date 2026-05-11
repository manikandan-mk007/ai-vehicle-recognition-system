import json
import cv2
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

from app.config import settings


class PersonClassifierService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.class_names = []
        self.model = None

        self.load_classes()
        self.load_model()

    def load_classes(self):
        if not settings.PERSON_TYPE_CLASSES_PATH.exists():
            print(f"Person type classes file not found: {settings.PERSON_TYPE_CLASSES_PATH}")
            self.class_names = []
            return

        with open(settings.PERSON_TYPE_CLASSES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            self.class_names = [data[str(i)] for i in range(len(data))]
        elif isinstance(data, list):
            self.class_names = data
        else:
            self.class_names = []

    def build_model(self, num_classes: int):
        model = models.efficientnet_b0(weights=None)

        in_features = model.classifier[1].in_features

        model.classifier[1] = nn.Linear(
            in_features,
            num_classes
        )

        return model

    def load_model(self):
        if not settings.PERSON_TYPE_CLASSIFIER_PATH.exists():
            print(f"Person classifier model not found: {settings.PERSON_TYPE_CLASSIFIER_PATH}")
            self.model = None
            return

        if len(self.class_names) == 0:
            print("Person class names not loaded. Classifier disabled.")
            self.model = None
            return

        self.model = self.build_model(num_classes=len(self.class_names))

        checkpoint = torch.load(
            settings.PERSON_TYPE_CLASSIFIER_PATH,
            map_location=self.device
        )

        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["model_state_dict"])
        else:
            self.model.load_state_dict(checkpoint)

        self.model.to(self.device)
        self.model.eval()

    def get_transform(self):
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def predict_person_type(self, person_crop):
        if self.model is None:
            return {
                "person_type": None,
                "confidence": None
            }

        if person_crop is None or person_crop.size == 0:
            return {
                "person_type": None,
                "confidence": None
            }

        try:
            rgb_image = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)

            transform = self.get_transform()
            input_tensor = transform(pil_image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                confidence, predicted_index = torch.max(probabilities, 1)

            predicted_index = int(predicted_index.item())
            confidence = float(confidence.item())

            person_type = self.class_names[predicted_index]

            return {
                "person_type": person_type,
                "confidence": round(confidence, 4)
            }

        except Exception as e:
            print(f"Person classification error: {str(e)}")

            return {
                "person_type": None,
                "confidence": None
            }


person_classifier_service = PersonClassifierService()