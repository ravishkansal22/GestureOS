import pyautogui

# Make movement smooth and safe
pyautogui.FAILSAFE = False

def move_cursor(x, y):
    """
    Move cursor to given screen coordinates
    """
    screen_width, screen_height = pyautogui.size()

    target_x = int(x * screen_width)
    target_y = int(y * screen_height)

    pyautogui.moveTo(target_x, target_y, duration=0.05)


def left_click():
    """
    Perform left mouse click
    """
    pyautogui.click()


def right_click():
    """
    Perform right mouse click
    """
    pyautogui.rightClick()


def double_click():
    """
    Perform double click
    """
    pyautogui.doubleClick()
