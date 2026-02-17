import cv2
from vision.hand_tracker import HandTracker

tracker = HandTracker()

while True:

    frame, hands = tracker.update()

    if frame is None:
        break

    if hands:
        print("Index:", hands[0].index_tip)
        print("Pinch distance:", hands[0].pinch_distance)

    cv2.imshow("Hand Tracker", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

tracker.release()
