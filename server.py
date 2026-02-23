from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from retrain_pipeline import retrain
from fastapi import BackgroundTasks
import retrain_pipeline
from training.train_model import train
import time
import main
import subprocess
import cv2
import threading
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
def start_engine():
    main.start_engine(show_window=True)
    return {"status": "engine started"}

@app.post("/stop")
def stop():
    """
    Stops gesture engine safely
    """
    main.stop_engine()
    return {"status": "Engine stopped"}

@app.get("/retrain_status")
def retrain_status():
    return main.retrain_state
# ============================================================
# VIDEO STREAM ROUTE
# ============================================================

def generate_frames():
    while True:
        frame = main.get_latest_frame()

        if not main._engine_running:
            # Engine stopped → wait cleanly
            time.sleep(0.1)
            continue

        if frame is None:
            time.sleep(0.01)
            continue

        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
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
def retrain_model(background_tasks: BackgroundTasks):

    def train_task():
        try:
            main.retrain_state["phase"] = "training"
            main.retrain_state["progress"] = 10

            from retrain_pipeline import retrain
            retrain(None)

            main.retrain_state["progress"] = 100
            main.retrain_state["phase"] = "done"

        except Exception as e:
            print("TRAIN ERROR:", e)
            main.retrain_state["phase"] = "error"
            main.retrain_state["progress"] = 0

    background_tasks.add_task(train_task)


    return {"status": "Training started"}
@app.post("/add_gesture")
def add_gesture(data: dict):

    gesture = data.get("gesture")
    action_type = data.get("type")
    value = data.get("value")

    if not gesture:
        return {"error": "Gesture name required"}

    gesture = gesture.upper()

    gesture_map = load_gesture_map()

    if gesture in gesture_map:
        return {"error": "Gesture already exists"}

    gesture_map[gesture] = {
        "type": action_type,
        "value": value
    }

    with open("data/gesture_action_map.json", "w") as f:
        json.dump(gesture_map, f, indent=4)

    return {"status": "Gesture added successfully"}

# ============================================================
# ROOT
# ============================================================
@app.post("/collect")
def start_collection(data: dict):

    gesture = data.get("gesture")

    if not gesture:
        return {"error": "Gesture required"}

    main.ENGINE_MODE = "collect"
    main.COLLECT_GESTURE = gesture
    main.COLLECT_COUNT = 0

    main.retrain_state["phase"] = "collecting"
    main.retrain_state["progress"] = 0

    return {"status": "Collection started"}
    print("COLLECT ENDPOINT HIT")
    print("ENGINE MODE SET TO:", main.ENGINE_MODE)

@app.get("/")
def root():
    return {"message": "GestureOS Backend Running"}