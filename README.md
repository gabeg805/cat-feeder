# Cat Feeder

Feed your cat (or dog) by driving a servo motor, which in turn, twists the knob on a
cereal dispenser, allowing dry food to be released.

## Requirements

* [RpiMotorLib](https://github.com/gavinlyonsrepo/RpiMotorLib)

## Installation

Clone the repo:

`git clone https://github.com/gabeg805/cat-feeder`

Ensure the `SERVO_PIN` variable in `catfeeder.py` matches the same pin in your setup.

## Usage

Run the servo motor. Allowed angles are +/- 0 to 360 degrees.

`catfeeder.py --angle=<ANGLE>`

Run the servo motor, and if this run is meant to be **skipped** (see the next
example for details), send a message to an [ntfy.sh](https://ntfy.sh) address.

`catfeeder.py --angle=<ANGLE> --notify-addr=<ADDRESS>`

Skip the next time the motor is run. For instance, if you are giving your cat
wet food, and you do not need the dry food dispensed.

`catfeeder.py --skip`

Undo a previous skip that was run. For instance, if it was accidental or what
have you.

`catfeeder.py --unskip`

For any of the above commands, if you want to send the printed output to a log
file, instead, use the `--log-file=<LOG_FILE>` option.

## Uninstall

`rm -rf cat-feeder/`
