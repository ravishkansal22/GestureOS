import json
import os

MAPPING_FILE = "data/gesture_action_map.json"


class GestureMapper:

    def __init__(self):
        self.mapping = {}
        self.load_mapping()

    def load_mapping(self):
        """
        Load gesture-action mapping from file
        """
        if os.path.exists(MAPPING_FILE):
            with open(MAPPING_FILE, "r") as f:
                self.mapping = json.load(f)
        else:
            self.mapping = {}
            self.save_mapping()

    def save_mapping(self):
        """
        Save gesture-action mapping to file
        """
        os.makedirs("data", exist_ok=True)
        with open(MAPPING_FILE, "w") as f:
            json.dump(self.mapping, f, indent=4)

    def get_action(self, gesture_name):
        """
        Get action assigned to gesture
        """
        return self.mapping.get(gesture_name, None)

    def add_gesture(self, gesture_name, action_name):
        """
        Add new gesture-action mapping
        """
        self.mapping[gesture_name] = action_name
        self.save_mapping()

    def delete_gesture(self, gesture_name):
        """
        Delete gesture mapping
        """
        if gesture_name in self.mapping:
            del self.mapping[gesture_name]
            self.save_mapping()

    def list_gestures(self):
        return self.mapping
