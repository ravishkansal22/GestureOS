from controller.action_engine import ActionEngine


class SystemController:

    def __init__(self):

        print("System Controller Initialized")

        self.action_engine = ActionEngine()

    def execute_action(self, gesture_name, x=None, y=None):

        params = {}

        # Pass cursor parameters if exist
        if x is not None and y is not None:

            params["x"] = x
            params["y"] = y

        try:

            self.action_engine.execute(gesture_name, params)

        except Exception as e:

            print("Execution error:", e)
