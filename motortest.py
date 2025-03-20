import time
import math
import RPi.GPIO as GPIO
from simple_pid import PID

SERVO_PIN = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50) 
servo.start(7.5) 


pid = PID(1.0, 0.1, 0.05, setpoint=0)
pid.output_limits = (-90, 90)  # 


def simulate_sensor_data():

    return 10 * math.sin(time.time())


def angle_to_duty_cycle(angle):

    mapped_angle = angle + 90
    duty_cycle = 2.5 + (mapped_angle / 180.0) * 10  # 0째:2.5%, 180째:12.5%
    return duty_cycle


try:
    while True:

        sensor_angle = simulate_sensor_data()  

        correction = pid(sensor_angle)

        duty_cycle = angle_to_duty_cycle(correction)
        servo.ChangeDutyCycle(duty_cycle)
       
        print(f"Sensor angle: {sensor_angle:.2f}째, PID correction: {correction:.2f}째, Duty cycle: {duty_cycle:.2f}%")
       
        time.sleep(0.05)

except KeyboardInterrupt:
    print("dasdf")
    servo.stop()
    GPIO.cleanup()