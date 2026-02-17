import cv2

from vision.hand_tracker import HandTracker
from vision.mouse_gesture_detector import MouseGestureDetector
from controller.cursor_controller import CursorController


tracker = HandTracker()
detector = MouseGestureDetector()
cursor = CursorController()


frame_width = tracker.frame_width
frame_height = tracker.frame_height


while True:

    frame, hands = tracker.update()

    if frame is None:
        break

    result = detector.detect(hands)

    gesture = result["gesture"]
    position = result["position"]
    scroll = result["scroll"]

    if position is not None:

        x, y = position

        if gesture == "MOVE_CURSOR":
            cursor.move_cursor(x, y, frame_width, frame_height)

        elif gesture == "LEFT_CLICK":
            cursor.left_click()

        elif gesture == "RIGHT_CLICK":
            cursor.right_click()

        elif gesture == "DRAG":
            cursor.drag(x, y, frame_width, frame_height)

        elif gesture == "DRAG_END":
            cursor.drag_end()

        elif gesture == "SCROLL":
            cursor.scroll(scroll)

    cv2.imshow("GestureOS Mouse Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break


tracker.release()
