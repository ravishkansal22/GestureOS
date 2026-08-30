import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, "data", "settings.json")

DEFAULT_SETTINGS = {

    "mouse_speed": 1.0,
    "click_delay": 0.2,
    "confidence_threshold": 0.85,
    "gesture_cooldown": 1.0,
    "camera_index": 0
}

def load_settings():

    if not os.path.exists(SETTINGS_PATH):

        save_settings(DEFAULT_SETTINGS)

        return dict(DEFAULT_SETTINGS)

    with open(SETTINGS_PATH, "r") as f:

        settings = json.load(f)

    merged = dict(DEFAULT_SETTINGS)
    merged.update(settings)
    return merged

def save_settings(settings):

    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)

    with open(SETTINGS_PATH, "w") as f:

        json.dump(settings, f, indent=4)
