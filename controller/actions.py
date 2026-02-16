import pyautogui
import subprocess
import os
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from datetime import datetime


def move_cursor(x, y):
    screen_width, screen_height = pyautogui.size()
    pyautogui.moveTo(int(x * screen_width), int(y * screen_height), duration=0.05)


def left_click():
    pyautogui.click()


def right_click():
    pyautogui.rightClick()


def double_click():
    pyautogui.doubleClick()


# Scroll actions
def scroll_up():
    pyautogui.scroll(200)


def scroll_down():
    pyautogui.scroll(-200)


# Application actions
def open_chrome():
    subprocess.Popen("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")


def open_notepad():
    subprocess.Popen("notepad.exe")


def open_calculator():
    subprocess.Popen("calc.exe")


# System actions
def shutdown():
    os.system("shutdown /s /t 1")


def restart():
    os.system("shutdown /r /t 1")

def volume_up():
    pyautogui.press("volumeup")
    print("Volume Up")


def volume_down():
    pyautogui.press("volumedown")
    print("Volume Down")

def brightness_up():
    current = sbc.get_brightness()[0]
    sbc.set_brightness(min(100, current + 10))

def brightness_down():
    current = sbc.get_brightness()[0]
    sbc.set_brightness(max(0, current - 10))

def switch_app():
    import pyautogui
    pyautogui.hotkey('alt', 'tab')

def take_screenshot():
    folder = "screenshots"
    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/screenshot_{timestamp}.png"

    screenshot = pyautogui.screenshot()
    screenshot.save(filename)

    print(f"Screenshot saved: {filename}")

def close_app():
    pyautogui.hotkey('alt', 'f4')
    print("Closed active app")