import pyautogui

pyautogui.FAILSAFE = False


# =========================
# CLASS VERSION (for GestureOS engine)
# =========================

class CursorController:

    def __init__(self):

        self.screen_width, self.screen_height = pyautogui.size()
        self.dragging = False


    def move_cursor(self, x, y, frame_width, frame_height):

        screen_x = int((x / frame_width) * self.screen_width)
        screen_y = int((y / frame_height) * self.screen_height)

        pyautogui.moveTo(screen_x, screen_y, duration=0)


    def left_click(self):

        pyautogui.click()


    def right_click(self):

        pyautogui.rightClick()


    def double_click(self):

        pyautogui.doubleClick()


    def drag(self, x, y, frame_width, frame_height):

        screen_x = int((x / frame_width) * self.screen_width)
        screen_y = int((y / frame_height) * self.screen_height)

        if not self.dragging:

            pyautogui.mouseDown()
            self.dragging = True

        pyautogui.moveTo(screen_x, screen_y, duration=0)


    def drag_end(self):

        if self.dragging:

            pyautogui.mouseUp()
            self.dragging = False


    def scroll(self, amount):

        pyautogui.scroll(amount)


# =========================
# FUNCTION VERSION (legacy compatibility)
# =========================

_screen_width, _screen_height = pyautogui.size()


def move_cursor(x, y):

    target_x = int(x * _screen_width)
    target_y = int(y * _screen_height)

    pyautogui.moveTo(target_x, target_y, duration=0.05)


def left_click():

    pyautogui.click()


def right_click():

    pyautogui.rightClick()


def double_click():

    pyautogui.doubleClick()


def scroll(amount):

    pyautogui.scroll(amount)
