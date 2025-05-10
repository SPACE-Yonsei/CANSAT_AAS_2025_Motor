#!/usr/bin/env python3
import time, math
import board, busio
from adafruit_bno055 import BNO055_I2C
from gpiozero import AngularServo

servo = None

def init_MG92B():
    global servo
    servo = AngularServo(
        18,
        min_angle=-90, max_angle=90,
        min_pulse_width=0.0005, max_pulse_width=0.0025,
        frame_width=0.005
    )

def terminate_MG92B():
    servo.detach()
    
def rotate_MG92B_ByYaw(yaw: float):
    yaw_turn =0

    if 90>yaw>=0:   #1
        servo_angle = yaw
    elif 180>yaw>=90:  #2
        servo_angle = -90
    elif 270>yaw>=180:  #3
        servo_angle = 90
    elif 360>=yaw>=270:   #4
        servo_angle = -(360-yaw)    

    servo.angle = servo_angle
    print(f"yaw={yaw:6.1f}°, servo→{servo_angle:5.1f}°")


# --------- BNO055 초기화 ------------
i2c    = busio.I2C(board.SCL, board.SDA)
sensor = BNO055_I2C(i2c)

# --------- 메인 루프 ------------
if __name__ == "__main__":
    init_MG92B()
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

            rotate_MG92B_ByYaw(heading)
            time.sleep(1.0)

    except KeyboardInterrupt:
        pass
    finally:
        terminate_MG92B()


