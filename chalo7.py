import requests
import time
import math
import serial


# =====================================================
# MOONRAKER
# =====================================================

URL = "http://127.0.0.1:7125/printer/gcode/script"


# =====================================================
# ARDUINO SERIAL
# =====================================================

arduino = serial.Serial(
    '/dev/kinetic_pot',
    115200,
    timeout=0.01
)

time.sleep(2)


# =====================================================
# SEND GCODE
# =====================================================

def send_block(cmds):

    r = requests.post(
        URL,
        json={"script": "\n".join(cmds)}
    )

    print("STATUS:", r.status_code)


# =====================================================
# INIT
# =====================================================

send_block(["FIRMWARE_RESTART"])

time.sleep(3)

send_block([

    "SET_KINEMATIC_POSITION X=0 Y=0 Z=0",

    "G90",
    "G92 X0 Y0 Z0",

    # smoother motion
    "SET_VELOCITY_LIMIT VELOCITY=50",
    "SET_VELOCITY_LIMIT ACCEL=120",
    "SET_VELOCITY_LIMIT SQUARE_CORNER_VELOCITY=0.5",

    # enable motors
    "SET_STEPPER_ENABLE STEPPER=stepper_x ENABLE=1",
    "SET_STEPPER_ENABLE STEPPER=stepper_x1 ENABLE=1",
    "SET_STEPPER_ENABLE STEPPER=stepper_x2 ENABLE=1",

    "SET_STEPPER_ENABLE STEPPER=stepper_y ENABLE=1",
    "SET_STEPPER_ENABLE STEPPER=stepper_y1 ENABLE=1",
    "SET_STEPPER_ENABLE STEPPER=stepper_y2 ENABLE=1",

    "SET_STEPPER_ENABLE STEPPER=stepper_z ENABLE=1",
    "SET_STEPPER_ENABLE STEPPER=stepper_z1 ENABLE=1",
])

time.sleep(2)


# =====================================================
# MOTION PARAMETERS
# =====================================================

AMPLITUDE = 2.0

# faster waveform evolution
STEP = 0.003

# responsive live control
POINTS = 160

# low latency
CHUNK = 50

t = 0.0

feed = 400


# =====================================================
# MAIN LOOP
# =====================================================

while True:

    cmds = []

    for _ in range(POINTS):

        # =============================================
        # LIVE POT READ
        # =============================================

        try:

            while arduino.in_waiting:

                line = arduino.readline().decode().strip()

                if line:

                    pot = float(line)

                    normalized = pot / 1023.0

                    # lower overall speed range
                    target_feed = 50 + (normalized ** 2) * 1500

                    # smoother response
                    feed = feed * 0.90 + target_feed * 0.10

        except Exception as e:

            print("SERIAL ERROR:", e)

        print("FEED:", round(feed, 1))

        # =============================================
        # MOTION
        # =============================================

        wave = AMPLITUDE * math.sin(t)

        cmds.append(
            f"G1 X{wave:.4f} Y{wave:.4f} Z{wave:.4f} F{feed:.1f}"
        )

        t += STEP

        # =============================================
        # SEND CHUNK
        # =============================================

        if len(cmds) >= CHUNK:

            send_block(cmds)

            cmds = []

    if cmds:

        send_block(cmds)
