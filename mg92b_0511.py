## 목표 각도 설정 기능 추가

#!/usr/bin/env python3
import time, math
import board, busio
from adafruit_bno055 import BNO055_I2C
from gpiozero import AngularServo

servo = None


target = 0  # IMU 기준으로 목표는 시계방향 몇도? / 0511 추가


# MG92b 시작
def init_MG92B():
    global servo
    servo = AngularServo(
        18,
        min_angle=-90, max_angle=90,
        min_pulse_width=0.0005, max_pulse_width=0.0025,
        frame_width=0.005
    )

# MG92b 시작 종류
def terminate_MG92B():
    servo.detach()


# MG92b 회전전
def rotate_MG92B_ByYaw(yaw: float):
    yaw = (yaw-target) % 360
        
    if 90>yaw+target >= 0+target:   #1사분면    0~90 
        servo_angle = yaw
    elif 180+target > yaw >= 90+target:  #2사분면  
        servo_angle = 85
    elif 270+target > yaw >= 180+target:  #3사분면  
        servo_angle = -85
    elif 360+target >= yaw >= 270+target:   #4사분면
        servo_angle = -(360-yaw)    
    else:
        pass

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
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        terminate_MG92B()
