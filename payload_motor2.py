#### sudo apt install -y python3-gpiozero
#### #!/usr/bin/env python3 지우면 안됩니다

#!/usr/bin/env python3

#from gpiozero import AngularServo
#import math, random, time

import time

# Target Degree based on IMU
TARGET_DEGREE = 0

def init_MG92B():
    import pigpio
    pi = pigpio.pi()
    pin = 12
    pi.set_servo_pulsewidth(pin, 0)

    return pi, pin

def terminate_MG92B(pi):
    pi.stop()

def rotate_MG92B_ByYaw(pi, pin, yaw:float):

    yaw = (yaw+TARGET_DEGREE) % 360
        
    if 90 > yaw >= 0:   #1사분면    0~90 
        pi.set_servo_pulsewidth(pin, (yaw/180)*2000+500)
    elif 180> yaw >= 90:  #2사분면  
        pi.set_servo_pulsewidth(pin, 2500)
    elif 270 > yaw >= 180:  #3사분면  
        pi.set_servo_pulsewidth(pin, 500)
    elif 360 >= yaw >= 270:   #4사분면
        pi.set_servo_pulsewidth(pin, ((yaw-270)/180)*2000 + 500) 
    else:
        pass

    # The Servo angle range is -90 ~ 90, but adafruit servo library support 0 ~ 180, so apply the offset
    #print(f"yaw={yaw:6.1f}°, servo→{servo_angle:5.1f}°")

""""
import random
def get_yaw():
    return random.uniform(0, 360)
"""

if __name__ == "__main__":
    from adafruit_bno055 import BNO055_I2C
    import board, busio

    i2c    = busio.I2C(board.SCL, board.SDA)
    sensor = BNO055_I2C(i2c)

    pi, pin = init_MG92B()

    try:
        print("BNO055 + MG92B 보정 시작 (Ctrl+C 종료)")
        # 센서 워밍업
        time.sleep(0.5)
        while True:
            heading = sensor.euler[0]  # (heading, roll, pitch)
            if heading is None:
                # 아직 센서가 준비 안 됐으면 재시도
                time.sleep(0.1)
                continue

            rotate_MG92B_ByYaw(pi, pin, heading)
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass

    finally:
        terminate_MG92B(pi)
