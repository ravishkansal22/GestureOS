import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import time
import cv2
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "gesture_model.keras")

from controller.action_engine import ActionEngine
from controller.gesture_mapper import GestureMapper
from vision.hand_tracker import HandTracker
from vision.mouse_gesture_detector import MouseGestureDetector
from vision.gesture_classifier import GestureClassifier
from backend.gesture_state import set_gesture
from controller.cursor_controller import CursorController
from vision.temporal_gesture_detection import TemporalGestureDetector


# ============================================================
# 🔥 GLOBAL SHARED STATE (used by server.py)
# ============================================================

latest_prediction = {
    "gesture": None,
    "action": None,
    "confidence": 0.0,
    "hand": None,
    "timestamp": None
}

system_state = {
    "model_version": "v2.4.1",
    "accuracy": 0.0,
    "fps": 0,
    "latency": 0,
    "total_gestures": 0,
    "custom_gestures": 0,
    "status": "INITIALIZING",
    "camera": "DISCONNECTED"
}


# Thread control
_engine_running = False
_engine_thread = None
latest_frame = None



def get_latest_frame():
    return latest_frame

# ============================================================
# 🎯 ENGINE START FUNCTION (called by server.py)
# ============================================================

def start_engine(show_window=False):

    global _engine_running

    if _engine_running:
        return

    _engine_running = True

    print("=====================================")
    print("      GestureOS Engine Started")
    print("=====================================")

    # Initialize components
    tracker = HandTracker(camera_index=0)
    mouse_detector = MouseGestureDetector()
    classifier = GestureClassifier()
    temporal_detector = TemporalGestureDetector()
    cursor = CursorController()

    mapper = GestureMapper()
    engine = ActionEngine()
    system_state["custom_gestures"] = len(mapper.list_gestures())
    system_state["status"] = "ONLINE"
    system_state["camera"] = "CONNECTED"
    system_state["status"] = "ACTIVE"
    system_state["camera"] = "CONNECTED"


    last_gesture_time = 0
    gesture_cooldown = 1.0

    model_last_modified = os.path.getmtime(MODEL_PATH)

    fps_counter = 0
    fps_timer = time.time()

    while _engine_running:
        if not _engine_running:
           break

        start_time = time.time()

        frame, hands = tracker.update()

        if frame is None:
            break
        global latest_frame
        latest_frame = frame.copy()

        right_hand = None
        left_hand = None
        
        gesture_name = None
        confidence = 0.0
        detected_action = None
        detected_hand = None
        
        for hand in hands:
            if hand.hand_label == "Right":
                right_hand = hand
            elif hand.hand_label == "Left":
                left_hand = hand

    

        # =====================================================
        # RIGHT HAND → MOUSE CONTROL
        # =====================================================

        if right_hand:

            mouse_result = mouse_detector.detect([right_hand])

            gesture = mouse_result["gesture"]
            position = mouse_result["position"]
            scroll = mouse_result["scroll"]

            if position:
                x, y = position

                if gesture == "MOVE_CURSOR":
                    cursor.move_cursor(x, y, tracker.frame_width, tracker.frame_height)
                    detected_action = "CURSOR_MOVE"

                elif gesture == "LEFT_CLICK":
                    cursor.left_click()
                    detected_action = "MOUSE_LEFT_CLICK"

                elif gesture == "RIGHT_CLICK":
                    cursor.right_click()
                    detected_action = "MOUSE_RIGHT_CLICK"

                elif gesture == "DRAG":
                    cursor.drag(x, y, tracker.frame_width, tracker.frame_height)
                    detected_action = "MOUSE_DRAG"

                elif gesture == "DRAG_END":
                    cursor.drag_end()

                elif gesture == "SCROLL":
                    cursor.scroll(scroll)
                    detected_action = "SCROLL"

                gesture_name = gesture
                confidence = 1.0
                detected_hand = "RIGHT"

        # =====================================================
        # LEFT HAND → CLASSIFIED GESTURES
        # =====================================================

        if left_hand:

            gesture_name, confidence = classifier.predict(
                left_hand,
                tracker.frame_width,
                tracker.frame_height
            )

            set_gesture(gesture_name)
            detected_hand = "LEFT"

            if gesture_name == "PINKY_FINGER" and confidence > 0.90:
                temporal_gesture = temporal_detector.update(left_hand)

                if temporal_gesture:
                    engine.execute(temporal_gesture)
                    detected_action = temporal_gesture

            else:
                temporal_detector.reset()

        # =====================================================
        # STATIC EXECUTION WITH COOLDOWN
        # =====================================================

        current_time = time.time()

        if (
            gesture_name
            and confidence > 0.85
            and current_time - last_gesture_time > gesture_cooldown
        ):
            engine.execute(gesture_name, None)
            system_state["total_gestures"] += 1
            last_gesture_time = current_time

        # =====================================================
        # UPDATE SHARED STATE FOR FRONTEND
        # =====================================================

        if gesture_name:
            latest_prediction.update({
                "gesture": gesture_name,
                "action": detected_action,
                "confidence": round(confidence * 100, 2),
                "hand": detected_hand,
                "timestamp": time.time()
            })
            system_state["accuracy"] = round(confidence * 100, 2)
        else:
    # Reset prediction when no gesture
            latest_prediction.update({
                "gesture": None,
                "action": None,
                "confidence": 0,
                "hand": None,
                "timestamp": None
            })
        
        system_state["accuracy"] = 0

        if gesture_name:
            system_state["status"] = "DETECTING"
        else:
           system_state["status"] = "NONE"
        # =====================================================
        # FPS & LATENCY TRACKING
        # =====================================================

        fps_counter += 1

        if time.time() - fps_timer >= 1:
            system_state["fps"] = fps_counter
            fps_counter = 0
            fps_timer = time.time()

        system_state["latency"] = int((time.time() - start_time) * 1000)

        # =====================================================
        # OPTIONAL DISPLAY
        # =====================================================

        if show_window:
            if gesture_name:
                cv2.putText(
                    frame,
                    f"{gesture_name} ({confidence:.2f})",
                    (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
            # cv2.imshow("GestureOS", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

    tracker.release()
    cv2.destroyAllWindows()
def stop_engine():
    global _engine_running
    _engine_running = False
    system_state["status"] = "STANDBY"
    system_state["camera"] = "DISCONNECTED"




# ============================================================
# SAFE CLI RUN (Optional)
# ============================================================

if __name__ == "__main__":
    start_engine(show_window=True)
import json

def load_gesture_map():
    try:
        with open("gesture_action_map.json", "r") as f:
            return json.load(f)
    except:
        return {}
