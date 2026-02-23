import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import time
import cv2
import threading
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "gesture_model.keras")
DATASET_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")

from controller.action_engine import ActionEngine
from controller.gesture_mapper import GestureMapper
from vision.hand_tracker import HandTracker
from vision.mouse_gesture_detector import MouseGestureDetector
from vision.gesture_classifier import GestureClassifier
from backend.gesture_state import set_gesture
from controller.cursor_controller import CursorController
from vision.temporal_gesture_detection import TemporalGestureDetector


# ============================================================
# 🔥 GLOBAL SHARED STATE
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

retrain_state = {
    "phase": "idle",
    "progress": 0
}

ENGINE_MODE = "detect"
COLLECT_GESTURE = None
COLLECT_COUNT = 0
COLLECT_TARGET = 200

_engine_running = False
_engine_thread = None
latest_frame = None
classifier = None


def get_latest_frame():
    return latest_frame


# ============================================================
# 🎯 ENGINE LOOP
# ============================================================

def _engine_loop(show_window=False):

    global _engine_running
    global latest_frame
    global classifier
    global ENGINE_MODE, COLLECT_GESTURE, COLLECT_COUNT

    print("=====================================")
    print("      GestureOS Engine Started")
    print("=====================================")

    tracker = HandTracker(camera_index=0)
    mouse_detector = MouseGestureDetector()
    classifier = GestureClassifier()
    temporal_detector = TemporalGestureDetector()
    cursor = CursorController()

    mapper = GestureMapper()
    engine = ActionEngine()

    system_state["custom_gestures"] = len(mapper.list_gestures())
    system_state["status"] = "ACTIVE"
    system_state["camera"] = "CONNECTED"

    last_gesture_time = 0
    gesture_cooldown = 1.0

    fps_counter = 0
    fps_timer = time.time()

    while _engine_running:

        start_time = time.time()

        frame, hands = tracker.update()

        if frame is None:
            continue

        latest_frame = frame

        right_hand = None
        left_hand = None

        for hand in hands:
            if hand.hand_label == "Right":
                right_hand = hand
            elif hand.hand_label == "Left":
                left_hand = hand

        # =====================================================
        # 🔥 COLLECTION MODE (CSV BASED)
        # =====================================================
        if ENGINE_MODE == "collect":

            retrain_state["phase"] = "collecting"

            if left_hand:

                landmarks = []
                frame_width = tracker.frame_width
                frame_height = tracker.frame_height

                for (x, y) in left_hand.landmarks:
                    nx = x / frame_width
                    ny = y / frame_height
                    landmarks.append(nx)
                    landmarks.append(ny)

                row = landmarks + [COLLECT_GESTURE]

                with open(DATASET_PATH, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(row)

                COLLECT_COUNT += 1

                retrain_state["progress"] = int(
                    (COLLECT_COUNT / COLLECT_TARGET) * 100
                )

            if COLLECT_COUNT >= COLLECT_TARGET:
                ENGINE_MODE = "detect"
                COLLECT_COUNT = 0
                retrain_state["phase"] = "done"
                retrain_state["progress"] = 100
                print("Dataset collection completed.")

            continue

        # =====================================================
        # RIGHT HAND → MOUSE CONTROL
        # =====================================================

        gesture_name = None
        confidence = 0.0
        detected_action = None
        detected_hand = None

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
        # LEFT HAND → CLASSIFIER
        # =====================================================

        if left_hand:

            gesture_name, confidence = classifier.predict(
                left_hand,
                tracker.frame_width,
                tracker.frame_height
            )

            CONF_THRESHOLD = 0.85

            if confidence < CONF_THRESHOLD:
                gesture_name = None
                confidence = 0

            set_gesture(gesture_name)
            detected_hand = "LEFT"

            if gesture_name == "PINKY_FINGER" and confidence > 0.85:
                temporal_gesture = temporal_detector.update(left_hand)
                if temporal_gesture:
                    engine.execute(temporal_gesture)
                    detected_action = temporal_gesture
            else:
                temporal_detector.reset()

        # =====================================================
        # EXECUTION COOLDOWN
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
        # UPDATE STATE
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
            system_state["status"] = "DETECTING"
        else:
            latest_prediction.update({
                "gesture": None,
                "action": None,
                "confidence": 0,
                "hand": None,
                "timestamp": None
            })
            system_state["accuracy"] = 0
            system_state["status"] = "NONE"

        fps_counter += 1
        if time.time() - fps_timer >= 1:
            system_state["fps"] = fps_counter
            fps_counter = 0
            fps_timer = time.time()

        system_state["latency"] = int((time.time() - start_time) * 1000)

    tracker.release()
    cv2.destroyAllWindows()


# ============================================================
# ENGINE CONTROL
# ============================================================

def start_engine(show_window=False):
    global _engine_running, _engine_thread

    if _engine_running:
        return

    _engine_running = True

    _engine_thread = threading.Thread(
        target=_engine_loop,
        args=(show_window,),
        daemon=True
    )
    _engine_thread.start()


def stop_engine():
    global _engine_running
    _engine_running = False
    system_state["status"] = "STANDBY"
    system_state["camera"] = "DISCONNECTED"


def reload_model():
    global classifier
    print("Reloading updated model...")
    classifier = GestureClassifier()
    print("Model reloaded successfully.")


if __name__ == "__main__":
    start_engine(show_window=True)