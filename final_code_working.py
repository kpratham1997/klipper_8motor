import requests
import time
import math

URL = "http://127.0.0.1:7125/printer/gcode/script"

def send_block(cmds):
    requests.post(URL, json={"script": "\n".join(cmds)})


# =========================
# INIT
# =========================
send_block(["FIRMWARE_RESTART"])
time.sleep(2)

send_block([
    "FAKE_HOME",   # kept (not needed but not removed)
    "G90",

    # 🔥 ensure motors are enabled
    "SET_STEPPER_ENABLE STEPPER=stepper_x ENABLE=1",
    "SET_STEPPER_ENABLE STEPPER=stepper_x1 ENABLE=1",
    "SET_STEPPER_ENABLE STEPPER=stepper_x2 ENABLE=1",

    "SET_STEPPER_ENABLE STEPPER=stepper_y ENABLE=1",
    "SET_STEPPER_ENABLE STEPPER=stepper_y1 ENABLE=1",
    "SET_STEPPER_ENABLE STEPPER=stepper_y2 ENABLE=1",

    "SET_STEPPER_ENABLE STEPPER=stepper_z ENABLE=1",
    "SET_STEPPER_ENABLE STEPPER=stepper_z1 ENABLE=1",
])

time.sleep(1)


# =========================
# PARAMETERS
# =========================
AMPLITUDE = 3
POINTS = 200
STEP = 0.03
FEED = 2500   # not used in FORCE_MOVE but kept

t = 0.0

# 🔥 REQUIRED for FORCE_MOVE
prev_x = 0.0
prev_y = 0.0
prev_z = 0.0


# =========================
# LOOP (CONTINUOUS STREAM)
# =========================
while True:
    cmds = []

    for i in range(POINTS):
        x = AMPLITUDE * math.sin(t)
        y = AMPLITUDE * math.sin(t + math.pi/2)
        z = AMPLITUDE * math.sin(t + math.pi)

        # 🔥 delta calculation (key change)
        dx = x - prev_x
        dy = y - prev_y
        dz = z - prev_z

        # 🔥 X axis (3 motors)
        cmds.append(f"FORCE_MOVE STEPPER=stepper_x DISTANCE={dx:.4f} VELOCITY=50")
        cmds.append(f"FORCE_MOVE STEPPER=stepper_x1 DISTANCE={dx:.4f} VELOCITY=50")
        cmds.append(f"FORCE_MOVE STEPPER=stepper_x2 DISTANCE={dx:.4f} VELOCITY=50")

        # 🔥 Y axis (3 motors)
        cmds.append(f"FORCE_MOVE STEPPER=stepper_y DISTANCE={dy:.4f} VELOCITY=50")
        cmds.append(f"FORCE_MOVE STEPPER=stepper_y1 DISTANCE={dy:.4f} VELOCITY=50")
        cmds.append(f"FORCE_MOVE STEPPER=stepper_y2 DISTANCE={dy:.4f} VELOCITY=50")

        # 🔥 Z axis (2 motors)
        cmds.append(f"FORCE_MOVE STEPPER=stepper_z DISTANCE={dz:.4f} VELOCITY=50")
        cmds.append(f"FORCE_MOVE STEPPER=stepper_z1 DISTANCE={dz:.4f} VELOCITY=50")

        # update previous
        prev_x = x
        prev_y = y
        prev_z = z

        t += STEP

    send_block(cmds)

    time.sleep(0.02)
