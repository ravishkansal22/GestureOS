import numpy as np
import tensorflow as tf
import json

class HybridClassifier:

    def __init__(self):

        self.model = tf.keras.models.load_model("models/gesture_model.keras")

        with open("models/gesture_labels.json", "r") as f:
            self.labels = json.load(f)

        self.labels = {int(k): v for k, v in self.labels.items()}

    def preprocess(self, landmarks):

        data = []

        for x, y in landmarks:
            data.append(x)
            data.append(y)

        return np.array(data).reshape(1, -1)

    def predict(self, landmarks):

        data = self.preprocess(landmarks)

        prediction = self.model.predict(data, verbose=0)

        class_id = np.argmax(prediction)

        confidence = float(np.max(prediction))

        gesture = self.labels[class_id]

        return gesture, confidence
