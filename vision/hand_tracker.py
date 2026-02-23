import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass


# ============================
# Data structure for hand data
# ============================

@dataclass
class HandData:
    hand_id: int
    hand_label: str 
    landmarks: list
    index_tip: tuple
    thumb_tip: tuple
    middle_tip: tuple
    wrist: tuple
    pinch_distance: float


# ============================
# Hand Tracker Class
# ============================

class HandTracker:
    def __init__(
        self,
        max_hands=2,
        detection_confidence=0.7,
        tracking_confidence=0.7,
        camera_index=0,
    ):
        self.max_hands = max_hands

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

        print("Attempting to open camera...")

        if not self.cap.isOpened():
           print("❌ Camera failed to open.")
        else:
           print("✅ Camera opened successfully.")

        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


    # ============================
    # Get frame from camera
    # ============================

    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None

        frame = cv2.flip(frame, 1)
        return frame


    # ============================
    # Process frame and detect hands
    # ============================

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.hands.process(rgb_frame)

        hand_data_list = []

        if results.multi_hand_landmarks:

            for hand_id, (hand_landmarks, handedness) in enumerate(
                zip(results.multi_hand_landmarks, results.multi_handedness)
           ):

                hand_label = handedness.classification[0].label  # "Left" or "Right"

                landmarks = []

                for lm in hand_landmarks.landmark:
                    x = int(lm.x * self.frame_width)
                    y = int(lm.y * self.frame_height)
                    landmarks.append((x, y))

                index_tip = landmarks[8]
                thumb_tip = landmarks[4]
                middle_tip = landmarks[12]
                wrist = landmarks[0]

                pinch_distance = np.linalg.norm(
                    np.array(index_tip) - np.array(thumb_tip)
                )

                hand_data = HandData(
                    hand_id=hand_id,
                    hand_label=hand_label,  # REQUIRED FIX
                    landmarks=landmarks,
                    index_tip=index_tip,
                    thumb_tip=thumb_tip,
                    middle_tip=middle_tip,
                    wrist=wrist,
                    pinch_distance=pinch_distance,
                )

                hand_data_list.append(hand_data)

        return frame, hand_data_list


    # ============================
    # Main update function
    # ============================

    def update(self):

        frame = self.get_frame()

        if frame is None:
            return None, []

        frame, hand_data_list = self.process_frame(frame)

        return frame, hand_data_list


    # ============================
    # Release camera
    # ============================

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
