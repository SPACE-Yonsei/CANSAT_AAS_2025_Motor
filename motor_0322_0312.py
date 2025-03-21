from gpiozero import Servo
from time import sleep

# 서보 핀 (GPIO 번호 기준, 예: GPIO 17번 → physical pin 11)
servo = Servo(17)

# 기본적으로 -1.0 ~ 1.0 사이의 값으로 제어
# 180도 → 1.0, 0도 → -1.0 으로 간주

current_angle = 1.0  # 시작은 180도 위치

try:
    while True:
        # 각도 전환
        if current_angle == 1.0:
            current_angle = -1.0  # 0도
        else:
            current_angle = 1.0   # 180도

        servo.value = current_angle
        print(f"Moved to angle: {'180' if current_angle == 1.0 else '0'} degrees")
        sleep(1)

except KeyboardInterrupt:
    print("서보 제어 종료")
