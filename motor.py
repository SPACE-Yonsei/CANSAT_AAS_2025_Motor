import time
import math
import RPi.GPIO as GPIO
import board
import busio
import adafruit_bno055

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
SERVO_PIN = 18
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)  # 50Hz (20ms 주기)
servo.start(7.5)

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bno055.BNO055_I2C(i2c)

current_servo_angle = 0

def minimal_angle_diff(target, current):
    diff = target - current
    diff = (diff + 180) % 360 - 180
    return diff

def angle_to_duty_cycle(angle):
    mapped_angle = angle + 90   # -90° → 0°, +90° → 180°
    duty_cycle = 2.5 + (mapped_angle / 180.0) * 10 
    return duty_cycle

def get_heading():
    euler = sensor.euler  # euler = (heading, roll, pitch)
    if euler is None:
        return None
    heading = euler[0]
    if heading is None:
        return None
    return heading

def compute_target_servo_angle(heading):
    if heading <= 180:
        return -heading
    else:
        return 360 - heading

try:
    while True
        heading = get_heading()
        if heading is None:
            print("BNO055 센서 값을 읽을 수 없습니다.")
            time.sleep(0.1)
            continue

        target_servo = compute_target_servo_angle(heading)
        
        diff = minimal_angle_diff(target_servo, current_servo_angle)
        
        max_step = 10
        if diff > max_step:
            diff = max_step
        elif diff < -max_step:
            diff = -max_step
        
        current_servo_angle += diff
        
        if current_servo_angle > 90:
            current_servo_angle = 90
        elif current_servo_angle < -90:
            current_servo_angle = -90
        
        duty = angle_to_duty_cycle(current_servo_angle)
        servo.ChangeDutyCycle(duty)
        
        print(f"Heading: {heading:.1f}°, Target Servo: {target_servo:.1f}°, Current Servo: {current_servo_angle:.1f}°, Diff: {diff:.1f}°, Duty: {duty:.2f}%")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("프로그램 종료")
    servo.stop()
    GPIO.cleanup()
