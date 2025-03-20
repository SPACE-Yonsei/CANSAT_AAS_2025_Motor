import time
import math
import board
import busio
import adafruit_bno055
import RPi.GPIO as GPIO

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bno055.BNO055_I2C(i2c)

while sensor.euler[0] is None:  #센서값 들어올 때까지 가만히 있어요.
    time.sleep(0.1)

raw_yaw = sensor.euler[0]
unwrapped_angle = raw_yaw  #초기 센서값 읽기.
old_angle = raw_yaw #얘도 마찬가지.
print(f"초기 센서 yaw: {raw_yaw:6.2f}°")

SERVO_PIN = 32
SERVO_FREQ = 50  # 50Hz, 20ms 주기

#보정값.
SERVO_MIN_DUTY = 2.5    # 0°에 해당하는 duty
SERVO_MAX_DUTY = 12.5   # 180°에 해당하는 duty

GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, SERVO_FREQ)

# 서보의 중립(정지) 상태를 90°로 정의
neutral_angle = 90.0
neutral_duty = SERVO_MIN_DUTY + (neutral_angle / 180.0) * (SERVO_MAX_DUTY - SERVO_MIN_DUTY)
pwm.start(neutral_duty)
print(f"서보 초기화: 중립(90°), Duty = {neutral_duty:.2f}%")

def set_servo(angle): #실제로 서보를 돌리는 친구이다. 선형 짝짓기.
    angle = max(0, min(180, angle))
    duty = SERVO_MIN_DUTY + (angle / 180.0) * (SERVO_MAX_DUTY - SERVO_MIN_DUTY)
    pwm.ChangeDutyCycle(duty)
    print(f"명령 각도: {angle:6.2f}°, Duty: {duty:6.2f}%")

def combined_map(new_angle, old_angle, unwrapped_angle):
    """
    new_angle: 새 센서 yaw (0~360°)
    old_angle: 이전 센서 yaw (0~360°)
    unwrapped_angle: 이전 누적 회전량 (°)
    
    1. 최소각 차이를 계산하여 unwrapped_angle 업데이트
    2. 카메라가 북쪽(0°)을 유지하기 위한 보상 각도 = -unwrapped_angle 계산
    3. 보상 각도를 MG92B 서보의 명령 각도(0~180°)로 선형 매핑 (1/12 스케일: -1080°→0°, 0→90°, +1080°→180°)
    """
    # 최소각 차이 (-180° ~ +180°)
    diff = (new_angle - old_angle + 180) % 360 - 180
    updated_unwrapped = unwrapped_angle + diff
    # 한 방향으로 3회(1080°) 이상 회전하지 않도록
    if updated_unwrapped > 1080:
        updated_unwrapped = 1080
    elif updated_unwrapped < -1080:
        updated_unwrapped = -1080

    # 보상 각도: 카메라가 북쪽을 유지하도록 하기 위해 모터는 -unwrapped_angle만큼 회전
    desired_motor_angle = -updated_unwrapped
    # 선형 매핑: 1/12 스케일 적용 → 90 + (desired_motor_angle/12)
    commanded_servo_angle = 90 + (desired_motor_angle / 12.0)
    # 0°~180° 범위로 클램핑
    commanded_servo_angle = max(0, min(180, commanded_servo_angle))
    return commanded_servo_angle, updated_unwrapped

# ---------------------------
# 메인 제어 루프 (0.1초 주기)
# ---------------------------
try:
    while True:
        current_raw = sensor.euler[0]
        if current_raw is None:
            time.sleep(0.1)
            continue

        # combined_map 함수를 통해 새로운 서보 명령 각도와 업데이트된 unwrapped_angle 계산
        commanded_angle, unwrapped_angle = combined_map(current_raw, old_angle, unwrapped_angle)
        old_angle = current_raw  # 현재 센서 값을 이전 값으로 업데이트

        # 계산된 명령 각도로 서보 제어
        set_servo(commanded_angle)

        # 0.1초 주기로 갱신
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n프로그램 종료")

finally:
    pwm.stop()
    GPIO.cleanup()
