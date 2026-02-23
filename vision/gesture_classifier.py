import os
import json
import numpy as np
import tensorflow as tf

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

MODEL_PATH = os.path.join(BASE_DIR, "models", "gesture_model.keras")
LABEL_PATH = os.path.join(BASE_DIR, "models", "gesture_labels.json")
DATASET_DIR = os.path.join(BASE_DIR, "data", "dataset")

class GestureClassifier:

    def __init__(self):

        print("Loading gesture model...")
        self.model = tf.keras.models.load_model(MODEL_PATH)

        with open(LABEL_PATH, "r") as f:
            self.label_map = json.load(f)

        self.index_to_label = {
            int(k): v for k, v in self.label_map.items()
        }

        print("Gesture model loaded.")


    def extract_landmarks(self, hand, frame_width, frame_height):

        landmarks = []

        for (x, y) in hand.landmarks:
            nx = x / frame_width
            ny = y / frame_height
            landmarks.append(nx)
            landmarks.append(ny)

        return np.array(landmarks)


    def save_sample(self, hand, gesture_name, frame_width=None, frame_height=None):
        """
        Saves landmark sample for retraining
        """

        if hand is None:
            return

        if frame_width is None or frame_height is None:
            frame_width = 640
            frame_height = 480

        data = self.extract_landmarks(hand, frame_width, frame_height)

        gesture_path = os.path.join(DATASET_DIR, gesture_name)

        os.makedirs(gesture_path, exist_ok=True)

        sample_count = len(os.listdir(gesture_path))
        file_path = os.path.join(gesture_path, f"{sample_count}.npy")

        np.save(file_path, data)


    def predict(self, hand, frame_width, frame_height):

        if hand is None:
            return None, 0.0

        data = self.extract_landmarks(hand, frame_width, frame_height)
        data = data.reshape(1, -1)

        prediction = self.model.predict(data, verbose=0)

        class_id = np.argmax(prediction)
        confidence = float(np.max(prediction))

        gesture_name = self.index_to_label[class_id]

        return gesture_name, confidence