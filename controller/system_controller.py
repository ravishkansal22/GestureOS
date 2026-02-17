from controller.action_engine import ActionEngine
import pyautogui
import subprocess
import platform


class SystemController:

    def __init__(self):

        print("System Controller Initialized")

        self.action_engine = ActionEngine()


    # EXISTING FUNCTION (DO NOT CHANGE)
    def execute_action(self, gesture_name, x=None, y=None):

        params = {}

        if x is not None and y is not None:

            params["x"] = x
            params["y"] = y

        try:

            self.action_engine.execute(gesture_name, params)

        except Exception as e:

            print("Execution error:", e)


    # NEW SAFE DIRECT METHODS (optional use)
    # These DO NOT interfere with ActionEngine

    def screenshot(self):

        pyautogui.hotkey("win", "shift", "s")


    def volume_up(self):

        pyautogui.press("volumeup")


    def volume_down(self):

        pyautogui.press("volumedown")


    def open_start_menu(self):

        pyautogui.press("win")


    def switch_app(self):

        pyautogui.hotkey("alt", "tab")


    def open_chrome(self):

        if platform.system() == "Windows":
            subprocess.Popen("start chrome", shell=True)
