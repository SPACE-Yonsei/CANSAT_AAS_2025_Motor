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

    elif recv_msg.MsgID == appargs.ImuAppArg.MID_SendIMUData:
        try:
            recv_data = recv_msg.data.split(',')
            roll = recv_data[0]
            pitch = recv_data[1]
            yaw = recv_data[2]
            accx = recv_data[3]
            accy = recv_data[4]
            accz = recv_data[5]
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
    events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, "motorapp Started")

# Termination
def motorapp_terminate():
    global MOTORAPP_RUNSTATUS

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

def rocket_logic():
    global pressure
    global temperature
    global altitude
    global roll
    global pitch
    global yaw
    global accx
    global accy
    global accz

    print(f"Pr:{pressure:.2f}, Tm{temperature:.2f}, Al{altitude:.2f}, Ax{accx:.2f}, Ay{accy:.2f}, Az{accz:.2f}")

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