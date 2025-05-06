#### sudo apt install -y python3-gpiozero
#### #!/usr/bin/env python3 지우면 안됩니다

#!/usr/bin/env python3
from gpiozero import AngularServo
from time import sleep
import math, random


## Init Servo Motor

servo = None

max_revs = 2.0 #최대 회전 횟수 -> 꼬임 방지
prev_yaw = None    # 이전에 읽은 yaw
total_turns = 0.0

def init_MG92B():
    global servo

    servo = AngularServo(
        pin = 18,
        min_angle=-90,
        max_angle=90,
        min_pulse_width=0.0005,
        max_pulse_width=0.0025,
        frame_width=0.02
    )

def terminate_MG92B():
    global servo

    servo.detach()

def normalize_diff(angle):
    return (angle + 180) % 360 - 180

def rotate_MG92B_ByYaw(yaw:float):
    global servo
    global prev_yaw
    global total_turns
    
    if prev_yaw is None:
        prev_yaw = yaw

    delta = normalize_diff(yaw - prev_yaw)
    prev_yaw = yaw

    # Update total turns
    total_turns += delta / 360.0
    total_turns = max(-max_revs, min(max_revs, total_turns))

    raw_correction = - (yaw + total_turns * 360)

    corr = normalize_diff(raw_correction)
    corr = max(-90, min(90, corr))

    servo.angle = corr

    print(f"yaw={yaw:6.1f}°, Δ={delta:5.1f}°, turns={total_turns:5.2f}, servo→{corr:5.1f}°")