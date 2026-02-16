import time
from controller.system_controller import SystemController
from controller.gesture_mapper import GestureMapper



mapper = GestureMapper()

def simulated_gesture_input():

    # Reload latest gestures
    mapper.load_mapping()

    gestures = mapper.list_gestures()

    print("\nAvailable gestures:")

    for gesture in gestures:
        print(gesture)

    print("EXIT")

    gesture = input("\nEnter gesture: ")

    if gesture == "MOVE_CURSOR":
        x = float(input("Enter X (0–1): "))
        y = float(input("Enter Y (0–1): "))
        return gesture, x, y

    return gesture, None, None


def main():

    controller = SystemController()

    print("GestureOS Started")

    while True:

        gesture_name, x, y = simulated_gesture_input()

        if gesture_name == "EXIT":
            print("Exiting GestureOS")
            break

        controller.execute_action(gesture_name, x, y)

        time.sleep(0.1)


if __name__ == "__main__":
    main()
