# Python FSW V2 Gimbalmotor App
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

from motor import mg92b

# Runstatus of application. Application is terminated when false
GIMBALMOTORAPP_RUNSTATUS = True

######################################################
## FUNDEMENTAL METHODS                              ##
######################################################

# SB Methods
# Methods for sending/receiving/handling SB messages

# Handles received message
def command_handler (recv_msg : msgstructure.MsgStructure):
    global GIMBALMOTORAPP_RUNSTATUS

    if recv_msg.MsgID == appargs.MainAppArg.MID_TerminateProcess:
        # Change Runstatus to false to start termination process
        events.LogEvent(appargs.GimbalmotorAppArg.AppName, events.EventType.info, f"GIMBALMOTORAPP TERMINATION DETECTED")
        GIMBALMOTORAPP_RUNSTATUS = False

    else:
        events.LogEvent(appargs.GimbalmotorAppArg.AppName, events.EventType.error, f"MID {recv_msg.MsgID} not handled")
    return

def send_hk(Main_Queue : Queue, motor_instance, pwm_instance):
    global GIMBALMOTORAPP_RUNSTATUS
    while GIMBALMOTORAPP_RUNSTATUS:
        gimbalmotorHK = msgstructure.MsgStructure
        msgstructure.send_msg(Main_Queue, gimbalmotorHK, appargs.GimbalmotorAppArg.AppID, appargs.HkAppArg.AppID, appargs.GimbalmotorAppArg.MID_SendHK, str(GIMBALMOTORAPP_RUNSTATUS))
        mg92b.rotate_MG92B_ByYaw(motor_instance, pwm_instance, 1)
        time.sleep(1)
    return

######################################################
## INITIALIZATION, TERMINATION                      ##
######################################################

# Initialization
def gimbalmotorapp_init():
    global GIMBALMOTORAPP_RUNSTATUS
    try:
        # Disable Keyboardinterrupt since Termination is handled by parent process
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        events.LogEvent(appargs.GimbalmotorAppArg.AppName, events.EventType.info, "Initializating gimbalmotorapp")
        ## User Defined Initialization goes HERE

        motor_instance, pwm_instance = mg92b.init_MG92B()

        events.LogEvent(appargs.GimbalmotorAppArg.AppName, events.EventType.info, "Gimbalmotorapp Initialization Complete")
        return motor_instance, pwm_instance
    
    except Exception as e:
        events.LogEvent(appargs.GimbalmotorAppArg.AppName, events.EventType.error, "Error during initialization")
        GIMBALMOTORAPP_RUNSTATUS = False
    

# Termination
def gimbalmotorapp_terminate():
    global GIMBALMOTORAPP_RUNSTATUS

    GIMBALMOTORAPP_RUNSTATUS = False
    events.LogEvent(appargs.GimbalmotorAppArg.AppName, events.EventType.info, "Terminating gimbalmotorapp")
    # Termination Process Comes Here

    # Join Each Thread to make sure all threads terminates
    for thread_name in thread_dict:
        events.LogEvent(appargs.GimbalmotorAppArg.AppName, events.EventType.info, f"Terminating thread {thread_name}")
        thread_dict[thread_name].join()
        events.LogEvent(appargs.GimbalmotorAppArg.AppName, events.EventType.info, f"Terminating thread {thread_name} Complete")

    # The termination flag should switch to false AFTER ALL TERMINATION PROCESS HAS ENDED
    events.LogEvent(appargs.GimbalmotorAppArg.AppName, events.EventType.info, "Terminating gimbalmotorapp complete")
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
def gimbalmotorapp_main(Main_Queue : Queue, Main_Pipe : connection.Connection):
    global GIMBALMOTORAPP_RUNSTATUS
    GIMBALMOTORAPP_RUNSTATUS = True

    # Initialization Process
    motor_instance, pwm_instance = gimbalmotorapp_init()

    # Spawn SB Message Listner Thread
    thread_dict["HKSender_Thread"] = threading.Thread(target=send_hk, args=(Main_Queue, motor_instance, pwm_instance), name="HKSender_Thread")

    # Spawn Each Threads
    for thread_name in thread_dict:
        thread_dict[thread_name].start()

    try:
        while GIMBALMOTORAPP_RUNSTATUS:
            # Receive Message From Pipe
            message = Main_Pipe.recv()
            recv_msg = msgstructure.MsgStructure()

            # Unpack Message, Skip this message if unpacked message is not valid
            if msgstructure.unpack_msg(recv_msg, message) == False:
                continue
            
            # Validate Message, Skip this message if target AppID different from gimbalmotorapp's AppID
            # Exception when the message is from main app
            if recv_msg.receiver_app == appargs.GimbalmotorAppArg.AppID or recv_msg.receiver_app == appargs.MainAppArg.AppID:
                # Handle Command According to Message ID
                command_handler(recv_msg)
            else:
                events.LogEvent(appargs.GimbalmotorAppArg.AppName, events.EventType.error, "Receiver MID does not match with gimbalmotorapp MID")

    # If error occurs, terminate app
    except Exception as e:
        events.LogEvent(appargs.GimbalmotorAppArg.AppName, events.EventType.error, f"gimbalmotorapp error : {e}")
        GIMBALMOTORAPP_RUNSTATUS = False

    # Termination Process after runloop
    gimbalmotorapp_terminate()

    return