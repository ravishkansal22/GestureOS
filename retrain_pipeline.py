import os

def retrain():

    print("Starting retraining pipeline...")

    os.system("python training/auto_collect.py")

    os.system("python training/train_model.py")

    print("Retraining completed.")

if __name__ == "__main__":
    retrain()
