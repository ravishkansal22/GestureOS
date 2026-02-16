from controller.gesture_mapper import GestureMapper


class GestureManager:

    def __init__(self):
        self.mapper = GestureMapper()

    def show_menu(self):
        while True:

            print("\n===== GestureOS Manager =====")
            print("1. View Gestures")
            print("2. Add Gesture")
            print("3. Delete Gesture")
            print("4. Exit")

            choice = input("Enter choice: ")

            if choice == "1":
                self.view_gestures()

            elif choice == "2":
                self.add_gesture()

            elif choice == "3":
                self.delete_gesture()

            elif choice == "4":
                break

            else:
                print("Invalid choice")

    def view_gestures(self):

        gestures = self.mapper.list_gestures()

        if not gestures:
            print("No gestures found")
            return

        print("\nCurrent Gestures:")

        for gesture, action in gestures.items():
            print(f"{gesture}  →  {action}")

    def add_gesture(self):

        gesture_name = input("Enter new gesture name: ")
        action_name = input("Enter action name: ")

        self.mapper.add_gesture(gesture_name, action_name)

        print("Gesture added successfully")

    def delete_gesture(self):

        gesture_name = input("Enter gesture name to delete: ")

        self.mapper.delete_gesture(gesture_name)

        print("Gesture deleted successfully")
