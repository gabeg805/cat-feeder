# Cat Feeder

Feed your cat (or dog) by driving a servo motor, which in turn, twists the knob on a
cereal dispenser, allowing dry food to be released.

## Requirements

* [RpiMotorLib](https://github.com/gavinlyonsrepo/RpiMotorLib)

## Installation

**1.** Install RpiMotorLib:

```
sudo apt install python3-rpi-lgpio
```

**2.** Clone the repo:

```
git clone https://github.com/gabeg805/cat-feeder
```

> [!NOTE]
> Ensure the `SERVO_PIN` variable in `catfeeder.py` matches the same pin in
> your setup.

## Usage

### Run the servo motor

Allowed angles are +/- 0 to 360 degrees.

```
catfeeder.py --angle=<ANGLE>
```
  
<!-- Dummy comment -->
*****
<!-- Dummy comment -->
  
### Run the servo motor, and if this run is meant to be skipped, send a message to an [ntfy.sh](https://ntfy.sh) address

```
catfeeder.py --angle=<ANGLE> --notify-addr=<ADDRESS>
```

<!-- Dummy comment -->
*****

### Skip the next time the motor is run

You may want to skip, as an example, if you are giving your cat wet food, and
you do not need the dry food dispensed.

```
catfeeder.py --skip
```
  
<!-- Dummy comment -->
*****
  
### Undo a previous skip that was run

```
catfeeder.py --unskip
```
  
<!-- Dummy comment -->
_____
<!-- Dummy comment -->
  
### Log output to a file

For any of the above commands, if you want to send the printed output to a log
file instead, simply add the `--log-file=<LOG_FILE>` option to the command
line.

## Uninstall

Remove the repo:

```
rm -rf cat-feeder/
```
