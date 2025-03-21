import time
import math
import RPi.GPIO as GPIO

# 로켓 페이로드 사출 MG995 서보모터가 연결된 핀 번호
SERVO_PIN = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz PWM
pwm.start(0)

state = None  # 하강 상태 여부, None 이다가 descending으로 변경
n = 0         # 조건 만족 카운트 (n이 5보다 커지면 사출)
ACC_THRESHOLD = 0.3  # 가속도 변화 임계치

def set_servo_angle(angle):
    duty = angle / 18.0 + 2   # 예: 0도 -> 약 2% duty, 180도 -> 약 12% duty
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)        
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

def rocket_payload_init():
    pwm.start(0)

def Sachull():
    set_servo_angle(180)
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(12)
    time.sleep(0.5)
    GPIO.output(SERVO_PIN, False)

def read_acceleration():
    return 0.5  # 예시

def read_altitude():
    return 100.0  # 예시

def read_angle():
    return 90.0  # 예시

try:
    while True:
        acc = read_acceleration() # 현재 가속도
        
        # 가속도 임계치 이상이고 아직 하강 상태가 아닐 때 하강 상태로 전환
        if acc > ACC_THRESHOLD and state != "descending":
            state = "descending"
            start_time = time.time()      # 최고 고도 시각 기록
            high_alt = read_altitude()      # 최고 고도 기록
            print("하강 상태 전환: 최고 고도 기록 =", high_alt)
        
        if state == "descending":
            current_time = time.time()
            current_alt = read_altitude()   # 현재 고도 입력
            current_angle = read_angle()      # 현재 z축 기준 각도 입력
            
            # 여러 조건 충족 시 (예시로 출력)
            if n > 5:
                Sachull()
            if current_time - start_time >= 3000:
                Sachull()
            if high_alt - current_alt >= 20:
                Sachull()
            if current_angle >= 135:
                Sachull()
            
            if 80 <= current_angle <= 100 and high_alt - current_alt < 0.2:
                n += 1
            elif 60 <= current_angle <= 120 and high_alt - current_alt < 0.3:
                n += 1
            elif 45 <= current_angle <= 135 and high_alt - current_alt < 0.5:
                n += 1
            else:
                # 로켓 안정성 유지: 조건 벗어나면 n 차감 (0 미만은 안되도록)
                if n > 0:
                    n -= 1

        time.sleep(0.1)

except KeyboardInterrupt:
    print("프로그램 종료")

finally:
    pwm.stop()
    GPIO.cleanup()
