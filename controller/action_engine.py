from controller.gesture_mapper import GestureMapper
import controller.actions as actions

import webbrowser
import subprocess
import os


class ActionEngine:

    def __init__(self):

        self.mapper = GestureMapper()

    def execute(self, gesture_name, runtime_params=None):

        # Reload latest mapping
        self.mapper.load_mapping()

        action_data = self.mapper.get_action(gesture_name)

        if action_data is None:

            print(f"No action mapped for gesture: {gesture_name}")
            return

        try:

            # ==============================
            # CASE 1: simple system action
            # example: "volume_up"
            # ==============================
            if isinstance(action_data, str):

                action_function = getattr(actions, action_data, None)

                if action_function is None:

                    print(f"Action function not found: {action_data}")
                    return

                if runtime_params:
                    action_function(**runtime_params)
                else:
                    action_function()

                print(f"Executed: {gesture_name} -> {action_data}")

            # ==============================
            # CASE 2: structured action
            # example:
            # { "type": "website", "value": "https://youtube.com" }
            # ==============================
            elif isinstance(action_data, dict):

                action_type = action_data.get("type")
                value = action_data.get("value")

                if action_type is None or value is None:

                    print("Invalid action format.")
                    return

                # WEBSITE ACTION
                if action_type == "website":

                    webbrowser.open(value)

                    print(f"Opened website: {value}")

                # APPLICATION ACTION
                elif action_type == "app":

                    try:

                        # Try opening directly
                        subprocess.Popen(value)

                        print(f"Opened application: {value}")

                    except Exception:

                        try:
                            # Try opening via shell
                            os.system(f'start "" "{value}"')

                            print(f"Opened application via shell: {value}")

                        except Exception as e:

                            print("Failed to open application:", e)

                # SYSTEM ACTION
                elif action_type == "system":

                    action_function = getattr(actions, value, None)

                    if action_function is None:

                        print(f"System action not found: {value}")
                        return

                    if runtime_params:
                        action_function(**runtime_params)
                    else:
                        action_function()

                    print(f"Executed system action: {value}")

                # LEGACY SUPPORT (old format)
                elif "action" in action_data:

                    action_name = action_data.get("action")

                    action_function = getattr(actions, action_name, None)

                    if action_function is None:

                        print(f"Action function not found: {action_name}")
                        return

                    params = dict(action_data)

                    params.pop("action", None)

                    if runtime_params:
                        params.update(runtime_params)

                    action_function(**params)

                    print(f"Executed: {gesture_name} -> {action_name}")

                else:

                    print("Unknown action type.")

        except Exception as e:

            print("Execution error:", e)
