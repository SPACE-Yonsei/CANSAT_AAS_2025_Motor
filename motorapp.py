# Python FSW V2 Motor App
# Author : Hyeon Lee

from lib import appargs
from lib import msgstructure
from lib import logging
from lib import events
from lib import types

import os
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

# This fuction is spawned as an independent thread
# Listens SB messages routed from main app using pipe
def SB_listner (Main_Pipe : connection.Connection):
    global MOTORAPP_RUNSTATUS
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
    return

# Handles received message
def command_handler (recv_msg : msgstructure.MsgStructure):
    if recv_msg.MsgID == appargs.MotorAppArg.MID_SendHK:
        print(recv_msg.data)

    elif recv_msg.MsgID == appargs.ImuAppArg.MID_SendHeadingData:
        heading_data_handler(recv_msg)

    elif recv_msg.MsgID == appargs.MainAppArg.MID_TerminateProcess:
        # Change Runstatus to false to start termination process
        global MOTORAPP_RUNSTATUS
        MOTORAPP_RUNSTATUS = False

    else:
        events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.error, f"MID {recv_msg.MsgID} not handled")
    return

######################################################
## INITIALIZATION, TERMINATION                      ##
######################################################

# Initialization
def motorapp_init():
    events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, "Starting motorapp")
    ## User Defined Initialization goes HERE
    events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, "Initializing Motor Module")
    motor.motor_init()
    events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, "motorapp Started")

# Termination
def motorapp_terminate():
    global MOTORAPP_RUNSTATUS

    current_thread = threading.current_thread().name
        
    MOTORAPP_RUNSTATUS = False
    events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, "Terminating motorapp")
    # Termination Process Comes Here

    # Join Each Thread to make sure all threads terminates
    for thread_name in thread_dict:
        events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, f"Terminating thread {thread_name}")
        if thread_name != current_thread:
            thread_dict[thread_name].join()
        events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, f"Terminating thread {thread_name} Complete")

    # The termination flag should switch to false AFTER ALL TERMINATION PROCESS HAS ENDED
    events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, "Terminating motorapp complete")
    sys.exit()
    return

######################################################
## USER METHOD                                      ##
######################################################

from motor import motor

def heading_data_handler(recv_msg : msgstructure.MsgStructure):
    heading = float(recv_msg.data)
    print(f"heading : {heading}")
    motor.control_motor_using_imu(heading)

# Put user-defined methods here!

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
    thread_dict["SBListner_Thread"] = threading.Thread(target=SB_listner, args=(Main_Pipe, ), name="SBListner_Thread")

    # Spawn Each Threads
    for thread_name in thread_dict:
        thread_dict[thread_name].start()

    try:
        # Runloop
        while MOTORAPP_RUNSTATUS:
            motorHK = msgstructure.MsgStructure
            msgstructure.send_msg(Main_Queue, motorHK, appargs.MotorAppArg.AppID, appargs.HkAppArg.AppID, appargs.HkAppArg.MID_ReceiveHK, str(MOTORAPP_RUNSTATUS))

            time.sleep(1)
    # If error occurs, terminate app
    except Exception as e:
        events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.error, f"motorapp error : {e}")
        MOTORAPP_RUNSTATUS = False

    # Termination Process after runloop
    motorapp_terminate()

    return