import time
import math
import RPi.GPIO as GPIO
import board
import busio

SERVO_PIN = 12
servo = None

def motor_init():
    global servo
    global current_servo_angle

    # 경고 메시지를 끄면 이전 실행에서 설정된 핀의 상태로 인해 발생하는 경고를 무시할 수 있습니다.
    GPIO.setwarnings(False)

    # BCM(브로드컴) 핀 번호 체계를 사용하여 핀 번호를 지정합니다.
    GPIO.setmode(GPIO.BCM)

    # 서보 모터 제어를 위한 핀 설정 (여기서는 GPIO 18번 사용)
    GPIO.setup(SERVO_PIN, GPIO.OUT)   # 서보 모터를 출력 모드로 설정

    # 50Hz PWM 신호 생성: 서보 모터의 기본 동작 주기는 약 20ms(50Hz)입니다.
    servo = GPIO.PWM(SERVO_PIN, 50)
    # 초기 듀티 사이클을 7.5%로 설정하면, 대부분의 서보 모터는 중앙(약 90°) 위치에 놓입니다.
    servo.start(ROCKET_MIDDLE)

    # 현재 서보 모터의 각도를 저장할 변수 (단위: 도)
    # 여기서는 카메라가 북쪽을 바라보도록 0도로 초기화합니다.
    current_servo_angle = 0
        
def motor_terminate():
    servo.stop()
    GPIO.cleanup()
    return

"""
현재 각도(current)와 목표 각도(target) 사이의 최소 회전 차이를 계산합니다.
이 함수는 두 각도 간의 차이를 -180°에서 +180° 범위로 반환하여,
예를 들어 10°와 350°의 차이를 -20°로 계산해 불필요한 340° 회전을 피하도록 합니다.

매개변수:
    target  - 목표 각도 (도)
    current - 현재 각도 (도)

반환값:
    두 각도 사이의 최소 회전 차이 (도)
"""
def minimal_angle_diff(target, current):
    diff = target - current
    # (diff + 180)를 360으로 나눈 나머지에서 180을 빼면 -180° ~ +180° 범위가 됩니다.
    diff = (diff + 180) % 360 - 180
    return diff



"""
서보 모터의 각도(도)를 PWM 듀티 사이클(%)로 변환합니다.
MG92B 서보 모터는 일반적으로 0°에 약 2.5%, 180°에 약 12.5%의 듀티 사이클로 동작합니다.

본 예제에서는 서보 모터의 동작 범위를 -90° ~ +90°로 가정하고,
이를 0° ~ 180° 범위로 매핑한 후 선형적으로 듀티 사이클을 계산합니다.

변환 과정:
    1. 주어진 각도(angle, -90°~+90°)에 90을 더해 0°~180° 범위로 만듭니다.
    2. 0°일 때 듀티 사이클이 2.5%, 180°일 때 12.5%가 되도록 선형 변환합니다.

매개변수:
    angle - 서보 모터의 각도 (도, -90° ~ +90°)

반환값:
    해당 각도에 대응하는 PWM 듀티 사이클 (%)
"""
def angle_to_duty_cycle(angle):
    mapped_angle = angle + 90   # 예: -90° → 0°, +90° → 180°
    # 선형 매핑: 0°에 2.5%, 180°에 12.5% → 듀티 사이클 변화 범위는 10%
    duty_cycle = 2.5 + (mapped_angle / 180.0) * 10
    return duty_cycle


"""
기체의 현재 heading(0°~360°)을 이용하여 카메라(서보 모터)가 항상 북쪽(0°)을 바라보도록 
목표 서보 각도를 계산합니다.

원리:
    - 기체가 heading을 향하고 있을 때, 카메라는 반대 방향으로 회전해야 북쪽을 바라볼 수 있습니다.
    - 예를 들어, 기체의 heading이 90°라면, 카메라는 -90° (또는 +270°)를 취해야 합니다.
    - 그러나 서보 모터의 물리적 한계는 -90° ~ +90°이므로, 이 범위 내에서 최소 회전 경로를 선택합니다.

계산 방법:
    - 만약 heading이 0°~180°이면, 목표 서보 각도 = -heading
    - 만약 heading이 180° 초과이면, 목표 서보 각도 = 360 - heading
    (예: heading이 270°이면, 360 - 270 = 90°)

매개변수:
    heading - BNO055 센서로부터 읽은 방위각 (0°~360°)

반환값:
    서보 모터가 취해야 할 목표 각도 (도, -90° ~ +90° 범위 내)
"""
def compute_target_servo_angle(heading):
    if heading <= 180:
        return -heading
    else:
        return 360 - heading

"""
BNO055 센서로부터 현재 heading(방위각, 0°~360°) 값을 통해 모터를 제어합니다.

"""
def control_motor_using_imu(heading):
        # 1) BNO055 센서로부터 현재 heading(방위각, 0°~360°) 값을 읽어옵니다. heading은 함수의 인자로 주어집니다.

        # 2) 센서의 heading 값을 이용하여, 카메라(서보)가 북쪽을 바라보도록 할 목표 서보 각도를 계산합니다.
        #    이 함수는 기체의 heading에 따라 서보가 반대 방향으로 회전하도록 보정 각도를 결정합니다.
        target_servo = compute_target_servo_angle(heading)

        # 3) 현재 서보 각도와 목표 서보 각도 사이의 최소 회전 차이를 계산합니다.
        #    이 차이는 -180° ~ +180° 범위 내에서 계산되므로, 불필요하게 긴 회전을 방지합니다.
        diff = minimal_angle_diff(target_servo, current_servo_angle)

        # 4) 한 번에 너무 큰 회전을 피하기 위해 회전 스텝을 제한합니다.
        #    여기서는 최대 10°씩만 회전하도록 제한합니다.
        max_step = 10
        if diff > max_step:
            diff = max_step
        elif diff < -max_step:
            diff = -max_step
        
        # 5) 제한된 회전 차이(diff)를 현재 서보 각도에 더하여 새로운 각도로 업데이트합니다.
        current_servo_angle += diff

        # 6) 서보 모터의 물리적 한계(-90° ~ +90°)를 넘지 않도록 클램핑합니다.
        if current_servo_angle > 90:
            current_servo_angle = 90
        elif current_servo_angle < -90:
            current_servo_angle = -90

        # 7) 현재 서보 각도를 PWM 듀티 사이클로 변환하여 서보 모터에 적용합니다.
        duty = angle_to_duty_cycle(current_servo_angle)
        servo.ChangeDutyCycle(duty)

        # Optional) 디버깅을 위해 현재 센서의 heading, 목표 서보 각도, 현재 서보 각도, 회전 차이, 그리고 계산된 듀티 사이클을 출력합니다.
        # print(f"Heading: {heading:.1f}°, Target Servo: {target_servo:.1f}°, Current Servo: {current_servo_angle:.1f}°, Diff: {diff:.1f}°, Duty: {duty:.2f}%")
        return


### For rocket team
# 7.5 (middle)
# 2.9 (sa chul)
ROCKET_MIDDLE = 7.5
ROCKET_SACHUL = 2.9

def change_motor_angle(dutycycle):
    global servo
    servo.ChangeDutyCycle(dutycycle)
    return

