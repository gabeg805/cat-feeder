#!/usr/bin/env python3
# 
# NAME
#     catfeeder.py
# 
# SYNOPSIS
#     catfeeder.py [options] <args>
# 
# DESCRIPTION
#     Run a servo motor to dispense food from a cat feeder.
# 
# AUTHOR
#     Gabriel Gonzalez
# 

import argparse
import logging
import os
import requests
import sys
import tempfile
import time
import RPi.GPIO as GPIO
from RpiMotorLib import rpiservolib
from logging.handlers import RotatingFileHandler

# Servo pin number and frequency
SERVO_PIN  = 18
SERVO_FREQUENCY = 50

# Skip indicator information
SKIP_INDICATOR_DIRECTORY = os.path.join(os.getenv('HOME'), ".config", "catfeeder")
SKIP_INDICATOR_PREFIX = 'skip_catfeeder'

# Create the logger
logger = logging.getLogger(__name__)

def cleanup_skip_indicator_file(addr=''):
	'''
	Cleanup a skip indicator file that would have skipped the next feeding time.
	'''

	logger.info("Cleaning up a skip indicator file.")

	# Send message
	if addr:
		message = "Skipped feeding time"
		timestamp = time.strftime("%b %d, %-I:%M %p")
		notifyMessage = f"**{message}**\n{timestamp}"

		send_message(addr, notifyMessage)

	# Remove the skip file
	filepath = find_skip_indicator_file()

	if filepath:
		try:
			logger.info(f"Cleaning up skip indicator file : {filepath}")
			os.remove(filepath)
		except OSError as e:
			logger.exception(exc_info=e)

	# Skip file not found
	else:
		logger.warning("No skip indicator file found to cleanup.")

	return

def create_skip_indicator_file():
	'''
	Create a file that acts as an indicator to skip the next feeding time.
	'''

	logger.info("Creating a skip indicator file so that the next feeding time is skipped.")

	# Make the directory if it does not exist
	if not os.path.isdir(SKIP_INDICATOR_DIRECTORY):
		logger.info(f"Creating directory where skip indicator files will be made : {SKIP_INDICATOR_DIRECTORY}")
		os.makedirs(SKIP_INDICATOR_DIRECTORY, mode=0o775)

		# Change the permissions in case above did not work
		try:
			os.chmod(SKIP_INDICATOR_DIRECTORY, 0o775)
		except OSError as e:
			logger.exception(exc_info=e)

	# Make temporary file (skip indicator file)
	tempfile.mkstemp(prefix=f'{SKIP_INDICATOR_PREFIX}_', suffix='.txt', dir=SKIP_INDICATOR_DIRECTORY)
	return

def find_skip_indicator_file():
	'''
	Get the file path to a skip indicator file.

	Returns:
		str: The file path to a skip indicator file.
	'''

	# Directory does not exist
	if not os.path.isdir(SKIP_INDICATOR_DIRECTORY):
		return ''

	# Iterate over each file in the directory
	for a in os.listdir(SKIP_INDICATOR_DIRECTORY):
		filepath = os.path.join(SKIP_INDICATOR_DIRECTORY, a)

		# Check if the file is a file (not a directory) and has the skip indicator
		# naming convention in it
		if os.path.isfile(filepath) and SKIP_INDICATOR_PREFIX in a:
			return filepath

	# Unable to find a skip indicator file
	return ''

def main():
	'''
	Main for cat feeder.
	'''

	# Setup the arg parser and logger
	parser = setup_argument_parser()
	args = parser.parse_args()
	logger = setup_logger(logFile=args.log_file)

	# Help
	if len(sys.argv) == 1:
		parser.print_help()
		return 0

	# Log parameters
	logger.info(f"angle       = {args.angle}")
	logger.info(f"notify_addr = {args.notify_addr}")
	logger.info(f"skip        = {args.skip}")
	logger.info(f"unskip      = {args.unskip}")
	logger.info(f"log_file    = {args.log_file}")

	# Skip feeding
	if args.skip:
		create_skip_indicator_file()
		return 0

	# Unskip feeding
	elif args.unskip:
		cleanup_skip_indicator_file()
		return 0

	# Feeding should be skipped instead of dispensing food because a skip indicator
	# file was found
	elif find_skip_indicator_file():
		cleanup_skip_indicator_file(addr=args.notify_addr)
		return 0

	# Invalid angle
	elif abs(args.angle) < 0 or abs(args.angle) > 360:
		logger.error(f"Invalid angle : {args.angle}. Allowed angles are +/- 0 to 360 degrees.")
		return 4

	# Create the servo object
	servo = rpiservolib.SG90servo("servoone", SERVO_FREQUENCY)

	# Run the servo
	return run(servo, args.angle)

def run(servo, angle):
	'''
	Run the cat feeder.
	'''

	##
	# 7.8 = 90 deg
	# 8.3 = 180 deg
	##
	# Didn't move from 6.9 - 7.35
	#
	##
	# CCW
	# 
	# 7.7-7.9 = 45 deg
	# 
	# 8.3-8.4 = 90 deg
	##
	# CW
	# 
	# 6.35 - 6.45 = 45 deg
	# 
	# 5.8 - 6 = 90 deg
	# 

	logger.info("Dispensing food.")

	# Spin CCW
	if angle > 0:
		for a in range(0, angle, 90):
			# 90
			servo.servo_move(SERVO_PIN, position=8.3, verbose=True)
			# 45
			#servo.servo_move(SERVO_PIN, position=7.7, verbose=True)

	# Spin CW
	elif angle < 0:
		for a in range(0, -angle, 90):
			# 90
			servo.servo_move(SERVO_PIN, position=6.4, verbose=True)
			# 45
			#servo.servo_move(SERVO_PIN, position=5.9, verbose=True)

	# Cleanup GPIOs
	GPIO.cleanup()

	return 0

def send_message(addr, message):
	'''
	Send a message to a ntfy.sh address.
	'''

	# Invalid address
	if not addr:
		return

	logger.info(f"Sending message : {message.replace('\n', ' - ')}")

	# Send message
	response = requests.put(
		addr,
		data=message,
		headers= {
			"Markdown" : "yes",
			"Tags": "no_entry_sign",
		},
	)

	return

def setup_argument_parser():
	"""
	Setup the argument parser.

	Returns:
		argparse.ArgumentParser: The argument parser.
	"""

	# Create the parser
	parser = argparse.ArgumentParser(
		prog=os.path.basename(sys.argv[0]),
		description='Cat food dispenser that drives a servo motor to dispense food.'
	)

	# Add arguments
	parser.add_argument('-a', '--angle',
		default='45',
		type=int,
		help='Amount of time the motor should run for.')

	parser.add_argument('-l', '--log-file',
		default='',
		help='Log file to write to.')

	parser.add_argument('-n', '--notify-addr',
		default='',
		help='Notify any issues or snapshots to this ntfy.sh address.')

	parser.add_argument('-S', '--skip',
		action='store_true',
		help='Skip the next scheduled feeding task.')

	parser.add_argument('-U', '--unskip',
		action='store_true',
		help='Unskip the next scheduled feeding task.')

	return parser

def setup_logger(
		logFile="",
		logFmt="[%(asctime)s]  %(levelname)s  %(message)s",
		dateFmt="%Y-%m-%d %I:%M:%S %p",
		level=logging.INFO,
		maxBytes=1000000,
		backupCount=2,
		encoding="utf-8"
	):
	"""
	Setup the logger.

	Args:
		logFile (str, optional): Path to the log file. If empty, messages will
			be printed in the console. [Default=""]
		logFmt (str, optional): Format of log messages.
		dateFmt (str, optional): Date format for the date in the log messages.
		level (int, optional): Log level to use. [Default=logging.INFO]
		maxBytes (int, optional): Max number of bytes before the log file is rotated.
			[Default=1000000]
		backupCount (int, optional): Max number of backup files for the rotating log.
			[Default=3]
		encoding (str, optional): Encoding to use for the log file. [Default="utf-8"]

	Returns:
		logging.Logger: The logger.
	"""

	# Create the logger and formatter
	formatter = logging.Formatter(
		fmt=logFmt,
		datefmt=dateFmt
	)

	# Log messages will be sent to rotating file
	if logFile:
		handler = RotatingFileHandler(
			logFile,
			maxBytes=maxBytes,
			backupCount=backupCount,
			encoding=encoding
		)

	# Messages will be printed to the console
	else:
		handler = logging.StreamHandler()

	# Setup the logger
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	logger.setLevel(level)

	return logger

if __name__ == '__main__':
	ret = main()
	sys.exit(ret)
