# Python FSW V2 Cammotor App
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
CAMMOTORAPP_RUNSTATUS = True

# Import Cammotor App for MG92B
from motor import mg92b

######################################################
## FUNDEMENTAL METHODS                              ##
######################################################

# SB Methods
# Methods for sending/receiving/handling SB messages

# Handles received message
def command_handler (recv_msg : msgstructure.MsgStructure):
    global CAMMOTORAPP_RUNSTATUS

    if recv_msg.MsgID == appargs.MainAppArg.MID_TerminateProcess:
        # Change Runstatus to false to start termination process
        events.LogEvent(appargs.CammotorAppArg.AppName, events.EventType.info, f"CAMMOTORAPP TERMINATION DETECTED")
        CAMMOTORAPP_RUNSTATUS = False

    # When received Yaw Data from IMU
    if recv_msg.MsgID == appargs.ImuAppArg.MID_SendYawData:
        recv_yaw = float(recv_msg.data)
        mg92b.rotate_MG92B_ByYaw(recv_yaw)

    else:
        events.LogEvent(appargs.CammotorAppArg.AppName, events.EventType.error, f"MID {recv_msg.MsgID} not handled")
    return

def send_hk(Main_Queue : Queue):
    global CAMMOTORAPP_RUNSTATUS
    while CAMMOTORAPP_RUNSTATUS:
        cammotorHK = msgstructure.MsgStructure
        msgstructure.send_msg(Main_Queue, cammotorHK, appargs.CammotorAppArg.AppID, appargs.HkAppArg.AppID, appargs.CammotorAppArg.MID_SendHK, str(CAMMOTORAPP_RUNSTATUS))
        time.sleep(1)
    return

######################################################
## INITIALIZATION, TERMINATION                      ##
######################################################

# Initialization
def cammotorapp_init():
    global CAMMOTORAPP_RUNSTATUS
    try:
        # Disable Keyboardinterrupt since Termination is handled by parent process
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        events.LogEvent(appargs.CammotorAppArg.AppName, events.EventType.info, "Initializating cammotorapp")
        ## User Defined Initialization goes HERE

        # Initialize MG92B Cammotor
        mg92b.init_MG92B()

        events.LogEvent(appargs.CammotorAppArg.AppName, events.EventType.info, "Cammotorapp Initialization Complete")
    except Exception as e:
        events.LogEvent(appargs.CammotorAppArg.AppName, events.EventType.error, "Error during initialization")
        CAMMOTORAPP_RUNSTATUS = False

# Termination
def cammotorapp_terminate():
    global CAMMOTORAPP_RUNSTATUS

    CAMMOTORAPP_RUNSTATUS = False
    events.LogEvent(appargs.CammotorAppArg.AppName, events.EventType.info, "Terminating cammotorapp")
    # Termination Process Comes Here

    # Terminate Cammotor
    mg92b.terminate_MG92B()

    # Join Each Thread to make sure all threads terminates
    for thread_name in thread_dict:
        events.LogEvent(appargs.CammotorAppArg.AppName, events.EventType.info, f"Terminating thread {thread_name}")
        thread_dict[thread_name].join()
        events.LogEvent(appargs.CammotorAppArg.AppName, events.EventType.info, f"Terminating thread {thread_name} Complete")

    # The termination flag should switch to false AFTER ALL TERMINATION PROCESS HAS ENDED
    events.LogEvent(appargs.CammotorAppArg.AppName, events.EventType.info, "Terminating cammotorapp complete")
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
def cammotorapp_main(Main_Queue : Queue, Main_Pipe : connection.Connection):
    global CAMMOTORAPP_RUNSTATUS
    CAMMOTORAPP_RUNSTATUS = True

    # Initialization Process
    cammotorapp_init()

    # Spawn SB Message Listner Thread
    thread_dict["HKSender_Thread"] = threading.Thread(target=send_hk, args=(Main_Queue, ), name="HKSender_Thread")

    # Spawn Each Threads
    for thread_name in thread_dict:
        thread_dict[thread_name].start()

    try:
        while CAMMOTORAPP_RUNSTATUS:
            # Receive Message From Pipe
            message = Main_Pipe.recv()
            recv_msg = msgstructure.MsgStructure()

            # Unpack Message, Skip this message if unpacked message is not valid
            if msgstructure.unpack_msg(recv_msg, message) == False:
                continue
            
            # Validate Message, Skip this message if target AppID different from cammotorapp's AppID
            # Exception when the message is from main app
            if recv_msg.receiver_app == appargs.CammotorAppArg.AppID or recv_msg.receiver_app == appargs.MainAppArg.AppID:
                # Handle Command According to Message ID
                command_handler(recv_msg)
            else:
                events.LogEvent(appargs.CammotorAppArg.AppName, events.EventType.error, "Receiver MID does not match with cammotorapp MID")

    # If error occurs, terminate app
    except Exception as e:
        events.LogEvent(appargs.CammotorAppArg.AppName, events.EventType.error, f"cammotorapp error : {e}")
        CAMMOTORAPP_RUNSTATUS = False

    # Termination Process after runloop
    cammotorapp_terminate()

    return