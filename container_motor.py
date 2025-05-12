#### sudo apt install -y python3-gpiozero
#### #!/usr/bin/env python3 지우면 안됩니다

#!/usr/bin/env python3

#from gpiozero import AngularServo
#import math, random, time

import math, random, time

# Define the pulse width of motor in microseconds
MG996R_MIN_PULSE = 500
MG996R_MAX_PULSE = 2500

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

def rotate_mg996r(mg996r_servo, target_degree):
    mg996r_servo.angle = target_degree
    return

def terminate_MG996R(pwm):
    pwm.deinit()

def normalize_diff(angle):
    return (angle + 180) % 360 - 180

if __name__ == "__main__":

    motor_instance, pwm_instance = init_MG996R()
    
    try:
        while True:

            target_degree = float(input("Input Target Degree (0 ~ 180) : "))
            if target_degree > 180 or target_degree < 0:
                print("invalid range!")
                continue
            else:
                rotate_mg996r(motor_instance, target_degree)
            
    except KeyboardInterrupt:
        pass

    finally:
        terminate_MG996R(pwm_instance)
