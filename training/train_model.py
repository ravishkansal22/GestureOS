import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras


DATASET_PATH = os.path.join("data", "dataset.csv")
MODEL_PATH = os.path.join("models", "gesture_model.keras")
LABEL_PATH = os.path.join("models", "gesture_labels.json")


def load_dataset():

    print("Loading dataset...")

    df = pd.read_csv(DATASET_PATH, header=None)

    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values

    return X, y


def encode_labels(y):

    encoder = LabelEncoder()

    y_encoded = encoder.fit_transform(y)

    label_map = {
        int(i): label
        for i, label in enumerate(encoder.classes_)
    }

    return y_encoded, label_map


def build_model(input_size, num_classes):

    model = keras.Sequential([
        keras.layers.Dense(128, activation="relu", input_shape=(input_size,)),
        keras.layers.Dropout(0.3),

        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dropout(0.3),

        keras.layers.Dense(32, activation="relu"),

        keras.layers.Dense(num_classes, activation="softmax")
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


def train():

    X, y = load_dataset()

    y_encoded, label_map = encode_labels(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )

    model = build_model(X.shape[1], len(label_map))

    print("\nTraining model...")

    model.fit(
        X_train,
        y_train,
        epochs=30,
        batch_size=32,
        validation_data=(X_test, y_test)
    )

    os.makedirs("models", exist_ok=True)

    model.save(MODEL_PATH)

    with open(LABEL_PATH, "w") as f:
        json.dump(label_map, f)

    print("\nModel saved to:", MODEL_PATH)
    print("Labels saved to:", LABEL_PATH)


if __name__ == "__main__":
    train()
