import time
import math


class MouseGestureDetector:

    def __init__(self):

        self.PINCH_THRESHOLD = 35

        # Click / drag timing
        self.pinch_start_time = None
        self.drag_threshold_time = 0.5
        self.is_dragging = False

        # Scroll tracking
        self.prev_scroll_y = None
        self.scroll_mode = False
        self.SCROLL_SENSITIVITY = 3


    # =========================
    # Utility functions
    # =========================

    def distance(self, p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


    def is_finger_up(self, tip, pip):
        return tip[1] < pip[1]


    def reset_states(self):

        self.pinch_start_time = None
        self.is_dragging = False
        self.prev_scroll_y = None
        self.scroll_mode = False


    # =========================
    # Main detection function
    # =========================

    def detect(self, hand_data_list):

        if not hand_data_list:

            self.reset_states()

            return {
                "gesture": "NONE",
                "position": None,
                "scroll": 0
            }

        hand = None

        for h in hand_data_list:
            if h.hand_label == "Right":
                hand = h
                break

        if hand is None:
            return {
                "gesture": "NONE",
                "position": None,
                "scroll": 0
            }


        lm = hand.landmarks

        index_tip = lm[8]
        index_pip = lm[6]

        middle_tip = lm[12]
        middle_pip = lm[10]

        ring_tip = lm[16]
        ring_pip = lm[14]

        pinky_tip = lm[20]
        pinky_pip = lm[18]

        thumb_tip = lm[4]

        index_pos = index_tip

        pinch_distance = self.distance(index_tip, thumb_tip)

        current_time = time.time()

        # =========================
        # SCROLL MODE DETECTION
        # =========================

        index_up = self.is_finger_up(index_tip, index_pip)
        middle_up = self.is_finger_up(middle_tip, middle_pip)
        ring_down = not self.is_finger_up(ring_tip, ring_pip)
        pinky_down = not self.is_finger_up(pinky_tip, pinky_pip)

        if index_up and middle_up and ring_down and pinky_down:

            self.scroll_mode = True

            current_y = middle_tip[1]

            if self.prev_scroll_y is not None:

                dy = self.prev_scroll_y - current_y

                if abs(dy) > 8:

                    scroll_amount = int(dy / self.SCROLL_SENSITIVITY)

                    self.prev_scroll_y = current_y

                    return {
                        "gesture": "SCROLL",
                        "position": index_pos,
                        "scroll": scroll_amount
                    }

            self.prev_scroll_y = current_y

            return {
                "gesture": "SCROLL_IDLE",
                "position": index_pos,
                "scroll": 0
            }

        else:

            self.scroll_mode = False
            self.prev_scroll_y = None

        # =========================
        # CLICK / DRAG DETECTION
        # =========================

        if pinch_distance < self.PINCH_THRESHOLD:

            if self.pinch_start_time is None:
                self.pinch_start_time = current_time

            pinch_duration = current_time - self.pinch_start_time

            if pinch_duration > self.drag_threshold_time:

                self.is_dragging = True

                return {
                    "gesture": "DRAG",
                    "position": index_pos,
                    "scroll": 0
                }

        else:

            if self.pinch_start_time is not None:

                pinch_duration = current_time - self.pinch_start_time

                self.pinch_start_time = None

                if pinch_duration < self.drag_threshold_time:

                    return {
                        "gesture": "LEFT_CLICK",
                        "position": index_pos,
                        "scroll": 0
                    }

                if self.is_dragging:

                    self.is_dragging = False

                    return {
                        "gesture": "DRAG_END",
                        "position": index_pos,
                        "scroll": 0
                    }

        # =========================
        # RIGHT CLICK
        # =========================

        index_middle_dist = self.distance(index_tip, middle_tip)

        if index_middle_dist < self.PINCH_THRESHOLD:

            return {
                "gesture": "RIGHT_CLICK",
                "position": index_pos,
                "scroll": 0
            }

        # =========================
        # DEFAULT MOVE
        # =========================

        return {
            "gesture": "MOVE_CURSOR",
            "position": index_pos,
            "scroll": 0
        }
