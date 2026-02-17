import cv2

from vision.hand_tracker import HandTracker
from vision.gesture_classifier import GestureClassifier
from controller.gesture_executor import GestureExecutor


tracker = HandTracker(camera_index=0)
classifier = GestureClassifier()
executor = GestureExecutor()


while True:

    frame, hands = tracker.update()

    left_hand = None

    for hand in hands:
        if hand.hand_label == "Left":
            left_hand = hand
            break

    gesture, confidence = classifier.predict(
        left_hand,
        tracker.frame_width,
        tracker.frame_height
    )

    if confidence > 0.8:
        executor.execute(gesture)

    cv2.putText(
        frame,
        f"{gesture} ({confidence:.2f})",
        (10, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("GestureOS Full System", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

tracker.release()
