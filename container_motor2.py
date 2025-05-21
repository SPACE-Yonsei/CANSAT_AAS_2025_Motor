
#### sudo apt install -y python3-gpiozero
#### #!/usr/bin/env python3 지우면 안됩니다

#!/usr/bin/env python3

#from gpiozero import AngularServo
#import math, random, time

import time

CONTAINER_METHOD = 0

# 0 -> A, 1 -> B
SELECTED_CONFIG = 0

# Method A, Use hole
A_CONTAINER_INITIAL_DEGREE = (30/180)*2000 + 500
A_CONTAINER_RELEASE_DEGREE = (120/180)*2000 + 500

# Method B, Use motor to pull string
B_CONTAINER_INITIAL_DEGREE = (90/180)*2000 + 500
B_CONTAINER_RELEASE_DEGREE = (0/180)*2000 + 500


# pi.set_servo_pulsewidth(18, 1500)
#angle = (angle/180)*2000 + 500

def init_MG996R():
    import pigpio
    pi = pigpio.pi()
    pin = 12
    pi.set_servo_pulsewidth(pin, 0)

    return pi, pin

def container_initial(pi, pin):
    # Config A -> Use hole
    if SELECTED_CONFIG == 0:
        pi.set_servo_pulsewidth(pin, A_CONTAINER_INITIAL_DEGREE)

    # Config B -> Use motor
    if SELECTED_CONFIG == 1:
        pi.set_servo_pulsewidth(pin, B_CONTAINER_INITIAL_DEGREE)

def container_release(pi, pin):
    # Config A -> Use hole
    if SELECTED_CONFIG == 0:
        for i in range(0, 10):
            pi.set_servo_pulsewidth(pin, A_CONTAINER_RELEASE_DEGREE)
            time.sleep(0.3)
            pi.set_servo_pulsewidth(pin, A_CONTAINER_INITIAL_DEGREE)
            time.sleep(0.3)
    # Config B -> Use motor
    if SELECTED_CONFIG == 1:
        for i in range(0, 10):
            pi.set_servo_pulsewidth(pin, B_CONTAINER_RELEASE_DEGREE)
            time.sleep(0.3)
            pi.set_servo_pulsewidth(pin, B_CONTAINER_INITIAL_DEGREE)
            time.sleep(0.3)
    
    return

def terminate_MG996R(pi):
    pi.stop()

if __name__ == "__main__":

    pi, pin= init_MG996R()
    
    try:
        while True:

            print("INITIAL STATE")
            container_initial(pi, pin)
            input("Enter to switch to RELEASE state")

            print("release state")
            pi.set_servo_pulsewidth(pin, 1500)
            input("Enter to switch to DEPLOY state")

            print("DEPLOY STATE")
            container_release(pi, pin)
            input("Enter to switch to INITIAL state")

    except KeyboardInterrupt:
        pass

    finally:
        terminate_MG996R(pi)
