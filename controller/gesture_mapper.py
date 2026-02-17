import json
import os


class GestureMapper:

    def __init__(self, mapping_file="data/gesture_action_map.json"):

        self.mapping_file = mapping_file
        self.mapping = {}

        self.load_mapping()

    def load_mapping(self):
        """
        Load gesture-action mapping from JSON file
        """

        if not os.path.exists(self.mapping_file):

            os.makedirs(os.path.dirname(self.mapping_file), exist_ok=True)

            with open(self.mapping_file, "w") as f:
                json.dump({}, f, indent=4)

            self.mapping = {}
            return

        try:

            with open(self.mapping_file, "r") as f:
                self.mapping = json.load(f)

        except json.JSONDecodeError:

            print("Invalid JSON format in gesture_action_map.json")
            self.mapping = {}

    def save_mapping(self):
        """
        Save mapping to JSON file
        """

        os.makedirs(os.path.dirname(self.mapping_file), exist_ok=True)

        with open(self.mapping_file, "w") as f:
            json.dump(self.mapping, f, indent=4)

    def get_action(self, gesture_name):
        """
        Return action name mapped to gesture
        """

        return self.mapping.get(gesture_name)

    def add_gesture(self, gesture_name, action_name):
        """
        Add new gesture → action mapping
        """

        self.mapping[gesture_name] = action_name
        self.save_mapping()

        print(f"Added mapping: {gesture_name} → {action_name}")

    def delete_gesture(self, gesture_name):
        """
        Remove gesture mapping
        """

        if gesture_name in self.mapping:

            del self.mapping[gesture_name]

            self.save_mapping()

            print(f"Deleted gesture: {gesture_name}")

    def list_gestures(self):
        """
        Return list of gestures
        """

        return list(self.mapping.keys())

    def list_mappings(self):
        """
        Return full mapping dictionary
        """

        return self.mapping

    def gesture_exists(self, gesture_name):
        """
        Check if gesture exists
        """

        return gesture_name in self.mapping
