import time
import math
import RPi.GPIO as GPIO
from simple_pid import PID

SERVO_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50) 
servo.start(7.5) 


pid = PID(1.0, 0.1, 0.05, setpoint=0)
pid.output_limits = (-90, 90)  # 보정값 범위 (-90° ~ +90°)


def simulate_sensor_data():

    return 10 * math.sin(time.time())


def angle_to_duty_cycle(angle):

    mapped_angle = angle + 90  # -90° → 0°, +90° → 180°
    duty_cycle = 2.5 + (mapped_angle / 180.0) * 10  # 0°:2.5%, 180°:12.5%
    return duty_cycle


try:
    while True:

        sensor_angle = simulate_sensor_data()  # 단위: 도(degree)

        correction = pid(sensor_angle)

        duty_cycle = angle_to_duty_cycle(correction)
        servo.ChangeDutyCycle(duty_cycle)
       
        print(f"Sensor angle: {sensor_angle:.2f}°, PID correction: {correction:.2f}°, Duty cycle: {duty_cycle:.2f}%")
       
        time.sleep(0.05)

except KeyboardInterrupt:
    print("프로그램 종료")
    servo.stop()
    GPIO.cleanup()
