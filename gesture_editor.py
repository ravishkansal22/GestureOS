import json
import os
import subprocess
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = "data/gesture_action_map.json"


def load_config():

    if not os.path.exists(CONFIG_PATH):
        return {}

    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(config):

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)


def retrain_model():

    print("\nStarting automatic training...")

    auto_collect_path = os.path.join(BASE_DIR, "training", "auto_collect.py")
    train_model_path = os.path.join(BASE_DIR, "training", "train_model.py")

    subprocess.run(["python", auto_collect_path])

    subprocess.run(["python", train_model_path])

    print("Training complete. GestureOS updated.")



def add_gesture():

    config = load_config()

    gesture = input("Enter new gesture name: ").strip().upper()

    if gesture in config:

        print("Gesture already exists.")
        return

    action = input("Enter action to assign: ").strip()

    config[gesture] = action

    save_config(config)

    print(f"\nGesture '{gesture}' added.")

    # Automatically retrain
    retrain_model()


def edit_gesture():

    import pandas as pd

    config = load_config()

    old_gesture = input("Enter gesture name to edit: ").strip().upper()

    if old_gesture not in config:

        print("Gesture not found.")
        return

    print("\nWhat do you want to edit?")
    print("1. Change action only")
    print("2. Rename gesture completely")

    choice = input("Enter choice: ")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(BASE_DIR, "data", "dataset.csv")

    # OPTION 1: Change action only
    if choice == "1":

        new_action = input("Enter new action: ").strip()

        config[old_gesture] = new_action

        save_config(config)

        print("Action updated successfully.")

        return

    # OPTION 2: Rename gesture
    elif choice == "2":

        new_gesture = input("Enter new gesture name: ").strip().upper()

        if new_gesture in config:

            print("Gesture already exists.")
            return

        # Update mapping
        config[new_gesture] = config.pop(old_gesture)

        save_config(config)

        print("Gesture renamed in mapping.")

        # Update dataset.csv
        if os.path.exists(dataset_path):

            df = pd.read_csv(dataset_path, header=None)

            count = (df.iloc[:, -1] == old_gesture).sum()

            df.iloc[:, -1] = df.iloc[:, -1].replace(old_gesture, new_gesture)

            df.to_csv(dataset_path, header=False, index=False)

            print(f"Updated {count} samples in dataset.")

        else:

            print("dataset.csv not found.")

        # Retrain model
        print("\nRetraining model after edit...")

        train_model_path = os.path.join(BASE_DIR, "training", "train_model.py")

        subprocess.run(["python", train_model_path])

        print("Gesture edit complete and model updated.")

    else:

        print("Invalid choice.")



def delete_gesture():

    import pandas as pd

    config = load_config()

    gesture = input("Enter gesture to delete: ").strip().upper()

    # Step 1: Remove from mapping
    if gesture in config:

        del config[gesture]

        save_config(config)

        print(f"{gesture} removed from gesture_action_map.json")

    else:

        print("Gesture not found in mapping.")

    # Step 2: Remove from dataset.csv
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(BASE_DIR, "data", "dataset.csv")

    if os.path.exists(dataset_path):

        df = pd.read_csv(dataset_path, header=None)

        original_count = len(df)

        df = df[df.iloc[:, -1] != gesture]

        new_count = len(df)

        df.to_csv(dataset_path, header=False, index=False)

        print(f"Removed {original_count - new_count} samples from dataset.")

    else:

        print("dataset.csv not found.")

    # Step 3: Retrain model automatically
    print("\nRetraining model after deletion...")

    train_model_path = os.path.join(BASE_DIR, "training", "train_model.py")

    subprocess.run(["python", train_model_path])

    print(f"{gesture} completely removed from GestureOS.")



def menu():

    while True:

        print("\n==== GestureOS Editor ====")
        print("1. Add Gesture (Auto Train)")
        print("2. Edit Gesture")
        print("3. Delete Gesture")
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            add_gesture()

        elif choice == "2":
            edit_gesture()

        elif choice == "3":
            delete_gesture()

        elif choice == "4":
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()
