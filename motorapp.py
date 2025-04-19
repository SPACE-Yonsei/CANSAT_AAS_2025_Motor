# Python FSW V2 Motor App
# Author : Hyeon Lee

from lib import appargs
from lib import msgstructure
from lib import logging
from lib import events
from lib import types

import signal
from multiprocessing import Queue, connection
import threading
import time

# Runstatus of application. Application is terminated when false
MOTORAPP_RUNSTATUS = True

######################################################
## FUNDEMENTAL METHODS                              ##
######################################################

# SB Methods
# Methods for sending/receiving/handling SB messages

# Handles received message
def command_handler (recv_msg : msgstructure.MsgStructure):
    global MOTORAPP_RUNSTATUS

    if recv_msg.MsgID == appargs.MainAppArg.MID_TerminateProcess:
        # Change Runstatus to false to start termination process
        events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, f"MOTORAPP TERMINATION DETECTED")
        MOTORAPP_RUNSTATUS = False

    else:
        events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.error, f"MID {recv_msg.MsgID} not handled")
    return

def send_hk(Main_Queue : Queue):
    global MOTORAPP_RUNSTATUS
    while MOTORAPP_RUNSTATUS:
        motorHK = msgstructure.MsgStructure
        msgstructure.send_msg(Main_Queue, motorHK, appargs.MotorAppArg.AppID, appargs.HkAppArg.AppID, appargs.MotorAppArg.MID_SendHK, str(MOTORAPP_RUNSTATUS))
        time.sleep(1)
    return

######################################################
## INITIALIZATION, TERMINATION                      ##
######################################################

# Initialization
def motorapp_init():
    global MOTORAPP_RUNSTATUS
    try:
        # Disable Keyboardinterrupt since Termination is handled by parent process
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, "Initializating motorapp")
        ## User Defined Initialization goes HERE
        events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.info, "Motorapp Initialization Complete")
    except Exception as e:
        events.LogEvent(appargs.MotorAppArg.AppName, events.EventType.error, "Error during initialization")
        MOTORAPP_RUNSTATUS = False

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