# Python FSW V2 Motor App
# Author : Hyeon Lee

from lib import appargs
from lib import msgstructure
from lib import logging
from lib import events
from lib import types

import os
import signal
from multiprocessing import Queue, connection
import threading
import time
import sys

# Runstatus of application. Application is terminated when false
MOTORAPP_RUNSTATUS = True

######################################################
## FUNDEMENTAL METHODS                              ##
######################################################

# SB Methods
# Methods for sending/receiving/handling SB messages

# define constraints for state determination
pressure = 0
temperature = 0
altitude = 0
roll = 0
pitch = 0
yaw = 0
accx = 0
accy = 0
accz = 0

# Handles received message
def command_handler (recv_msg : msgstructure.MsgStructure):
    global MOTORAPP_RUNSTATUS
    global pressure
    global temperature
    global altitude
    global roll
    global pitch
    global yaw
    global accx
    global accy
    global accz

    if recv_msg.MsgID == appargs.MotorAppArg.MID_SendHK:
        print(recv_msg.data)

    elif recv_msg.MsgID == appargs.MainAppArg.MID_TerminateProcess:
        # Change Runstatus to false to start termination process
        events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, f"MOTORAPP TERMINATION DETECTED")
        MOTORAPP_RUNSTATUS = False

    elif recv_msg.MsgID == appargs.BarometerAppArg.MID_SendBarometerData:
        try:
            recv_data = recv_msg.data.split(',')
            pressure = float(recv_data[0])
            temperature = float(recv_data[1])
            altitude = float(recv_data[2])
        except:
            return
        rocket_logic()

    elif recv_msg.MsgID == appargs.ImuAppArg.MID_SendHeadingData:
        try:
            recv_data = recv_msg.data.split(',')
            roll = float(recv_data[0])
            pitch = float(recv_data[1])
            yaw = float(recv_data[2])
            accx = float(recv_data[3])
            accy = float(recv_data[4])
            accz = float(recv_data[5])
        except:
            return
    else:
        events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.error, f"MID {recv_msg.MsgID} not handled")
    return

def send_hk(Main_Queue : Queue):
    global MOTORAPP_RUNSTATUS
    while MOTORAPP_RUNSTATUS:
        motorHK = msgstructure.MsgStructure
        msgstructure.send_msg(Main_Queue, motorHK, appargs.MotorAppArg.AppID, appargs.HkAppArg.AppID, appargs.HkAppArg.MID_ReceiveHK, str(MOTORAPP_RUNSTATUS))

        time.sleep(1)
    return

######################################################
## INITIALIZATION, TERMINATION                      ##
######################################################

# Initialization
def motorapp_init():
    global MOTORAPP_RUNSTATUS
    
    # Disable Keyboardinterrupt since Termination is handled by parent process
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, "Starting motorapp")
    ## User Defined Initialization goes HERE
    motor.motor_init()
    events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, "motorapp Started")

# Termination
def motorapp_terminate():
    global MOTORAPP_RUNSTATUS


    # Termination process goes here
    motor.motor_terminate()

    MOTORAPP_RUNSTATUS = False
    events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, "Terminating motorapp")
    # Termination Process Comes Here

    # Join Each Thread to make sure all threads terminates
    for thread_name in thread_dict:
        events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, f"Terminating thread {thread_name}")
        thread_dict[thread_name].join()
        events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, f"Terminating thread {thread_name} Complete")

    # The termination flag should switch to false AFTER ALL TERMINATION PROCESS HAS ENDED
    events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, "Terminating motorapp complete")
    return

######################################################
## USER METHOD                                      ##
######################################################

from motor import motor


"""
가장 최고의 사출 조건: 최고점에서, 90도 방향 

<절대적 사출조건>(or)
1. 타이머(시작점은 가속도 변화 기준/노이즈보다 크게) - 시뮬레이션 기준 최고 +3초(완성 후 계산 예정)
2. 고도 최대값보다 20m 하강
3. 로켓 각도 위쪽 0도 기준 135도로 회전시
(or n>5) 

<단계적 사출조건>(고도센서 10Hz 기준) 
if 80~100도 & 고도 변화량 < -0.2m  (n+1)
elif 60~120도 & 고도 변화량 < -0.3m  (n+1)
elif 45~135도 & 고도 변화량 < -0.5m  (n+1)
"""

# altitude deploy
logic_counter_altitude = 0
#heading deploy
logic_counter_heading_abs = 0
rocket_deployed = False

launched = False

max_alt = 0
def sa_chul():
    global rocket_deployed
    motor.change_motor_angle(motor.ROCKET_SACHUL)
    rocket_deployed = True

def rocket_logic():
    global rocket_deployed
    if rocket_deployed:
        return
    global logic_counter_heading_abs
    global logic_counter
    global launched

    global pressure
    global temperature
    global altitude
    global roll
    global pitch
    global yaw
    global accx
    global accy
    global accz
    global max_alt
    global logic_counter_altitude

    if altitude > 50 :
        launched = True

    #print(f"Pr:{pressure:.2f}, Mx{max_alt:.2f}, Al{altitude:.2f}, Rl{roll:.2f}, Pt{pitch:.2f}, Yw{yaw:.2f}, Ax{accx:.2f}, Ay{accy:.2f}, Az{accz:.2f}")
    #print(f"LA:{logic_counter_altitude}, LH{logic_counter_heading_abs}")
    ## Altitude logic
    max_alt = max(max_alt, altitude)
    if launched == False:
        return
    # Max alt 보다 2m보다 낮으면
    if (altitude < max_alt - 4):
        logic_counter_altitude += 1
    else:
        logic_counter_altitude -= 3
        if logic_counter_altitude < 0:
            logic_counter_altitude = 0
    
    if logic_counter_altitude >= 10:
        sa_chul()


    if roll > 75 or roll < -75 or pitch > 75 or pitch < -75:
        logic_counter_heading_abs += 1
    else :
        logic_counter_heading_abs -= 3
        if logic_counter_heading_abs < 0:
            logic_counter_heading_abs = 0
    
    if logic_counter_heading_abs >= 10:
        sa_chul()


######################################################
## MAIN METHOD                                      ##
######################################################

thread_dict = dict[str, threading.Thread]()

# This method is called from main app. Initialization, runloop process
def motorapp_main(Main_Queue : Queue, Main_Pipe : connection.Connection):
    global MOTORAPP_RUNSTATUS
    MOTORAPP_RUNSTATUS = True

    # Initialization Process
    motorapp_init()

    # Spawn SB Message Listner Thread
    thread_dict["HKSender_Thread"] = threading.Thread(target=send_hk, args=(Main_Queue, ), name="HKSender_Thread")

    # Spawn Each Threads
    for thread_name in thread_dict:
        thread_dict[thread_name].start()

    try:
        while MOTORAPP_RUNSTATUS:
            # Receive Message From Pipe
            message = Main_Pipe.recv()
            recv_msg = msgstructure.MsgStructure()

            # Unpack Message, Skip this message if unpacked message is not valid
            if msgstructure.unpack_msg(recv_msg, message) == False:
                continue
            
            # Validate Message, Skip this message if target AppID different from motorapp's AppID
            # Exception when the message is from main app
            if recv_msg.receiver_app == appargs.MotorAppArg.AppID or recv_msg.receiver_app == appargs.MainAppArg.AppID:
                # Handle Command According to Message ID
                command_handler(recv_msg)
            else:
                events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.error, "Receiver MID does not match with motorapp MID")

    # If error occurs, terminate app
    except Exception as e:
        events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.error, f"motorapp error : {e}")
        MOTORAPP_RUNSTATUS = False

    # Termination Process after runloop
    motorapp_terminate()

    return
