#!/usr/bin/env python
# ******************************************************************************
# 
# NAME
#	  catfeeder.py
# 
# DESCRIPTION
#	  Run the servo motor to dispense food from the feeder.
# 
# SYNTAX
#	  catfeeder.py [options] <args>
# 
# AUTHOR
#	  Gabriel Gonzalez
# 
# NOTES
#	  None.
# 
# ******************************************************************************

import __init__
import argparse
import motor.servo
import os
import personal.util
import sys
import tempfile
import time

##
# Project name.
##
PROJECT = os.path.basename(sys.argv[0])

##
# Pin number of the motor.
##
PIN  = 18

##
# Exit statuses.
##
ESERVO = 2
EDIRECTION = 3

def check_direction(direction):
	'''
	Check the direction that was provided to ensure it is valid.
	'''

	direction = direction.lower()
	if direction != 'cw' and direction != 'ccw':
		print "%s: Invalid spin direction '%s'. Allowed spins are 'CW' or 'CCW'." \
			% (PROJECT, direction.upper())
		return False
	else:
		return True

def check_servo(servo):
	'''
	Check that the servo is ready to be run.
	'''

	if not servo.is_pin():
		print "%s: Invalid circuit board pin '%s'." % (PROJECT, servo.get_pin())
		return False

	if not servo.is_duration():
		print "%s: Invalid time to keep feeder motor spinning '%s'." \
			% (PROJECT, servo.get_duration())
		return False

	return True

def get_recent_skip_indicator():
	'''
	Return the file path to the most recent skip indicator.
	'''

	tmpdir = '/tmp'
	naming = get_skip_indicator_naming_convention()

	for a in os.listdir(tmpdir):
		filepath = os.path.join(tmpdir, a)
		if os.path.isfile(filepath) and naming in a:
			return filepath
	return ''

def get_skip_indicator_naming_convention():
	'''
	Return the naming convention for the skip indicator.
	'''

	return 'skip_catfeeder'

def is_clockwise(direction):
	'''
	Return True if the direction is clockwise, and False otherwise.
	'''

	direction = direction.lower()
	return direction == 'cw'

def is_counter_clockwise(direction):
	'''
	Return True if the direction is counter-clockwise, and False otherwise.
	'''

	direction = direction.lower()
	return direction == 'ccw'

def main():
	'''
	Main for cat feeder.
	'''

	parser = argparse.ArgumentParser(prog=PROJECT)
	parser.add_argument('-d', '--direction', action='store', default='CCW',
		help='Direction the motor should spin in (either "CW" or "CCW").')
	parser.add_argument('-e', '--email', action='store', default='',
		help='Email any issues to the given email address.')
	parser.add_argument('-o', '--output', action='store', default='',
		help='Output file to write to.')
	parser.add_argument('-s', '--skip', action='store_true',
		help='Skip the next scheduled feeding task.')
	parser.add_argument('-t', '--time', action='store', default='0.2',
		help='Amount of time the motor should run for.')
	parser.add_argument('-u', '--unskip', action='store_true',
		help='Unskip the next scheduled feeding task.')
	args = parser.parse_args()
	output = args.output

	if len(sys.argv) == 1:
		parser.print_help()
		return 0
	elif args.skip:
		skip_feeding_task_setup(output=output)
		return 0
	elif args.unskip:
		unskip_feeding_task(output=output)
		return 0
	elif should_skip_feeding_task():
		skip_feeding_task_cleanup(email=args.email, output=output)
		return 0
	else:
		pass

	direction = args.direction
	duration = args.time
	servo = motor.servo.ServoMotor(PIN, duration=duration)

	if not check_servo(servo):
		return ESERVO
	elif not check_direction(direction):
		return EDIRECTION
	else:
		return run(servo, direction, output=output)

def print_output(message, filepath=''):
	'''
	Print the output to stdout or to the designated filepath, if one is specified.
	'''

	if filepath:
		with open(filepath, 'a+') as handle:
			handle.write('{0}\n'.format(message))
	else:
		print message
	return

def run(servo, direction, output=''):
	'''
	Run the cat feeder.
	'''

	if is_clockwise(direction):
		servo.run_cw()
	elif is_counter_clockwise(direction):
		servo.run_ccw()
	else:
		return EDIRECTION

	message = "[%s] Food dispensed." % time.strftime("%Y-%m-%d %H:%M:%S %Z")
	print_output(message, filepath=output)
	return 0

def should_skip_feeding_task():
	'''
	Return True if the feeding task should be skipped, and False otherwise.
	'''

	filepath = get_recent_skip_indicator()
	return len(filepath) > 0

def skip_feeding_task_cleanup(email='', output=''):
	'''
	Cleanup the most recent indicator to skip the next scheduled feeding task.
	'''

	message = "Scheduled feeding task has been skipped."
	timestamp = time.strftime("%Y-%m-%d %H:%M:%S %Z")
	timestampedMessage = "[{0}] {1}".format(timestamp, message)
	filepath = get_recent_skip_indicator()

	print_output(timestampedMessage, filepath=output)
	email_message(email, timestampedMessage)

	if filepath:
		os.remove(filepath)
	return

def email_message(email, message):
	'''
	Email the message to the given email address.
	'''

	command = 'echo "{0}" | /usr/bin/mail -s "Cat Feeder" "{1}"'.format(message, email)
	print command
	os.system(command)
	return

def skip_feeding_task_setup(output=''):
	'''
	Create a file that acts as an indicator to skip the next scheduled feeding task.
	'''

	message = "[%s] Preparing to skip the next scheduled feeding task." \
		% time.strftime("%Y-%m-%d %H:%M:%S %Z")
	print_output(message, filepath=output)

	tmpdir = '/tmp'
	naming = get_skip_indicator_naming_convention()
	tempfile.mkstemp(prefix='{0}_'.format(naming), suffix='.txt', dir=tmpdir)
	return

def unskip_feeding_task(output=''):
	'''
	Unskip the most recent indicator that would have skipped the next scheduled
	feeding task.
	'''

	message = "[%s] Unskipping the next scheduled feeding task." \
		% time.strftime("%Y-%m-%d %H:%M:%S %Z")
	print_output(message, filepath=output)

	filepath = get_recent_skip_indicator()
	if filepath:
		os.remove(filepath)
	return

if __name__ == '__main__':
	ret = main()
	sys.exit(ret)
