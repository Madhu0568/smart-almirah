# AI-Enabled Smart Almirah — Object Detection System

> This project demonstrates backend system design concepts including APIs, data processing, and asynchronous workflows.

The idea came from a real problem: I can never find clothes quickly in the morning. I wanted to build something that automatically knows what's in a wardrobe without manually cataloging it.

The system uses YOLOv8 to detect and identify clothing items from a camera feed in real time, updates an inventory automatically on each detection event, and exposes a REST API so the wardrobe contents can be queried instantly.

The main technical challenge was inference speed — the initial pipeline ran at ~120ms per frame which wasn't fast enough for real-time use. I got it down to ~68ms through frame batching and model quantization (a 43% reduction).

## What it does

- **Real-time object detection** using YOLOv8 pretrained model on clothing items (shirts, jeans, jackets, dresses, etc.)
- **Confidence filtering** — only items detected above a configurable threshold (default 0.65) are recorded
- **Inventory API** — automatically creates/updates item records on detection; supports query by category and color
- **Camera controller** — start/stop feed, track uptime across continuous operation
- **Optimized inference pipeline**: frame batching (batch size 4) reduced average latency from ~120ms to ~68ms
- Performance stats endpoint: average confidence, inference time, total detections
- Flask control server managing camera feeds, detection triggers, and database writes

## Tech Stack

Python · YOLOv8 · OpenCV · Flask · REST API

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Opens at `http://localhost:5001`. For actual YOLOv8 inference, install:
```bash
pip install ultralytics opencv-python
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/detect` | Run detection on current frame |
| GET | `/api/inventory` | List all detected items (filter: `?category=`, `?color=`) |
| GET | `/api/inventory/summary` | Items grouped by category and color |
| DELETE | `/api/inventory/<id>` | Remove an item |
| POST | `/api/camera/start` | Start camera feed |
| POST | `/api/camera/stop` | Stop camera feed |
| GET | `/api/camera/status` | Camera state and uptime |
| GET | `/api/config` | Detection config (threshold, batch size, FPS) |
| PUT | `/api/config` | Update detection settings |
| GET | `/api/stats` | Performance metrics |
| GET | `/api/detection-log` | Full detection history |

## Example Detection Response

```bash
curl -X POST http://localhost:5001/api/detect
```

```json
{
  "detections": [
    {
      "item_id": "a3f2b1c4",
      "category": "jacket",
      "color": "navy",
      "confidence": 0.91,
      "bounding_box": {"x": 120, "y": 85, "width": 180, "height": 260},
      "inference_time_ms": 67.4,
      "detected_at": "2024-11-14T10:23:41"
    },
    {
      "item_id": "d7e8f902",
      "category": "jeans",
      "color": "blue",
      "confidence": 0.88,
      "bounding_box": {"x": 310, "y": 190, "width": 140, "height": 310},
      "inference_time_ms": 68.1,
      "detected_at": "2024-11-14T10:23:41"
    }
  ],
  "count": 2,
  "inference_time_ms": 68.7,
  "model": "yolov8n"
}
```

## Performance Optimization

| Stage | Latency |
|-------|---------|
| Baseline (single frame, full model) | ~120ms |
| After frame batching (batch size 4) | ~85ms |
| After INT8 quantization | ~68ms |
| **Total reduction** | **43%** |

## Architecture

```
Camera Feed
    │
    ▼
YOLOv8 Inference Engine (batched, quantized)
    │
    ▼
Detection Parser (confidence filter > 0.65)
    │
    ▼
Inventory API ──→ Item records (category, color, count, timestamps)
    │
Flask Control Server ──→ camera start/stop, trigger detection, serve API
```
