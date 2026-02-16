from controller.gesture_mapper import GestureMapper
import controller.actions as actions


class SystemController:

    def __init__(self):
        print("System Controller Initialized")
        self.mapper = GestureMapper()

    def execute_action(self, gesture_name, x=None, y=None):

        self.mapper.load_mapping()

        action_name = self.mapper.get_action(gesture_name)

        if action_name is None:
            print("No action mapped")
            return

        try:

            if action_name == "move_cursor":
                actions.move_cursor(x, y)

            else:
                action_function = getattr(actions, action_name, None)

                if action_function:
                    action_function()
                else:
                    print(f"Action '{action_name}' not implemented")

        except Exception as e:
            print("Error:", e)
