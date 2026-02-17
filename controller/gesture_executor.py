import json
import os

from controller.system_controller import SystemController


MAP_PATH = os.path.join("data", "gesture_action_map.json")


class GestureExecutor:

    def __init__(self):

        print("Gesture Executor Initialized")

        if not os.path.exists(MAP_PATH):
            raise FileNotFoundError(f"Gesture map not found: {MAP_PATH}")

        with open(MAP_PATH, "r") as f:
            self.gesture_map = json.load(f)

        self.system_controller = SystemController()


    def execute(self, gesture_name, x=None, y=None):

        if gesture_name == "NONE":
            return

        if gesture_name not in self.gesture_map:
            return

        action_name = self.gesture_map[gesture_name]

        try:

            # IMPORTANT: call system_controller.execute_action()
            self.system_controller.execute_action(action_name, x, y)

            print(f"Executed gesture: {gesture_name} → action: {action_name}")

        except Exception as e:

            print("Gesture execution error:", e)
