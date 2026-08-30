import pyautogui

pyautogui.FAILSAFE = False

# pyautogui inserts a 0.1s sleep after EVERY call by default (PAUSE).
# move_cursor() below runs on every single camera frame the right hand
# is visible (~30x/sec) in the same thread that also does frame capture
# and hand tracking — at the default PAUSE, that throttles the whole
# engine loop to a few frames per second and makes the real OS cursor
# (and the rest of the app) appear to freeze while a hand is on screen.
pyautogui.PAUSE = 0


# =========================
# CLASS VERSION (for GestureOS engine)
# =========================

class CursorController:

    def __init__(self):

        self.screen_width, self.screen_height = pyautogui.size()
        self.dragging = False

        # Without damping, the raw fingertip position drives the real OS
        # cursor 1:1 on every camera frame (~30x/sec) with no smoothing,
        # which reads as violent/uncontrollable jitter rather than
        # deliberate movement. smoothed_x/y track an exponential moving
        # average of the target position; move_deadzone_px skips moves
        # too small to be an intentional gesture.
        self._smoothed_x = None
        self._smoothed_y = None
        self._last_sent = None
        self.smoothing = 0.5
        self.move_deadzone_px = 3


    def move_cursor(self, x, y, frame_width, frame_height):

        target_x = (x / frame_width) * self.screen_width
        target_y = (y / frame_height) * self.screen_height

        if self._smoothed_x is None:
            self._smoothed_x, self._smoothed_y = target_x, target_y
        else:
            self._smoothed_x += (target_x - self._smoothed_x) * (1 - self.smoothing)
            self._smoothed_y += (target_y - self._smoothed_y) * (1 - self.smoothing)

        screen_x = int(self._smoothed_x)
        screen_y = int(self._smoothed_y)

        if self._last_sent is not None:
            last_x, last_y = self._last_sent
            if (
                abs(screen_x - last_x) < self.move_deadzone_px
                and abs(screen_y - last_y) < self.move_deadzone_px
            ):
                return

        self._last_sent = (screen_x, screen_y)
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
