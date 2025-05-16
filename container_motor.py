#### sudo apt install -y python3-gpiozero
#### #!/usr/bin/env python3 지우면 안됩니다

#!/usr/bin/env python3

#from gpiozero import AngularServo
#import math, random, time

import math, random, time

# Define the pulse width of motor in microseconds
MG996R_MIN_PULSE = 500
MG996R_MAX_PULSE = 2500

CONTAINER_METHOD = 0

# 0 -> A, 1 -> B
SELECTED_CONFIG = 0

# Method A, Use hole
A_CONTAINER_INITIAL_DEGREE = 30
A_CONTAINER_RELEASE_DEGREE = 120

# Method B, Use motor to pull string
B_CONTAINER_INITIAL_DEGREE = 90
B_CONTAINER_RELEASE_DEGREE = 0

def init_MG996R():
    import board
    import pwmio
    from adafruit_motor import servo

    # Configure Motor Pin
    pwm = pwmio.PWMOut(board.D12, frequency=50)

    # Adjust minimum, maximum pulse value
    mg996r_servo = servo.Servo(
        pwm,
        min_pulse=MG996R_MIN_PULSE,    # microseconds
        max_pulse=MG996R_MAX_PULSE,   # microseconds
        actuation_range=180
    )
    
    return mg996r_servo, pwm

def container_initial(mg996r_servo):
    # Config A -> Use hole
    if SELECTED_CONFIG == 0:
        mg996r_servo.angle = A_CONTAINER_INITIAL_DEGREE

    # Config B -> Use motor
    if SELECTED_CONFIG == 1:
        mg996r_servo.angle = B_CONTAINER_INITIAL_DEGREE

def container_release(mg996r_servo):
    # Config A -> Use hole
    if SELECTED_CONFIG == 0:
        for i in range(0, 10):
            mg996r_servo.angle = A_CONTAINER_RELEASE_DEGREE
            time.sleep(0.5)
            mg996r_servo.angle = A_CONTAINER_INITIAL_DEGREE
            time.sleep(0.5)

    # Config B -> Use motor
    if SELECTED_CONFIG == 1:
        mg996r_servo.angle = B_CONTAINER_RELEASE_DEGREE
    
    return

def terminate_MG996R(pwm):
    pwm.deinit()

def normalize_diff(angle):
    return (angle + 180) % 360 - 180

if __name__ == "__main__":

    motor_instance, pwm_instance = init_MG996R()
    
    try:
        while True:

            print("INITIAL STATE")
            container_initial(motor_instance)
            input("Enter to switch to RELEASE state")
            print("release state")
            motor_instance.angle = 90
            input("Enter to switch to DEPLOY state")
            print("DEPLOY STATE")
            container_release(motor_instance)
            input("Enter to switch to INITIAL state")

    except KeyboardInterrupt:
        pass

    finally:
        terminate_MG996R(pwm_instance)
