#### sudo apt install -y python3-gpiozero
#### #!/usr/bin/env python3 지우면 안됩니다

#!/usr/bin/env python3

#from gpiozero import AngularServo
#import math, random, time

import math, random, time

# Target Degree based on IMU
TARGET_DEGREE = 0

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

    yaw = (yaw-TARGET_DEGREE) % 360
        
    if 90>yaw+TARGET_DEGREE >= 0+TARGET_DEGREE:   #1사분면    0~90 
        servo_angle = yaw
    elif 180+TARGET_DEGREE > yaw >= 90+TARGET_DEGREE:  #2사분면  
        servo_angle = 85
    elif 270+TARGET_DEGREE > yaw >= 180+TARGET_DEGREE:  #3사분면  
        servo_angle = -85
    elif 360+TARGET_DEGREE >= yaw >= 270+TARGET_DEGREE:   #4사분면
        servo_angle = -(360-yaw)    
    else:
        pass

    # The Servo angle range is -90 ~ 90, but adafruit servo library support 0 ~ 180, so apply the offset
    servo_angle = servo_angle + 90

    mg92b_servo.angle = servo_angle
    print(f"yaw={yaw:6.1f}°, servo→{servo_angle:5.1f}°")


def get_yaw():
    return random.uniform(0, 360)

if __name__ == "__main__":
    from adafruit_bno055 import BNO055_I2C
    import board, busio

    i2c    = busio.I2C(board.SCL, board.SDA)
    sensor = BNO055_I2C(i2c)

    motor_instance, pwm_instance = init_MG92B()

    try:
        print("BNO055 + MG92B 보정 시작 (Ctrl+C 종료)")
        # 센서 워밍업
        time.sleep(1)
        while True:
            heading = sensor.euler[0]  # (heading, roll, pitch)
            if heading is None:
                # 아직 센서가 준비 안 됐으면 재시도
                time.sleep(0.1)
                continue

            rotate_MG92B_ByYaw(motor_instance, heading)
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass

    finally:
        terminate_MG92B(pwm_instance)