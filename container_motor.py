
#### sudo apt install -y python3-gpiozero
#### #!/usr/bin/env python3 지우면 안됩니다

#!/usr/bin/env python3

#from gpiozero import AngularServo
#import math, random, time

import time

CONTAINER_MOTOR_PIN = 12

# Set the container pulse and degree
CONTAINER_INITIAL_DEGREE = 30
CONTAINER_RELEASE_DEGREE = 120
CONTAINER_FREE_DEGREE = 90

CONTAINER_MOTOR_MIN_PULSE = 500
CONTAINER_MOTOR_MAX_PULSE = 2500

def angle_to_pulse(angle) -> int:
    if angle < 0:
        angle = 0
    elif angle > 180:
        angle = 180
    
    return int(CONTAINER_MOTOR_MIN_PULSE + ((angle/180)*(CONTAINER_MOTOR_MAX_PULSE - CONTAINER_MOTOR_MIN_PULSE)))

def init_MG996R():
    import pigpio
    pi = pigpio.pi()
    pi.set_servo_pulsewidth(CONTAINER_MOTOR_PIN, angle_to_pulse(CONTAINER_INITIAL_DEGREE))

    return pi

def container_initial(pi):

    pi.set_servo_pulsewidth(CONTAINER_MOTOR_PIN, angle_to_pulse(CONTAINER_INITIAL_DEGREE))

def container_free(pi):

    pi.set_servo_pulsewidth(CONTAINER_MOTOR_PIN, angle_to_pulse(CONTAINER_FREE_DEGREE))

def container_release(pi):

    for i in range(0, 10):
        pi.set_servo_pulsewidth(CONTAINER_MOTOR_PIN, angle_to_pulse(CONTAINER_RELEASE_DEGREE))
        time.sleep(0.5)
        pi.set_servo_pulsewidth(CONTAINER_MOTOR_PIN, angle_to_pulse(CONTAINER_INITIAL_DEGREE))
        time.sleep(0.5)
    
    return

def terminate_MG996R(pi):
    pi.stop()

if __name__ == "__main__":

    pi = init_MG996R()
    
    try:
        while True:

            print("INITIAL STATE")
            container_initial(pi)
            input("Enter to switch to RELEASE state")

            print("FREE STATE")
            container_free(pi)
            input("Enter to switch to DEPLOY state")

            print("DEPLOY STATE")
            container_release(pi)
            input("Enter to switch to INITIAL state")

    except KeyboardInterrupt:
        pass

    finally:
        terminate_MG996R(pi)
