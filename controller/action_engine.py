from controller.gesture_mapper import GestureMapper
from controller.actions import execute_action


class ActionEngine:

    def __init__(self):

        self.mapper = GestureMapper()

    def execute(self, gesture_name, runtime_params=None):

        # Always reload latest mapping
        self.mapper.load_mapping()

        action_data = self.mapper.get_action(gesture_name)

        # Debug prints (keep for now)
        print("DEBUG gesture:", gesture_name)
        print("DEBUG mapping:", action_data)
        print("DEBUG type:", type(action_data))

        if action_data is None:

            print(f"No action mapped for gesture: {gesture_name}")
            return

        try:

            # Case 1: simple string action
            if isinstance(action_data, str):

                execute_action(action_data)
                return

            # Case 2: dictionary action
            if isinstance(action_data, dict):

                action_name = action_data.get("action")

                if not action_name:

                    print("Invalid action format: missing 'action' key")
                    return

                params = dict(action_data)

                # Remove "action" key
                params.pop("action", None)

                if runtime_params:
                    params.update(runtime_params)

                execute_action(action_name, **params)

                return

            print("Invalid action format: unsupported type")

        except Exception as e:

            print("Execution error:", e)
