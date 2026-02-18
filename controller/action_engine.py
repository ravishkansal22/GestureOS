from controller.gesture_mapper import GestureMapper
import controller.actions as actions


class ActionEngine:

    def __init__(self):

        self.mapper = GestureMapper()

    def execute(self, gesture_name, runtime_params=None):

        self.mapper.load_mapping()

        action_data = self.mapper.get_action(gesture_name)

        if action_data is None:

            print(f"No action mapped for gesture: {gesture_name}")
            return

        try:

            # CASE 1: simple action string
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

            # CASE 2: action with parameters
            elif isinstance(action_data, dict):

                action_name = action_data.get("action")

                if not isinstance(action_name, str):

                    print("Invalid action format. 'action' must be string.")
                    return

                action_function = getattr(actions, action_name, None)

                if action_function is None:

                    print(f"Action function not found: {action_name}")
                    return

                params = dict(action_data)

                params.pop("action", None)

                if runtime_params:
                    params.update(runtime_params)

                action_function(**params)

                print(f"Executed: {gesture_name} → {action_name}")

        except Exception as e:

            print("Execution error:", e)
