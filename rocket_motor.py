#### sudo apt install -y python3-gpiozero
#### #!/usr/bin/env python3 지우면 안됩니다

#!/usr/bin/env python3

#from gpiozero import AngularServo
#import math, random, time

import math, random, time
#
# Define the pulse width of motor in microseconds
MG996R_MIN_PULSE = 500
MG996R_MAX_PULSE = 2500

# Rocket motor degrees
ROCKET_MOTOR_INITIAL_DEGREE = 175
ROCKET_MOTOR_DEPLOY_DEGREE = 90

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
    
    # Turn the motor to initial degree
    mg996r_servo.angle = ROCKET_MOTOR_INITIAL_DEGREE

    return mg996r_servo, pwm

def rocket_initial_state(mg996r_servo):
    mg996r_servo.angle = ROCKET_MOTOR_INITIAL_DEGREE
    return

def rocket_deploy_state(mg996r_servo):
    mg996r_servo.angle = ROCKET_MOTOR_DEPLOY_DEGREE
    return

def terminate_MG996R(pwm):
    pwm.deinit()

if __name__ == "__main__":

    motor_instance, pwm_instance = init_MG996R()
    
    try:
        while True:

            print("INITIAL STATE")
            rocket_initial_state(motor_instance)
            input("Enter to switch to DEPLOY state")
            print("DEPLOY STATE")
            rocket_deploy_state(motor_instance)
            input("Enter to switch to INITIAL state")

    except KeyboardInterrupt:
        pass

    finally:
        terminate_MG996R(pwm_instance)
