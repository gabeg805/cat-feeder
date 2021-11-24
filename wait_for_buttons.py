#!/usr/bin/env python
##
# Using Pin #4 for CW and Pin #27 for CCW.
##

import argparse
import atexit
import os
import signal
import subprocess
import sys
import tempfile
import time
import RPi.GPIO as GPIO

##
# Project name.
##
PROJECT = os.path.splitext(os.path.basename(__file__))[0]

##
# Pin numbers for the clockwise button and counter-clockwise button.
PINCW = 4
PINCCW = 27

##
# Capture the time between button presses.
# 
# Unit: seconds
##
EVENT_THRESHOLD_TIME = 1
EVENT_FILE = ''

##
# Log.
##
LOG_FILE = ''

def cleanup_handler(signum=None, frame=None):
    '''
    Cleanup the GPIO.
    '''

    if os.path.isfile(EVENT_FILE):
        os.remove(EVENT_FILE)

    #GPIO.cleanup()
    sys.exit(signum)
    return

def is_already_running():
    '''
    Return True if this process is already running, and False otherwise.
    '''

    tmpdir = '/tmp/'
    for f in os.listdir(tmpdir):
        if not os.path.isfile(tmpdir+f):
            continue

        if f.startswith(PROJECT):
            return True
    return False

def is_event_time():
    '''
    Check if a button has been pressed and, more importantly, that it has not
    been pressed too quickly.
    '''

    with open(EVENT_FILE, 'r') as handle:
        try:
            previous = float(handle.read())
        except ValueError:
            previous = 0
        current = time.time()

        print "Current : %d || Event : %d || Diff : %d" % (current, previous, current-previous)
        if ((current - previous) < EVENT_THRESHOLD_TIME):
            return False
    return True

def main():
    '''
    Wait for a button to be pressed.
    '''

    global LOG_FILE

    if is_already_running():
        return

    parser = argparse.ArgumentParser(prog=PROJECT)
    parser.add_argument('-o', '--output', action='store', default='',
        help='Output file to write to.')
    args = parser.parse_args()
    LOG_FILE = args.output

    setup_event_file()
    setup_signal_handler()
    setup_gpio()
    wait_for_button_press()
    return

def print_output(message):
    '''
    Print the output to stdout or to the log file.
    '''

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    output = '[{0}] {1}'.format(timestamp, message)

    if LOG_FILE:
        with open(LOG_FILE, 'a+') as handle:
            handle.write('{0}\n'.format(output))
    else:
        print output
    return

def run_feeder(pin):
    '''
    Run the cat feeder.
    '''

    if pin == PINCW:
        print_output('Running the feeder (CW).')
        cmd = ["~/projects/catfeeder/catfeeder.py -t 0.15 -d  CW >> ${HOME}/catfeeder.txt"]
    elif pin == PINCCW:
        print_output('Running the feeder (CCW).')
        cmd = ["~/projects/catfeeder/catfeeder.py -t 0.15 -d CCW >> ${HOME}/catfeeder.txt"]
    else:
        return

    if not is_event_time():
        return

    set_event_time()
    subprocess.Popen(cmd, shell=True)
    return

def set_event_time():
    '''
    Set the time of button press event.
    '''

    with open(EVENT_FILE, 'w') as handle:
        handle.write(str(time.time()))
    return

def setup_event_file():
    '''
    Setup the event file, which will contain the time at which button press
    events occur.
    '''

    global EVENT_FILE
    handle, EVENT_FILE = tempfile.mkstemp(prefix='{0}_'.format(PROJECT),
        suffix='.txt')
    os.close(handle)
    return

def setup_gpio():
    '''
    Setup the GPIO pins.
    '''

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PINCW, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PINCCW, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(PINCW, GPIO.RISING, run_feeder)
    GPIO.add_event_detect(PINCCW, GPIO.RISING, run_feeder)
    return

def setup_signal_handler():
    '''
    Setup the signal handlers to properly cleanup the GPIOs.
    '''

    signal.signal(signal.SIGTERM, cleanup_handler)
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGHUP, cleanup_handler)
    signal.signal(signal.SIGQUIT, cleanup_handler)
    atexit.register(GPIO.cleanup)
    return

def wait_for_button_press():
    '''
    Wait for a button to be pressed.
    '''

    while True:
        print_output('Waiting for button presses.')
        time.sleep(600)
    return

if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
