import pyautogui
import subprocess
import os
import webbrowser
import screen_brightness_control as sbc
from datetime import datetime

# -------------------------
# MOUSE ACTIONS
# -------------------------

def move_cursor(x, y):
    screen_width, screen_height = pyautogui.size()
    pyautogui.moveTo(int(x * screen_width), int(y * screen_height), duration=0.05)


def left_click():
    pyautogui.click()


def right_click():
    pyautogui.rightClick()


def double_click():
    pyautogui.doubleClick()


def scroll_up(amount=200):
    pyautogui.scroll(amount)


def scroll_down(amount=200):
    pyautogui.scroll(-amount)


# -------------------------
# APPLICATION ACTIONS
# -------------------------

def open_program(path):
    """
    Open any program using full path or program name
    Example:
    open_program("notepad.exe")
    open_program("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
    """
    try:
        subprocess.Popen(path)
        print(f"Opened program: {path}")
    except Exception as e:
        print("Error opening program:", e)


def open_website(url):
    """
    Open any website
    """
    try:
        webbrowser.open(url)
        print(f"Opened website: {url}")
    except Exception as e:
        print("Error opening website:", e)


# Backward compatibility (existing functions)
def open_chrome():
    open_program("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")


def open_notepad():
    open_program("notepad.exe")


def open_calculator():
    open_program("calc.exe")


# -------------------------
# SYSTEM ACTIONS
# -------------------------

def shutdown():
    os.system("shutdown /s /t 1")
    print("System shutting down")


def restart():
    os.system("shutdown /r /t 1")
    print("System restarting")


def close_app():
    pyautogui.hotkey('alt', 'f4')
    print("Closed active app")


def switch_app():
    pyautogui.hotkey('alt', 'tab')
    print("Switched app")


# -------------------------
# VOLUME CONTROL
# -------------------------

def volume_up(steps=1):
    for _ in range(steps):
        pyautogui.press("volumeup")
    print("Volume increased")


def volume_down(steps=1):
    for _ in range(steps):
        pyautogui.press("volumedown")
    print("Volume decreased")


def mute():
    pyautogui.press("volumemute")
    print("Volume muted")


# -------------------------
# BRIGHTNESS CONTROL
# -------------------------

def brightness_up(step=10):
    try:
        current = sbc.get_brightness()[0]
        sbc.set_brightness(min(100, current + step))
        print("Brightness increased")
    except:
        print("Brightness control not supported")


def brightness_down(step=10):
    try:
        current = sbc.get_brightness()[0]
        sbc.set_brightness(max(0, current - step))
        print("Brightness decreased")
    except:
        print("Brightness control not supported")


# -------------------------
# KEYBOARD ACTIONS
# -------------------------

def press_key(key):
    pyautogui.press(key)
    print(f"Pressed key: {key}")


def press_hotkey(*keys):
    pyautogui.hotkey(*keys)
    print(f"Pressed hotkey: {keys}")


# -------------------------
# SCREENSHOT
# -------------------------

def take_screenshot():
    folder = "screenshots"
    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/screenshot_{timestamp}.png"

    screenshot = pyautogui.screenshot()
    screenshot.save(filename)

    print(f"Screenshot saved: {filename}")


# -------------------------
# ACTION REGISTRY (CORE OF NEW SYSTEM)
# -------------------------

ACTION_REGISTRY = {

    # Mouse
    "move_cursor": move_cursor,
    "left_click": left_click,
    "right_click": right_click,
    "double_click": double_click,
    "scroll_up": scroll_up,
    "scroll_down": scroll_down,

    # Applications
    "open_program": open_program,
    "open_website": open_website,
    "open_chrome": open_chrome,
    "open_notepad": open_notepad,
    "open_calculator": open_calculator,

    # System
    "shutdown": shutdown,
    "restart": restart,
    "close_app": close_app,
    "switch_app": switch_app,

    # Volume
    "volume_up": volume_up,
    "volume_down": volume_down,
    "mute": mute,

    # Brightness
    "brightness_up": brightness_up,
    "brightness_down": brightness_down,

    # Keyboard
    "press_key": press_key,
    "press_hotkey": press_hotkey,

    # Screenshot
    "take_screenshot": take_screenshot,
}


# -------------------------
# EXECUTION ENGINE FUNCTION
# -------------------------

def execute_action(action_name, **kwargs):

    if action_name not in ACTION_REGISTRY:
        print(f"Unknown action: {action_name}")
        return

    action_function = ACTION_REGISTRY[action_name]

    try:
        # If parameters exist, use them
        if kwargs:
            action_function(**kwargs)
        else:
            action_function()

        print(f"Executed action: {action_name}")

    except Exception as e:
        print(f"Error executing action '{action_name}': {e}")

