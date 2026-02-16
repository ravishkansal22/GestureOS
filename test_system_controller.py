import time
from controller.system_controller import SystemController

controller = SystemController()

print("Testing in 3 seconds...")
time.sleep(3)

controller.execute_action("MOVE_CURSOR", 0.5, 0.5)

time.sleep(1)

controller.execute_action("LEFT_CLICK")

print("Test complete")
