from flask import Flask, request, jsonify
import uuid
import time
from datetime import datetime
import random
import os

app = Flask(__name__)

inventory = {}
detection_log = []
camera_status = {"active": False, "feed_url": None, "started_at": None}
detection_config = {
    "confidence_threshold": 0.65,
    "model": "yolov8n",
    "frame_batch_size": 4,
    "target_fps": 15,
}

CLOTHING_CATEGORIES = [
    "t-shirt", "shirt", "jeans", "trousers", "jacket", "hoodie",
    "dress", "skirt", "sweater", "shorts", "blazer", "coat",
    "tank-top", "polo", "cardigan", "scarf", "hat", "socks"
]

COLORS = [
    "red", "blue", "black", "white", "green", "navy",
    "gray", "beige", "brown", "pink", "yellow", "purple"
]


def simulate_detection():
    num_items = random.randint(1, 5)
    detections = []
    for _ in range(num_items):
        detection = {
            "item_id": str(uuid.uuid4())[:8],
            "category": random.choice(CLOTHING_CATEGORIES),
            "color": random.choice(COLORS),
            "confidence": round(random.uniform(0.70, 0.98), 2),
            "bounding_box": {
                "x": random.randint(50, 400),
                "y": random.randint(50, 400),
                "width": random.randint(80, 200),
                "height": random.randint(100, 300),
            },
            "detected_at": datetime.utcnow().isoformat(),
            "inference_time_ms": round(random.uniform(55, 85), 1),
        }
        detections.append(detection)
    return detections


@app.route("/api/detect", methods=["POST"])
def run_detection():
    start_time = time.time()
    detections = simulate_detection()

    for det in detections:
        item_key = f"{det['color']}_{det['category']}"
        if item_key in inventory:
            inventory[item_key]["count"] += 1
            inventory[item_key]["last_seen"] = det["detected_at"]
            inventory[item_key]["confidence"] = max(
                inventory[item_key]["confidence"], det["confidence"]
            )
        else:
            inventory[item_key] = {
                "item_id": det["item_id"],
                "category": det["category"],
                "color": det["color"],
                "count": 1,
                "confidence": det["confidence"],
                "first_seen": det["detected_at"],
                "last_seen": det["detected_at"],
            }

        detection_log.append(det)

    elapsed = round((time.time() - start_time) * 1000, 1)

    return jsonify({
        "detections": detections,
        "count": len(detections),
        "inference_time_ms": elapsed,
        "model": detection_config["model"],
    })


@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    category = request.args.get("category")
    color = request.args.get("color")

    items = list(inventory.values())

    if category:
        items = [i for i in items if i["category"] == category]
    if color:
        items = [i for i in items if i["color"] == color]

    return jsonify({
        "total_items": len(items),
        "total_count": sum(i["count"] for i in items),
        "items": items,
    })


@app.route("/api/inventory/summary", methods=["GET"])
def inventory_summary():
    by_category = {}
    by_color = {}

    for item in inventory.values():
        cat = item["category"]
        col = item["color"]
        by_category[cat] = by_category.get(cat, 0) + item["count"]
        by_color[col] = by_color.get(col, 0) + item["count"]

    return jsonify({
        "total_unique_items": len(inventory),
        "total_count": sum(i["count"] for i in inventory.values()),
        "by_category": dict(sorted(by_category.items(), key=lambda x: x[1], reverse=True)),
        "by_color": dict(sorted(by_color.items(), key=lambda x: x[1], reverse=True)),
    })


@app.route("/api/inventory/<item_id>", methods=["DELETE"])
def remove_item(item_id):
    to_remove = None
    for key, item in inventory.items():
        if item["item_id"] == item_id:
            to_remove = key
            break
    if to_remove:
        removed = inventory.pop(to_remove)
        return jsonify({"message": "Item removed", "item": removed})
    return jsonify({"error": "Item not found"}), 404


@app.route("/api/camera/start", methods=["POST"])
def start_camera():
    camera_status["active"] = True
    camera_status["started_at"] = datetime.utcnow().isoformat()
    camera_status["feed_url"] = "/api/camera/feed"
    return jsonify({"message": "Camera started", "status": camera_status})


@app.route("/api/camera/stop", methods=["POST"])
def stop_camera():
    camera_status["active"] = False
    camera_status["started_at"] = None
    return jsonify({"message": "Camera stopped", "status": camera_status})


@app.route("/api/camera/status", methods=["GET"])
def get_camera_status():
    uptime = None
    if camera_status["active"] and camera_status["started_at"]:
        start = datetime.fromisoformat(camera_status["started_at"])
        uptime = str(datetime.utcnow() - start)
    return jsonify({**camera_status, "uptime": uptime})


@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(detection_config)


@app.route("/api/config", methods=["PUT"])
def update_config():
    data = request.get_json()
    for key in data:
        if key in detection_config:
            detection_config[key] = data[key]
    return jsonify({"message": "Configuration updated", "config": detection_config})


@app.route("/api/detection-log", methods=["GET"])
def get_detection_log():
    limit = request.args.get("limit", 50, type=int)
    return jsonify({
        "total": len(detection_log),
        "entries": detection_log[-limit:],
    })


@app.route("/api/stats", methods=["GET"])
def get_stats():
    if not detection_log:
        return jsonify({"message": "No detections yet"})

    avg_confidence = sum(d["confidence"] for d in detection_log) / len(detection_log)
    avg_inference = sum(d["inference_time_ms"] for d in detection_log) / len(detection_log)

    return jsonify({
        "total_detections": len(detection_log),
        "unique_items": len(inventory),
        "average_confidence": round(avg_confidence, 3),
        "average_inference_ms": round(avg_inference, 1),
        "model": detection_config["model"],
        "fps_target": detection_config["target_fps"],
    })


@app.route("/")
def dashboard():
    return app.send_static_file("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
