import time         # 시간 지연을 위해 사용
import math         # 수학 함수(atan2, sin 등) 사용을 위해 필요
import RPi.GPIO as GPIO     # 라즈베리파이의 GPIO 제어를 위해 사용
import board        # I2C 핀 접근을 위한 라이브러리
import busio        # I2C 통신을 위한 라이브러리
import adafruit_bno055  # BNO055 센서 제어 라이브러리

# ===== 1. GPIO 및 서보 모터 설정 =====
# 경고 메시지를 끄면 이전 실행에서 설정된 핀의 상태로 인해 발생하는 경고를 무시할 수 있습니다.
GPIO.setwarnings(False)
# BCM(브로드컴) 핀 번호 체계를 사용하여 핀 번호를 지정합니다.
GPIO.setmode(GPIO.BCM)

# 서보 모터 제어를 위한 핀 설정 (여기서는 GPIO 18번 사용)
SERVO_PIN = 18
GPIO.setup(SERVO_PIN, GPIO.OUT)   # 서보 모터를 출력 모드로 설정

# 50Hz PWM 신호 생성: 서보 모터의 기본 동작 주기는 약 20ms(50Hz)입니다.
servo = GPIO.PWM(SERVO_PIN, 50)
# 초기 듀티 사이클을 7.5%로 설정하면, 대부분의 서보 모터는 중앙(약 90°) 위치에 놓입니다.
servo.start(7.5)

# ===== 2. BNO055 센서 초기화 =====
# I2C 버스를 초기화하여 라즈베리파이의 SCL과 SDA 핀을 사용하도록 합니다.
i2c = busio.I2C(board.SCL, board.SDA)
# BNO055 센서를 I2C를 통해 연결합니다.
# adafruit_bno055 라이브러리를 사용하면 센서의 다양한 데이터를 쉽게 읽을 수 있습니다.
sensor = adafruit_bno055.BNO055_I2C(i2c)

# 현재 서보 모터의 각도를 저장할 변수 (단위: 도)
# 여기서는 카메라가 북쪽을 바라보도록 0도로 초기화합니다.
current_servo_angle = 0

# ===== 3. 함수 정의 =====

def minimal_angle_diff(target, current):
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
    diff = target - current
    # (diff + 180)를 360으로 나눈 나머지에서 180을 빼면 -180° ~ +180° 범위가 됩니다.
    diff = (diff + 180) % 360 - 180
    return diff

def angle_to_duty_cycle(angle):
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
    mapped_angle = angle + 90   # 예: -90° → 0°, +90° → 180°
    # 선형 매핑: 0°에 2.5%, 180°에 12.5% → 듀티 사이클 변화 범위는 10%
    duty_cycle = 2.5 + (mapped_angle / 180.0) * 10
    return duty_cycle

def get_heading():
    """
    BNO055 센서에서 heading(방위각, 0°~360°) 값을 읽어 반환합니다.
    BNO055 센서는 euler 각도를 반환하며, 그 첫 번째 요소가 heading 값입니다.
    
    반환값:
      heading (도), 만약 센서 데이터가 없으면 None 반환
    """
    euler = sensor.euler  # sensor.euler는 (heading, roll, pitch) 튜플를 반환
    if euler is None:
        return None  # 데이터가 없을 경우 None 처리
    heading = euler[0]  # 첫 번째 값이 heading (방위각) 입니다.
    if heading is None:
        return None  # 센서가 유효하지 않을 경우 None 반환
    return heading

def compute_target_servo_angle(heading):
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
    if heading <= 180:
        return -heading
    else:
        return 360 - heading

# ===== 4. 메인 루프: 센서 데이터를 기반으로 서보 모터 보정 =====
try:
    while True:
        # 1) BNO055 센서로부터 현재 heading(방위각, 0°~360°) 값을 읽어옵니다.
        heading = get_heading()
        if heading is None:
            # 만약 센서로부터 데이터를 읽지 못하면, 에러 메시지를 출력하고 짧은 시간 후 다시 시도합니다.
            print("BNO055 센서 값을 읽을 수 없습니다.")
            time.sleep(0.1)
            continue  # 센서 값이 없으면 다음 루프로 넘어감
        
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
        
        # 8) 디버깅을 위해 현재 센서의 heading, 목표 서보 각도, 현재 서보 각도, 회전 차이, 그리고 계산된 듀티 사이클을 출력합니다.
        print(f"Heading: {heading:.1f}°, Target Servo: {target_servo:.1f}°, Current Servo: {current_servo_angle:.1f}°, Diff: {diff:.1f}°, Duty: {duty:.2f}%")
        
        # 9) 0.1초 대기 후 다음 센서 데이터를 읽어 업데이트합니다.
        time.sleep(0.1)

except KeyboardInterrupt:
    # 사용자가 Ctrl+C를 누르면 프로그램 종료
    print("프로그램 종료")
    # 서보 모터 PWM 신호를 중지하고, 모든 GPIO 설정을 초기화합니다.
    servo.stop()
    GPIO.cleanup()
