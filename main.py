import time
import cv2
from controller.action_engine import ActionEngine
from controller.gesture_mapper import GestureMapper
from vision.hand_tracker import HandTracker
from vision.mouse_gesture_detector import MouseGestureDetector
from vision.gesture_classifier import GestureClassifier

from controller.cursor_controller import CursorController


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


def main():

    print("=====================================")
    print("      GestureOS Started")
    print("      Camera Control Enabled")
    print("=====================================")

    # Initialize vision systems
    tracker = HandTracker(camera_index=1)
    mouse_detector = MouseGestureDetector()
    classifier = GestureClassifier()

    # Initialize controllers
    cursor = CursorController()

    last_gesture_time = 0
    gesture_cooldown = 1.0


    while True:

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

            current_time = time.time()

            if confidence > 0.85 and current_time - last_gesture_time > gesture_cooldown:

                engine.execute(gesture_name, None)

                last_gesture_time = current_time

            cv2.putText(
                frame,
                f"{gesture_name} ({confidence:.2f})",
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )


        cv2.imshow("GestureOS", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break


    tracker.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
