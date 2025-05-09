"""

sudo apt install -y python3-pip python3-smbus
sudo python3 -m pip install --break-system-packages adafruit-blinka
pip install adafruit-blinka adafruit-circuitpython-bno055 gpiozero
sudo python3 -m pip install --break-system-packages \
  adafruit-blinka adafruit-circuitpython-bno055
  """

#!/usr/bin/env python3
import time, math
import board, busio
#from adafruit_bno055 import BNO055_I2C
from gpiozero import AngularServo

# --------- 서보 설정 ------------
servo = None
max_revs   = 2.0     # 최대 꼬임 방지 회전수
prev_yaw   = None    # 이전 yaw
total_turns= 0.0     # 누적 회전수

def init_MG92B():
    global servo
    servo = AngularServo(
        18,
        min_angle=-90, max_angle=90,
        min_pulse_width=0.0005, max_pulse_width=0.0025,
        frame_width=0.02
    )

def terminate_MG92B():
    global servo
    servo.detach()

def normalize_diff(angle):
    global servo
    
    """360° 순환 차이를 –180~+180 사이로 변환"""
    return (angle + 180) % 360 - 180

def rotate_MG92B_ByYaw(yaw: float):
    """주어진 절대 yaw(0~360) 기준으로 서보 각도 보정"""
    global prev_yaw, total_turns
    global servo

    if prev_yaw is None:
        prev_yaw = yaw

    # Δyaw → –180~+180
    delta = normalize_diff(yaw - prev_yaw)
    prev_yaw = yaw

    # 샤프트 회전수 누적 & 클램프
    total_turns += delta / 360.0
    total_turns  = max(-max_revs, min(max_revs, total_turns))

    # 보정할 절대 각도 계산
    raw = - (yaw + total_turns * 360)
    corr= normalize_diff(raw)
    # 서보 물리 한계 ±90° 클램프
    corr= max(-90, min(90, corr))

    servo.angle = corr
    print(f"yaw={yaw:6.1f}°, Δ={delta:5.1f}°, turns={total_turns:5.2f}, servo→{corr:5.1f}°")


"""
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
"""