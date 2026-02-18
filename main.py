import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import time
import cv2
import argparse
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "gesture_model.keras")
from controller.action_engine import ActionEngine
from controller.gesture_mapper import GestureMapper
from vision.hand_tracker import HandTracker
from vision.mouse_gesture_detector import MouseGestureDetector
from vision.gesture_classifier import GestureClassifier

from controller.cursor_controller import CursorController
from vision.temporal_gesture_detection import TemporalGestureDetector


# Initialize components
mapper = GestureMapper()
engine = ActionEngine()


def simulated_gesture_input():

    # Reload latest gesture mapping
    mapper.load_mapping()

    gestures = mapper.list_gestures()

    print("\nAvailable gestures:")
    for gesture in gestures:
        print("-", gesture)

    print("- EXIT")

    gesture = input("\nEnter gesture: ").strip()

    if gesture == "MOVE_CURSOR":

        try:
            x = float(input("Enter X (0–1): "))
            y = float(input("Enter Y (0–1): "))
            return gesture, {"x": x, "y": y}
        except:
            print("Invalid coordinates")
            return None, None

    return gesture, None


def main(show_window=True):

    print("=====================================")
    print("      GestureOS Started")
    print("      Camera Control Enabled")
    print("=====================================")

    # Initialize vision systems
    tracker = HandTracker(camera_index=0)
    mouse_detector = MouseGestureDetector()
    classifier = GestureClassifier()
    temporal_detector = TemporalGestureDetector()

    model_last_modified = os.path.getmtime(MODEL_PATH)

    # Initialize controllers
    cursor = CursorController()

    last_gesture_time = 0
    gesture_cooldown = 1.0


    while True:

        gesture_name = None
        confidence = 0.0

        current_modified = os.path.getmtime(MODEL_PATH)

        if current_modified != model_last_modified:

            print("New model detected. Reloading...")

            classifier = GestureClassifier()

            model_last_modified = current_modified

        frame, hands = tracker.update()

        if frame is None:
            break

        right_hand = None
        left_hand = None

        for hand in hands:

            if hand.hand_label == "Right":
                right_hand = hand

            elif hand.hand_label == "Left":
                left_hand = hand


        # ==========================
        # RIGHT HAND → MOUSE CONTROL
        # ==========================

        if right_hand:

            mouse_result = mouse_detector.detect([right_hand])

            gesture = mouse_result["gesture"]
            position = mouse_result["position"]
            scroll = mouse_result["scroll"]

            if position:

                x, y = position

                if gesture == "MOVE_CURSOR":
                    cursor.move_cursor(
                        x, y,
                        tracker.frame_width,
                        tracker.frame_height
                    )

                elif gesture == "LEFT_CLICK":
                    cursor.left_click()

                elif gesture == "RIGHT_CLICK":
                    cursor.right_click()

                elif gesture == "DRAG":
                    cursor.drag(
                        x, y,
                        tracker.frame_width,
                        tracker.frame_height
                    )

                elif gesture == "DRAG_END":
                    cursor.drag_end()

                elif gesture == "SCROLL":
                    cursor.scroll(scroll)


        # ==========================
        # LEFT HAND → GESTURE CONTROL
        # ==========================

        if left_hand:

            gesture_name, confidence = classifier.predict(
                 left_hand,
                 tracker.frame_width,
                 tracker.frame_height
            )

    # DEBUG: verify PINKY detection
            print("Detected gesture:", gesture_name, "Confidence:", confidence)

    # Initialize temporal gesture variable
            temporal_gesture = None

    # Activate temporal mode ONLY when PINKY is held
            if gesture_name == "PINKY_FINGER" and confidence > 0.90:

                temporal_gesture = temporal_detector.update(left_hand)

                if temporal_gesture:

                    engine.execute(temporal_gesture)

                    cv2.putText(
                        frame,
                        "TEMPORAL: " + temporal_gesture,
                         (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                         (255, 0, 0),
                         2
                     )

        # Show temporal mode indicator
                cv2.putText(
                    frame,
                    "TEMPORAL MODE ACTIVE",
                    (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2
                )

            else:
                temporal_detector.reset()

    # Execute static gestures normally
        current_time = time.time()

        if confidence > 0.85 and current_time - last_gesture_time > gesture_cooldown:

            engine.execute(gesture_name, None)

            last_gesture_time = current_time

    # Display static gesture
        cv2.putText(
            frame,
            f"{gesture_name} ({confidence:.2f})",
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        if show_window:
            cv2.imshow("GestureOS", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break





    tracker.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--background",
        action="store_true",
        help="Run GestureOS in background mode"
    )

    args = parser.parse_args()

    main(show_window=not args.background)
