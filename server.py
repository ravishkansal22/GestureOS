from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import cv2
import threading
import main
import json
import os

# ============================================================
# FASTAPI INITIALIZATION
# ============================================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_gesture_map():
    """
    Safely loads gesture_action_map.json
    """
    try:
        with open("data/gesture_action_map.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading gesture map:", e)
        return {}

# ============================================================
# ENGINE CONTROL ROUTES
# ============================================================

@app.post("/start")
def start():
    """
    Starts gesture engine in background thread
    Prevents multiple instances
    """
    if main._engine_running:
        return {"status": "Already running"}

    threading.Thread(target=main.start_engine, daemon=True).start()
    return {"status": "Camera started"}


@app.post("/stop")
def stop():
    """
    Stops gesture engine safely
    """
    main.stop_engine()
    return {"status": "Engine stopped"}

# ============================================================
# VIDEO STREAM ROUTE
# ============================================================

def generate_frames():
    while True:
        frame = main.get_latest_frame()
        if frame is None:
            continue

        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


@app.get("/video")
def video_feed():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# ============================================================
# STATUS ROUTES
# ============================================================

@app.get("/status")
def get_status():
    """
    Returns live system_state from main.py
    """
    return main.system_state


@app.get("/prediction")
def prediction():
    """
    Returns latest detected gesture info
    """
    return main.latest_prediction

# ============================================================
# GESTURE MAPPING ROUTES
# ============================================================

@app.get("/mappings")
def get_mappings():

    gesture_map = load_gesture_map()

    fixed_gestures = [
        "RIGHT_CLICK",
        "LEFT_CLICK",
        "SCROLL",
        "DRAG",
        "CURSOR_MOVE",
        "LEFT_SWIPE_UP",
        "LEFT_SWIPE_DOWN",
        "LEFT_SWIPE_LEFT",
        "LEFT_SWIPE_RIGHT"
    ]

    response = []

    for gesture, config in gesture_map.items():

        action = config.get("action", "N/A")
        status = "Fixed" if gesture in fixed_gestures else "Custom"

        response.append({
            "gesture": gesture,
            "action": action.upper(),
            "status": status
        })

    return response

# ============================================================
# RETRAIN PLACEHOLDER (No conflict change)
# ============================================================

@app.post("/retrain")
def retrain():
    """
    Placeholder retrain endpoint
    (We will wire this properly next)
    """
    return {"message": "Retraining triggered"}

# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {"message": "GestureOS Backend Running"}