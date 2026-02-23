import cv2
import csv
import os
import sys
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vision.hand_tracker import HandTracker


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
RECORD_SECONDS = 5
COUNTDOWN_SECONDS = 3


class AutoGestureCollector:

    def __init__(self, gesture_name):

        self.gesture_name = gesture_name
        self.tracker = HandTracker(max_hands=2, camera_index=0)

        os.makedirs("data", exist_ok=True)

        self.file = open(DATASET_PATH, "a", newline="")
        self.writer = csv.writer(self.file)


    def extract_landmarks(self, hand):

        landmarks = []

        frame_width = self.tracker.frame_width
        frame_height = self.tracker.frame_height

        for (x, y) in hand.landmarks:

            # Normalize landmarks (important)
            nx = x / frame_width
            ny = y / frame_height

            landmarks.append(nx)
            landmarks.append(ny)

        return landmarks


    def countdown(self):

        for i in range(COUNTDOWN_SECONDS, 0, -1):

            start = time.time()

            while time.time() - start < 1:

                frame, hands = self.tracker.update()

                if frame is None:
                    continue

                cv2.putText(
                    frame,
                    f"Recording in {i}",
                    (200, 200),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    (0, 0, 255),
                    3,
                )

                cv2.imshow("GestureOS Auto Collector", frame)

                if cv2.waitKey(1) & 0xFF == 27:
                    return False

        return True


    def record(self):

        print(f"\nRecording gesture: {self.gesture_name}")
        print("Hold your LEFT hand gesture and move slightly\n")

        start_time = time.time()
        sample_count = 0

        while time.time() - start_time < RECORD_SECONDS:

            frame, hands = self.tracker.update()

            if frame is None:
                continue

            left_hand = None

            for hand in hands:

                if hand.hand_label == "Left":
                    left_hand = hand
                    break

            if left_hand:

                landmarks = self.extract_landmarks(left_hand)

                row = landmarks + [self.gesture_name]

                self.writer.writerow(row)

                sample_count += 1

                cv2.putText(
                    frame,
                    f"Recording... {sample_count}",
                    (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

            else:

                cv2.putText(
                    frame,
                    "LEFT HAND NOT DETECTED",
                    (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("GestureOS Auto Collector", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        print(f"\nCollected {sample_count} samples")


    def run(self):

        if not self.countdown():
            return

        self.record()

        self.file.close()
        self.tracker.release()

        print("\nGesture recording complete.")


if __name__ == "__main__":

    if len(sys.argv) > 1:
        gesture_name = sys.argv[1].strip().upper()
    else:
        gesture_name = input("Enter gesture name: ").strip().upper()

    collector = AutoGestureCollector(gesture_name)
    collector.run()
