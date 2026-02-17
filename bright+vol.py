import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

gesture_mapping = {
    "index_up": "volume"
}

while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    action_text = ""

    if results.multi_hand_landmarks and results.multi_handedness:

        for handLms, handedness in zip(results.multi_hand_landmarks,
                                        results.multi_handedness):

            # Detect ONLY LEFT hand internally
            label = handedness.classification[0].label
            if label != "Left":
                continue

            mp_draw.draw_landmarks(frame, handLms,
                                   mp_hands.HAND_CONNECTIONS)

            index_tip = handLms.landmark[8]
            index_pip = handLms.landmark[6]

            middle_tip = handLms.landmark[12]
            ring_tip = handLms.landmark[16]
            pinky_tip = handLms.landmark[20]

            middle_pip = handLms.landmark[10]
            ring_pip = handLms.landmark[14]
            pinky_pip = handLms.landmark[18]

            index_straight = abs(index_tip.y - index_pip.y) > 0.08
            middle_folded = middle_tip.y > middle_pip.y
            ring_folded = ring_tip.y > ring_pip.y
            pinky_folded = pinky_tip.y > pinky_pip.y

            if index_straight and middle_folded and ring_folded and pinky_folded:

                if index_tip.y < index_pip.y:

                    task = gesture_mapping["index_up"]

                    if task == "volume":
                        action_text = "VOLUME UP"

                    elif task == "brightness":
                        action_text = "BRIGHTNESS UP"

    # Display Current Mode (without mentioning left hand)
    cv2.putText(frame,
                f"Mode: {gesture_mapping['index_up'].upper()}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2)

    if action_text:
        cv2.putText(frame,
                    action_text,
                    (200, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    (0, 0, 255),
                    3)

    cv2.imshow("GestureOS", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('1'):
        gesture_mapping["index_up"] = "volume"

    elif key == ord('2'):
        gesture_mapping["index_up"] = "brightness"

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
