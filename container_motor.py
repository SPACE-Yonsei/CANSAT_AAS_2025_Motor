
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

CONTAINER_INITIAL_PULSE = (CONTAINER_INITIAL_DEGREE/180)*2000 + 500
CONTAINER_RELEASE_PULSE = (CONTAINER_RELEASE_DEGREE/180)*2000 + 500

# pi.set_servo_pulsewidth(18, 1500)
#angle = (angle/180)*2000 + 500

def init_MG996R():
    import pigpio
    pi = pigpio.pi()
    pin = CONTAINER_MOTOR_PIN
    pi.set_servo_pulsewidth(pin, CONTAINER_INITIAL_PULSE)

    return pi, pin

def container_initial(pi, pin):

    pi.set_servo_pulsewidth(pin, CONTAINER_INITIAL_PULSE)

def container_release(pi, pin):

    for i in range(0, 10):
        pi.set_servo_pulsewidth(pin, CONTAINER_RELEASE_PULSE)
        time.sleep(0.5)
        pi.set_servo_pulsewidth(pin, CONTAINER_INITIAL_PULSE)
        time.sleep(0.5)
    
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
            pi.set_servo_pulsewidth(pin, CONTAINER_RELEASE_PULSE)
            input("Enter to switch to DEPLOY state")

            print("DEPLOY STATE")
            container_release(pi, pin)
            input("Enter to switch to INITIAL state")

    except KeyboardInterrupt:
        pass

    finally:
        terminate_MG996R(pi)
