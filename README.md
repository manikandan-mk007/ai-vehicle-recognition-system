# AI-Based Vehicle, Number Plate and Person Recognition System

An end-to-end Machine Learning and Deep Learning project for detecting vehicles, recognizing number plates, classifying vehicle models, classifying person types, processing videos, monitoring live webcam streams, storing detection history, generating analytics, and exporting PDF reports.

This project supports image upload, video upload, and live webcam detection using a FastAPI backend and React frontend.

---

## Project Overview

The **AI-Based Vehicle, Number Plate and Person Recognition System** is designed for intelligent traffic monitoring, surveillance analytics, parking management, and smart transport applications.

The system can detect vehicles and persons from images, videos, and live webcam streams. It also detects number plates, reads plate text using OCR, classifies vehicle model names, classifies person types, stores detection history, shows dashboard analytics, and generates downloadable PDF reports.

---

## Key Features

### Image Detection

- Upload vehicle/person images
- Detect vehicles
- Detect persons
- Detect number plates
- Read number plate text
- Classify vehicle model name
- Classify person type
- Save detection result in database
- View annotated output image

### Video Detection

- Upload traffic videos
- Process frames using OpenCV
- Detect and track vehicles/persons
- Assign tracking IDs
- Export processed video
- Optional number plate OCR
- Save video session in history
- Show processed video preview

### Live Webcam Monitoring

- Access browser webcam
- Send frames to backend using WebSocket
- Detect vehicles/persons in real time
- Optional plate OCR
- Show processed AI output frame
- Save photo logs
- Record processed webcam output video
- Save recorded live detection as `webcam_video`

### Classification

- Vehicle model classification
- Person type classification
- Supports expandable class sets
- Easy model replacement through `trained_models/`

### Dashboard and Analytics

- Total detection sessions
- Total vehicles
- Total persons
- Total number plates
- Readable plate count
- Vehicle type chart
- Vehicle model chart
- Person type chart
- Recent detection sessions

### Detection History

- View all image/video/webcam sessions
- Preview output image/video
- View session details
- Delete session
- Download PDF report

### PDF Report Generation

Each detection session can export a PDF report containing:

- Session summary
- Input type
- Detection counts
- Vehicle details
- Person details
- Number plate details
- Output image preview or video link
- Model confidence values

---

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL / SQLite
- OpenCV
- Ultralytics YOLO
- EasyOCR
- PyTorch
- TorchVision
- ReportLab
- WebSocket

### Frontend

- React
- Vite
- Axios
- React Router
- Recharts
- Lucide React
- Tailwind CSS

### Machine Learning / Deep Learning

- YOLO object detection
- YOLO tracking with ByteTrack
- CNN-based vehicle model classification
- CNN-based person type classification
- OCR-based number plate text recognition

### Deployment

- Backend: Render
- Database: Render PostgreSQL
- Frontend: Vercel

---

## System Architecture

```text
User
│
├── Image Upload
├── Video Upload
└── Live Webcam
    │
    ▼
React Frontend
│
├── REST API requests
└── WebSocket live frames
    │
    ▼
FastAPI Backend
│
├── Vehicle Detection Model
├── Number Plate Detection Model
├── Vehicle Model Classifier
├── Person Type Classifier
├── OCR Service
├── Video Processing Service
├── Live Webcam Service
├── History Service
├── Analytics Service
└── PDF Report Service
    │
    ▼
Database
│
├── Detection Sessions
├── Vehicle Detections
├── Person Detections
└── Plate Detections
```

---

## Model Files

Keep all trained model files inside:

```text
backend/trained_models/
```

Required model files:

```text
backend/trained_models/
├── vehicle_detector.pt
├── plate_detector.pt
├── vehicle_model_classifier.pth
├── vehicle_model_classes.json
├── person_type_classifier.pth
└── person_type_classes.json
```

### Model Purpose

| File | Purpose |
|---|---|
| `vehicle_detector.pt` | Detects vehicle/person objects |
| `plate_detector.pt` | Detects number plate location |
| `vehicle_model_classifier.pth` | Predicts vehicle model name |
| `vehicle_model_classes.json` | Stores vehicle model class names |
| `person_type_classifier.pth` | Predicts person type |
| `person_type_classes.json` | Stores person type class names |

---

## Supported Classes

### Vehicle Detection Classes

```text
bicycle
bus
car
motorcycle
truck
```

### Vehicle Model Classification

Example classes:

```text
Hyundai i20
Mahindra Verito
Maruti Swift
Tata Nexon
Toyota Innova
```

The class list depends on `vehicle_model_classes.json`.

### Person Type Classification

```text
adult_male
adult_female
young_boy
young_girl
elderly_male
elderly_female
```

The class list depends on `person_type_classes.json`.

### Number Plate Detection

```text
number_plate
licence
license_plate
```

The label name depends on the trained plate model.

---

## Final Folder Structure

```text
ai-vehicle-recognition-system/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── db_models.py
│   │   │   └── schemas.py
│   │   ├── api/
│   │   │   ├── image_routes.py
│   │   │   ├── video_routes.py
│   │   │   ├── live_routes.py
│   │   │   ├── history_routes.py
│   │   │   └── analytics_routes.py
│   │   ├── services/
│   │   │   ├── detection_service.py
│   │   │   ├── plate_ocr_service.py
│   │   │   ├── vehicle_classifier_service.py
│   │   │   ├── person_classifier_service.py
│   │   │   ├── video_service.py
│   │   │   ├── live_service.py
│   │   │   ├── history_service.py
│   │   │   ├── analytics_service.py
│   │   │   └── report_service.py
│   │   ├── utils/
│   │   │   ├── image_utils.py
│   │   │   ├── video_utils.py
│   │   │   └── bbox_utils.py
│   │   └── storage/
│   │       ├── uploads/
│   │       ├── outputs/
│   │       ├── crops/
│   │       └── reports/
│   ├── trained_models/
│   │   ├── plate_detector.pt
│   │   ├── vehicle_detector.pt
│   │   ├── vehicle_model_classifier.pth
│   │   ├── vehicle_model_classes.json
│   │   ├── person_type_classifier.pth
│   │   └── person_type_classes.json
│   ├── requirements.txt
│   ├── run.py
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── axiosInstance.js
│   │   ├── components/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── StatCard.jsx
│   │   │   └── ChartBox.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ImageDetection.jsx
│   │   │   ├── VideoDetection.jsx
│   │   │   ├── LiveMonitoring.jsx
│   │   │   ├── DetectionHistory.jsx
│   │   │   └── SessionDetails.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── .env
│
├── training/
│   ├── plate_detection_training.ipynb
│   ├── vehicle_detection_training.ipynb
│   ├── vehicle_model_classification.ipynb
│   └── person_type_classification.ipynb
│
├── datasets/
│   ├── number_plate/
│   ├── vehicle_detection/
│   ├── vehicle_model/
│   └── person_type/
│
├── report/
│   ├── project_report.docx
│   └── presentation.pptx
│
├── README.md
└── .gitignore
```

---

## Backend Setup

Go to backend folder:

```bash
cd backend
```

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment:

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run backend:

```bash
python run.py
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger API docs:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

## Frontend Setup

Go to frontend folder:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Run frontend:

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

## Backend Environment Variables

Create:

```text
backend/.env
```

Example for local development:

```env
PROJECT_NAME=AI Vehicle Recognition System
VERSION=1.0.0
API_PREFIX=/api
DATABASE_URL=sqlite:///./vehicle_detection.db
BACKEND_BASE_URL=http://127.0.0.1:8000
FRONTEND_URL=http://localhost:5173
CONFIDENCE_THRESHOLD=0.35
MAX_VIDEO_SECONDS=120
VIDEO_PROCESS_EVERY_N_FRAMES=1
VIDEO_OCR_EVERY_N_FRAMES=30
```

Example for Render deployment:

```env
PROJECT_NAME=AI Vehicle Recognition System
VERSION=1.0.0
API_PREFIX=/api
DATABASE_URL=postgresql://username:password@host:5432/database
BACKEND_BASE_URL=https://your-backend.onrender.com
FRONTEND_URL=https://your-frontend.vercel.app
CONFIDENCE_THRESHOLD=0.35
MAX_VIDEO_SECONDS=120
VIDEO_PROCESS_EVERY_N_FRAMES=1
VIDEO_OCR_EVERY_N_FRAMES=30
```

---

## Frontend Environment Variables

Create:

```text
frontend/.env
```

Example for local development:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
VITE_BACKEND_BASE_URL=http://127.0.0.1:8000
VITE_WS_BASE_URL=ws://127.0.0.1:8000
```

Example for Vercel deployment:

```env
VITE_API_BASE_URL=https://your-backend.onrender.com/api
VITE_BACKEND_BASE_URL=https://your-backend.onrender.com
VITE_WS_BASE_URL=wss://your-backend.onrender.com
```

---

## API Endpoints

| Feature | Endpoint |
|---|---|
| Root | `GET /` |
| Health Check | `GET /health` |
| Image Detection | `POST /api/analyze/image` |
| Plate-Only Detection | `POST /api/analyze/plate` |
| Video Detection | `POST /api/analyze/video?enable_plate_ocr=false` |
| Live Webcam WebSocket | `ws://127.0.0.1:8000/api/live/webcam` |
| Upload Webcam Recording | `POST /api/live/upload-recording` |
| Detection History | `GET /api/history` |
| Session Details | `GET /api/history/{session_id}` |
| Delete Session | `DELETE /api/history/{session_id}` |
| Download PDF Report | `GET /api/history/{session_id}/report` |
| Analytics Summary | `GET /api/analytics/summary` |
| Analytics Charts | `GET /api/analytics/charts` |
| Recent Sessions | `GET /api/analytics/recent` |

---

## Database Tables

### detection_sessions

Stores each image, video, webcam, or webcam video detection session.

| Column | Description |
|---|---|
| id | Session ID |
| input_type | image / video / webcam / webcam_video |
| input_file_url | Uploaded input file |
| output_file_url | Processed output file |
| total_detections | Total detected objects |
| total_vehicles | Total vehicles |
| total_persons | Total persons |
| total_number_plates | Total plates |
| created_at | Session creation time |

### vehicle_detections

Stores vehicle detections.

| Column | Description |
|---|---|
| label | Detected class |
| confidence | Detection confidence |
| vehicle_model | Predicted model name |
| vehicle_model_confidence | Model confidence |
| crop_url | Vehicle crop |
| x1, y1, x2, y2 | Bounding box |

### person_detections

Stores person detections.

| Column | Description |
|---|---|
| label | Detected class |
| confidence | Detection confidence |
| person_type | Predicted person type |
| person_type_confidence | Type confidence |
| crop_url | Person crop |
| x1, y1, x2, y2 | Bounding box |

### plate_detections

Stores number plate detections.

| Column | Description |
|---|---|
| label | Plate detector label |
| plate_text | OCR text |
| detection_confidence | Plate detection confidence |
| ocr_confidence | OCR confidence |
| crop_url | Plate crop |
| x1, y1, x2, y2 | Bounding box |

---

## Screenshots

Add screenshots inside:

```text
frontend/src/assets/screenshots/
```

Recommended screenshot names:

```text
dashboard.png
image-detection.png
video-detection.png
live-monitoring.png
detection-history.png
session-details.png
pdf-report.png
```

### Dashboard

![Dashboard](frontend/src/assets/screenshots/dashboard.png)

### Image Detection

![Image Detection](frontend/src/assets/screenshots/image-detection.png)

### Video Detection

![Video Detection](frontend/src/assets/screenshots/video-detection.png)

### Live Monitoring

![Live Monitoring](frontend/src/assets/screenshots/live-monitoring.png)

### Detection History

![Detection History](frontend/src/assets/screenshots/detection-history.png)

### Session Details

![Session Details](frontend/src/assets/screenshots/session-details.png)

### PDF Report

![PDF Report](frontend/src/assets/screenshots/pdf-report.png)

---

## Output Screenshots / Page Source Links

After deployment, replace these placeholders with your actual links.

| Page | Local URL | Production URL |
|---|---|---|
| Dashboard | `http://localhost:5173/` | `https://your-frontend.vercel.app/` |
| Image Detection | `http://localhost:5173/image-detection` | `https://your-frontend.vercel.app/image-detection` |
| Video Detection | `http://localhost:5173/video-detection` | `https://your-frontend.vercel.app/video-detection` |
| Live Monitoring | `http://localhost:5173/live-monitoring` | `https://your-frontend.vercel.app/live-monitoring` |
| Detection History | `http://localhost:5173/history` | `https://your-frontend.vercel.app/history` |
| Session Details | `http://localhost:5173/history/1` | `https://your-frontend.vercel.app/history/1` |
| Backend API Docs | `http://127.0.0.1:8000/docs` | `https://your-backend.onrender.com/docs` |
| Backend Health | `http://127.0.0.1:8000/health` | `https://your-backend.onrender.com/health` |

---

## Sample Output

### Image Detection Output

```json
{
  "success": true,
  "message": "Image detection completed successfully.",
  "total_vehicles": 2,
  "total_persons": 1,
  "total_number_plates": 1,
  "vehicles": [
    {
      "label": "car",
      "confidence": 0.93,
      "vehicle_model": "Hyundai i20",
      "vehicle_model_confidence": 0.59,
      "box": {
        "x1": 0,
        "y1": 82,
        "x2": 198,
        "y2": 245
      }
    }
  ],
  "number_plates": [
    {
      "label": "licence",
      "plate_text": "TN59AB1234",
      "detection_confidence": 0.88,
      "ocr_confidence": 0.76
    }
  ]
}
```

### Video Detection Output

```json
{
  "success": true,
  "message": "Video detection and tracking completed successfully.",
  "output_video_url": "http://127.0.0.1:8000/outputs/processed_video.mp4",
  "unique_vehicles": 26,
  "unique_persons": 0,
  "unique_tracked_objects": 26,
  "vehicle_type_counts": {
    "car": 240,
    "truck": 20
  },
  "plate_texts": []
}
```

### Live Webcam Video Output

```json
{
  "success": true,
  "message": "Live webcam recording saved successfully.",
  "session_id": 10,
  "input_type": "webcam_video",
  "output_video_url": "http://127.0.0.1:8000/outputs/webcam_recording.webm"
}
```

---

## Model Training Plan

### Number Plate Detection

- Model: YOLO
- Output file: `plate_detector.pt`
- Dataset format: YOLO format
- Classes: number plate / licence / license plate

### Vehicle Detection

- Model: YOLO
- Output file: `vehicle_detector.pt`
- Classes: car, motorcycle, bus, truck, bicycle, person

### Vehicle Model Classification

- Model: EfficientNet-B0 / ResNet / MobileNet
- Output files:
  - `vehicle_model_classifier.pth`
  - `vehicle_model_classes.json`

### Person Type Classification

- Model: EfficientNet-B0 / ResNet / MobileNet
- Output files:
  - `person_type_classifier.pth`
  - `person_type_classes.json`

---

## Dataset Sources

The following datasets can be used for training or improving the model.

### Number Plate Detection

- Roboflow Indian License Plate Detection dataset includes open-source license plate images and a pre-trained model/API.
- Hugging Face UniDataPro license plate detection dataset contains license plate images from 32+ countries and provides OCR/detection-related annotations.

Source links:

- https://universe.roboflow.com/license-plate-detection-khhkb/indian-license-plate-detection-6tmbr
- https://huggingface.co/datasets/UniDataPro/license-plate-detection

### Vehicle Detection

- UAVDT is a vehicle detection/tracking dataset with annotated images for classes such as car, truck, and bus.
- Roboflow Aerial Vehicles dataset provides a Roboflow-exportable version with classes including car, truck, bus, and van.

Source links:

- https://datasetninja.com/uavdt
- https://universe.roboflow.com/uavdt/aerial-vehicles-hjarh

### Vehicle Model Classification

- Stanford Cars dataset contains 16,185 images across 196 vehicle classes, with classes at make/model/year level.

Source link:

- https://www.kaggle.com/datasets/eduardo4jesus/stanford-cars-dataset

### Person Type Classification

Person type classification can be trained using manually labeled person crops or filtered public datasets. The current project supports the following target classes:

```text
adult_male
adult_female
young_boy
young_girl
elderly_male
elderly_female
```

For best accuracy, use balanced datasets with 300–500 images per class.

---

## Deployment

### Backend Deployment on Render

1. Create PostgreSQL database in Render.
2. Copy the Internal Database URL.
3. Create Render Web Service.
4. Set root directory:

```text
backend
```

5. Build command:

```bash
pip install -r requirements.txt
```

6. Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

7. Add Render environment variables:

```env
DATABASE_URL=your_render_postgresql_internal_url
BACKEND_BASE_URL=https://your-backend.onrender.com
FRONTEND_URL=https://your-frontend.vercel.app
CONFIDENCE_THRESHOLD=0.35
MAX_VIDEO_SECONDS=120
VIDEO_PROCESS_EVERY_N_FRAMES=1
VIDEO_OCR_EVERY_N_FRAMES=30
```

### Frontend Deployment on Vercel

1. Import GitHub repository in Vercel.
2. Select root directory:

```text
frontend
```

3. Build command:

```bash
npm run build
```

4. Output directory:

```text
dist
```

5. Add Vercel environment variables:

```env
VITE_API_BASE_URL=https://your-backend.onrender.com/api
VITE_BACKEND_BASE_URL=https://your-backend.onrender.com
VITE_WS_BASE_URL=wss://your-backend.onrender.com
```

---

## Important Deployment Notes

### File Storage

The backend saves files in:

```text
backend/app/storage/uploads/
backend/app/storage/outputs/
backend/app/storage/crops/
backend/app/storage/reports/
```

On free cloud deployments, local file storage may be temporary. For production, use:

```text
Cloudinary
AWS S3
Render Persistent Disk
Supabase Storage
```

### Model File Size

If trained model files are larger than GitHub’s normal file limit, use:

```text
Git LFS
Cloud storage download during build
External model hosting
```

### WebSocket

Local WebSocket:

```text
ws://127.0.0.1:8000/api/live/webcam
```

Production WebSocket:

```text
wss://your-backend.onrender.com/api/live/webcam
```

---

## GitHub Commands

```bash
git init
git add .
git commit -m "Initial commit - AI vehicle recognition system"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-vehicle-recognition-system.git
git push -u origin main
```

For later updates:

```bash
git add .
git commit -m "Update project features"
git push origin main
```

---

## Future Enhancements

- Add more vehicle classes
- Add more Indian car and bike models
- Add truck and bus type classification
- Add helmet detection
- Add traffic police/security worker classification
- Add cloud storage for outputs
- Add user authentication
- Add admin dashboard
- Add role-based access
- Add real-time alert system
- Add email report sharing
- Add CSV/Excel export
- Add mobile responsive live monitoring
- Add GPU deployment support

---

## Project Status

```text
Completed:
- Image detection
- Video detection
- Live webcam detection
- Number plate OCR
- Vehicle model classification
- Person type classification
- Detection history
- Dashboard analytics
- PDF report generation
- Webcam video recording
- PostgreSQL deployment support
```

---

## Author

**Thangamanikandan I**

- GitHub: `https://github.com/manikandan-mk007`
- LinkedIn: `https://www.linkedin.com/in/thangamanikandan-i-560b20396/`
- Portfolio: `https://portfolio-o5cw.onrender.com`

---

## License

This project is intended for academic, research, and demonstration purposes.

---

## Disclaimer

This system uses AI-based detection and classification models. Results may vary depending on camera quality, lighting, distance, occlusion, object angle, weather, video resolution, and dataset quality. Person type classification is only a coarse visual category prediction and must not be used for identity recognition or sensitive decision-making.
