import os
import json
import numpy as np
import tensorflow as tf


# Absolute path to GestureOS root directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

MODEL_PATH = os.path.join(BASE_DIR, "models", "gesture_model.keras")
LABEL_PATH = os.path.join(BASE_DIR, "models", "gesture_labels.json")


class GestureClassifier:

    def __init__(self):

        print("Loading gesture model...")

        self.model = tf.keras.models.load_model(MODEL_PATH)

        with open(LABEL_PATH, "r") as f:
            self.label_map = json.load(f)

        # reverse map
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

        return np.array(landmarks).reshape(1, -1)


    def predict(self, hand, frame_width, frame_height):

        if hand is None:
            return "NONE", 0.0

        data = self.extract_landmarks(hand, frame_width, frame_height)

        prediction = self.model.predict(data, verbose=0)

        class_id = np.argmax(prediction)
        confidence = float(np.max(prediction))

        gesture_name = self.index_to_label[class_id]

        return gesture_name, confidence
