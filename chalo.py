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
    "FAKE_HOME",
    "G90"
])

time.sleep(1)


# =========================
# PARAMETERS
# =========================
AMPLITUDE = 10
POINTS = 120
STEP = 0.05
FEED = 3000

t = 0.0


# =========================
# LOOP
# =========================
while True:
    cmds = []

    # 🔥 ALWAYS ensure homed before motion
    cmds.append("FAKE_HOME")

    for i in range(POINTS):
        x = AMPLITUDE * math.sin(t)
        y = AMPLITUDE * math.sin(t + math.pi/2)
        z = AMPLITUDE * math.sin(t + math.pi)

        cmds.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} F{FEED}")

        t += STEP

    send_block(cmds)

    time.sleep(0.05)
