import time
from controller.action_engine import ActionEngine
from controller.gesture_mapper import GestureMapper


# Initialize components
mapper = GestureMapper()
engine = ActionEngine()


def simulated_gesture_input():

    # Reload latest gesture mapping
    mapper.load_mapping()

    gestures = mapper.list_gestures()

    print("\nAvailable gestures:")
    for gesture in gestures:
        print("-", gesture)

    print("- EXIT")

    gesture = input("\nEnter gesture: ").strip()

    if gesture == "MOVE_CURSOR":

        try:
            x = float(input("Enter X (0–1): "))
            y = float(input("Enter Y (0–1): "))
            return gesture, {"x": x, "y": y}
        except:
            print("Invalid coordinates")
            return None, None

    return gesture, None


def main():

    print("=====================================")
    print("      GestureOS Started")
    print("      Dynamic Action System Enabled")
    print("=====================================")

    while True:

        gesture_name, params = simulated_gesture_input()

        if gesture_name == "EXIT":
            print("Exiting GestureOS")
            break

        if gesture_name is None:
            continue

        try:
            # Execute action using new ActionEngine
            engine.execute(gesture_name, params)

        except Exception as e:
            print("Execution error:", e)

        time.sleep(0.1)


if __name__ == "__main__":
    main()
