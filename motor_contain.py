import RPi.GPIO as GPIO
import time

# 서보모터가 연결된 핀 번호 (BCM 모드 사용)
SERVO_PIN = 18

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# 서보모터 PWM 설정: 50Hz (표준 서보 주파수)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)  # 초기 듀티 사이클 0%

def set_servo_angle(angle):
    """
    서보모터의 각도를 설정하는 함수.
    서보모터의 경우 보통 0도에 2% ~ 1ms, 180도에 12% ~ 2ms 정도의 듀티사이클을 사용함.
    여기서는 간단하게 angle/18 + 2 방식으로 계산.
    """
    duty = angle / 18.0 + 2
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    # 각도 변경 후 서보가 목표 위치에 도달할 시간을 대기 (필요에 따라 조정)
    time.sleep(0.5)
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

def read_altitude_percentage():
    """
    타코미터(TCRT5000)를 통해 현재 고도(%)를 읽어오는 함수.
    실제 구현에서는 ADC 또는 센서 라이브러리 사용.
    아래는 예시로 시간에 따라 고도가 증가하는 시뮬레이션 코드임.
    """
    t = time.time() - start_time
    # 예시: 매초 5%씩 증가하여 20초면 100%가 되도록 시뮬레이션
    altitude_percentage = min(100, t * 5)
    return altitude_percentage

# 시뮬레이션 시작 시간 기록
start_time = time.time()

triggered = False  # 고도 75% 이상일 때 서보 회전 실행 여부

try:
    while True:
        altitude = read_altitude_percentage()
        print("현재 고도: {:.1f}%".format(altitude))
        
        # 고도가 최대 고도의 75% 이상일 때 서보 회전 실행 (단, 한번만)
        if altitude >= 75 and not triggered:
            print("고도가 75% 이상입니다. 서보모터를 0도에서 180도로 회전합니다.")
            # 0도 위치로 이동 후 180도로 이동
            set_servo_angle(0)
            time.sleep(0.5)  # 안정화를 위한 딜레이
            set_servo_angle(180)
            triggered = True
        
        time.sleep(1)

except KeyboardInterrupt:
    print("프로그램 종료")

finally:
    pwm.stop()
    GPIO.cleanup()
