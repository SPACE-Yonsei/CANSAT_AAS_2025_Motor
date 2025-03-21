import RPi.GPIO as GPIO
import time

SERVO_PIN = 12    # mg92b 180도 servo 모터

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)  


def motor_payload_contain_init():
    set_servo_angle(0):
    
def set_servo_angle(angle):
    duty = angle / 18.0 + 2
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    
    time.sleep(0.5)
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

def read_altitude_percentage():
    return altitude_percentage

start_time = time.time()

triggered = False  # 고도 75% 이상일 때 서보 회전 실행 여부

try:
    while True:
        altitude = read_altitude_percentage()
        print("현재 고도: {:.1f}%".format(altitude))
        
        if altitude >= 75 and not triggered:
            set_servo_angle(180)
            triggered = True
        
        time.sleep(1)

except KeyboardInterrupt:
    print("프로그램 종료")

finally:
    pwm.stop()
    GPIO.cleanup()
