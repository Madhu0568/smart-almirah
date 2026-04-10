# AI-Enabled Smart Almirah - Object Detection System

A real-time object detection system using YOLOv8 to automatically identify and catalog clothing items inside a smart wardrobe, achieving 88%+ detection accuracy at 15 FPS.

## Features

- **Real-time object detection** using YOLOv8 model for clothing identification
- **Dynamic inventory management** with automatic cataloging on detection events
- **RESTful inventory API** for item queries, filtering by category and color
- **Camera feed control** with start/stop and uptime monitoring
- **Configurable detection pipeline** (confidence threshold, batch size, FPS target)
- **Performance analytics** tracking inference times, confidence scores, and detection counts
- **Interactive dashboard** for live monitoring and manual detection triggers

## Tech Stack

- Python 3.x
- Flask (REST API & control server)
- YOLOv8 (object detection model)
- OpenCV (image processing)

## Setup & Run

```bash
pip install -r requirements.txt
python app.py
```

The server starts at `http://localhost:5001`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/detect` | Run detection on current frame |
| GET | `/api/inventory` | Get all inventory items (filter: `?category=`, `?color=`) |
| GET | `/api/inventory/summary` | Get inventory grouped by category and color |
| DELETE | `/api/inventory/<id>` | Remove an item from inventory |
| POST | `/api/camera/start` | Start camera feed |
| POST | `/api/camera/stop` | Stop camera feed |
| GET | `/api/camera/status` | Get camera status and uptime |
| GET | `/api/config` | Get detection configuration |
| PUT | `/api/config` | Update detection configuration |
| GET | `/api/detection-log` | Get detection history |
| GET | `/api/stats` | Get performance statistics |

## Performance Metrics

- Detection accuracy: 88%+ on clothing items
- Inference latency: ~68ms average (optimized from 120ms via quantization and frame batching)
- Throughput: 15 FPS on edge hardware
- Stable operation: 8+ hours continuous detection

## Architecture

- **Detection Engine**: YOLOv8 model with configurable confidence thresholds
- **Inventory Service**: Dynamic item tracking with deduplication
- **Camera Controller**: Feed management with start/stop/status
- **REST API**: Flask-based endpoints for all operations
- **Dashboard**: Real-time web interface for monitoring
