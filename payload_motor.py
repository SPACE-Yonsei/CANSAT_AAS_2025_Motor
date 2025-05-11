#### sudo apt install -y python3-gpiozero
#### #!/usr/bin/env python3 지우면 안됩니다

#!/usr/bin/env python3

#from gpiozero import AngularServo
#import math, random, time

import math, random, time

max_revs = 2.0 #최대 회전 횟수 -> 꼬임 방지
prev_yaw = None    # 이전에 읽은 yaw
total_turns = 0.0

def init_MG92B():
    import board
    import pwmio
    from adafruit_motor import servo

    pwm = pwmio.PWMOut(board.D12, frequency=50)

    mg92b_servo = servo.Servo(
        pwm,
        min_pulse=500,    # microseconds
        max_pulse=2500,   # microseconds
        actuation_range=180
    )
    
    return mg92b_servo, pwm

def terminate_MG92B(pwm):
    pwm.deinit()

def normalize_diff(angle):
    return (angle + 180) % 360 - 180

def rotate_MG92B_ByYaw(mg92b_servo, yaw:float):
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

    # 90 degree is added because the angle range is 0 ~ 180 degree
    mg92b_servo.angle = corr + 90

    #print(f"yaw={yaw:6.1f}°, Δ={delta:5.1f}°, turns={total_turns:5.2f}, servo→{corr:5.1f}°")

def get_yaw():
    return random.uniform(0, 360)

if __name__ == "__main__":
    motor_instance, pwm_instance = init_MG92B()

    try:
        while True:
            yaw = get_yaw()
            rotate_MG92B_ByYaw(motor_instance, yaw)
            time.sleep(1)

    except KeyboardInterrupt:
        terminate_MG92B(pwm_instance)