from training.train_model import train
import main

def retrain(gesture_name):

    print("Starting training phase...")

    # 🔥 DO NOT stop engine
    # 🔥 DO NOT open camera
    # 🔥 DO NOT restart engine

    main.retrain_state["phase"] = "training"
    main.retrain_state["progress"] = 0

    train()

    main.retrain_state["progress"] = 90

    print("Reloading updated model...")
    main.reload_model()

    main.retrain_state["progress"] = 100
    main.retrain_state["phase"] = "done"

    print("Retraining completed successfully.")