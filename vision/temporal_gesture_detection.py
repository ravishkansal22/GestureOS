import time
import math


class TemporalGestureDetector:

    def __init__(self):

        self.reset()

        # Motion thresholds (tuned for webcam)
        self.start_threshold = 0.035   # must move this much to start swipe
        self.confirm_threshold = 0.18  # total distance to confirm swipe

        self.min_direction_consistency = 4  # frames in same direction

        self.cooldown = 1.2
        self.last_gesture_time = 0

    def reset(self):

        self.positions = []
        self.direction = None
        self.direction_count = 0

    def update(self, hand):

        if hand is None:
            self.reset()
            return None

        current_time = time.time()

        # cooldown protection
        if current_time - self.last_gesture_time < self.cooldown:
            return None

        x, y = hand.landmarks[0]

        self.positions.append((x, y))

        if len(self.positions) < 2:
            return None

        # check initial movement start
        start_x, start_y = self.positions[0]

        dx_total = x - start_x
        dy_total = y - start_y

        total_distance = math.sqrt(dx_total*dx_total + dy_total*dy_total)

        # must exceed start threshold first
        if total_distance < self.start_threshold:
            return None

        # determine frame direction
        prev_x, prev_y = self.positions[-2]

        dx = x - prev_x
        dy = y - prev_y

        abs_dx = abs(dx)
        abs_dy = abs(dy)

        if abs_dx > abs_dy:

            current_direction = "RIGHT" if dx > 0 else "LEFT"

        else:

            current_direction = "DOWN" if dy > 0 else "UP"

        # check consistency
        if self.direction is None:

            self.direction = current_direction
            self.direction_count = 1

        elif self.direction == current_direction:

            self.direction_count += 1

        else:

            # direction changed → reset detection
            self.reset()
            return None

        # must have consistent direction AND enough distance
        if (self.direction_count >= self.min_direction_consistency and
            total_distance >= self.confirm_threshold):

            gesture = f"LEFT_SWIPE_{self.direction}"

            print("Temporal gesture detected:", gesture)

            self.last_gesture_time = current_time
            self.reset()

            return gesture

        return None
