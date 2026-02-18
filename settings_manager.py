import json
import os

SETTINGS_PATH = "data/settings.json"

DEFAULT_SETTINGS = {

    "mouse_speed": 1.0,
    "click_delay": 0.2,
    "confidence_threshold": 0.7
}

def load_settings():

    if not os.path.exists(SETTINGS_PATH):

        save_settings(DEFAULT_SETTINGS)

        return DEFAULT_SETTINGS

    with open(SETTINGS_PATH, "r") as f:

        return json.load(f)

def save_settings(settings):

    with open(SETTINGS_PATH, "w") as f:

        json.dump(settings, f, indent=4)
