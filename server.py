from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import cv2
import threading
import main
import json
import os

app = FastAPI()   # ← THIS MUST EXIST AT TOP LEVEL

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start gesture engine in background
@app.post("/start")
def start():
    threading.Thread(target=main.start_engine, daemon=True).start()
    return {"status": "Camera started"}

def generate_frames():
    while True:
        frame = main.get_latest_frame()
        if frame is None:
            continue

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
        )

@app.get("/video")
def video_feed():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
system_state = {
    "status": "STANDBY",
    "camera": "DISCONNECTED",
    "total_gestures": 0,
    "accuracy": 0,
    "fps": 0,
    "custom_gestures": 0
}


@app.get("/status")
def get_status():
    return {
        "status": system_state["status"],
        "camera": system_state["camera"],
        "total_gestures": system_state["total_gestures"],
        "accuracy": system_state["accuracy"],
        "fps": system_state["fps"],
        "custom_gestures": system_state["custom_gestures"],

        # 👇 NEW ADDITIONS
        "left_hand_gestures": 4,
        "right_hand_gestures": 5,

        "gesture_library": {
            "swipeup": "SCROLL UP / PREV TAB",
            "swipedown": "SCROLL DOWN / NEXT TAB",
            "swipeleft": "NAVIGATE BACK",
            "swiperight": "NAVIGATE FORWARD",
            "rightclick": "MOUSE RIGHT CLICK",
            "leftclick": "MOUSE LEFT CLICK",
            "scroll": "SCROLL PAGE",
            "drag": "MOUSE DRAG",
            "cursor": "CURSOR MOVE"
        }
    }
def load_gesture_map():
    try:
        with open("data\gesture_action_map.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading gesture map:", e)
        return {}
    
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

    print("FINAL RESPONSE:", response)  # 👈 debug

    return response


@app.get("/prediction")
def prediction():
    return main.latest_prediction


@app.post("/retrain")
def retrain():
    return {"message": "Retraining triggered"}

@app.get("/")
def root():
    return {"message": "GestureOS Backend Running"}

