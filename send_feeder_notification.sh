#!/bin/bash
# 
# NAME
#	  send_feeder_notification.sh
# 
# SYNOPSIS
#	  send_feeder_notification.sh --addr <ADDRESS> --latest
#	  send_feeder_notification.sh --addr <ADDRESS> --montage
# 
# DESCRIPTION
#	  Send a notification showing a either the latest picture of the cat
#	  feeder, or a montage of pictures before and after the cat feeder is run.
#	  This notification must be sent to a ntfy.sh address.
# 
# AUTHOR
#	  Gabriel Gonzalez
# 

##
# Print program usage.
##
usage()
{
    echo "Usage: ${PROJECT} --addr <ADDRESS> --latest"
    echo "       ${PROJECT} --addr <ADDRESS> --montage"
    echo 
    echo "Options:"
    echo "    -h, --help"
    echo "        Print program usage."
    echo 
    echo "    -a, --addr=<ntfy.sh address>"
    echo "        A ntfy.sh address to send the image to."
    echo 
    echo "    -l, --latest"
    echo "        Send the latest image that was taken."
    echo 
    echo "    -m, --montage"
    echo "        Send a montage image consisting of images from the 59th, onwards to the"
	echo "        4th minute. As an example, images from 8:59, 9:00, 9:01, 9:02, 9:03,"
	echo "        and 9:04am."
}

# Project name
PROJECT="${0##*/}"

# Input directory where images are
INPUT_DIR="${HOME}/projects/katty/static/pics/feeder"

# Output directory for montages
MONTAGE_OUTPUT_DIR="${HOME}/projects/katty/static/pics/montage"

# Path to an output file to send
OUTPUT_PATH=

# Ntfy.sh address
NTFY_ADDR=

# Send montage or latest image
SEND_MONTAGE=
SEND_LATEST=

# Print usage and exit
if [ $# -eq 0 ]
then
	usage
	exit 0
fi

# Short and long options
short="a:lmh"
long="addr:,latest,montage,help"

# Parse options
args=$(getopt --options "${short}" --long "${long}" --name "${PROJECT}" -- "${@}")

if [ $? -ne 0 ]
then
	# An error occurred so print the usage and exit
	usage
	return 1
fi

eval set -- "${args}"

# Iterate over each option
while true
do
	case "${1}" in

		# Help
		-h|--help)
			usage
			return 0
			;;

		# Address
		-a|--addr)
			shift
			NTFY_ADDR="${1}"
			;;

		# Latest
		-l|--latest)
			shift
			SEND_LATEST=true
			;;

		# Montage
		-m|--montage)
			shift
			SEND_MONTAGE=true
			;;

		*)
			break
			;;
	esac
	shift
done

# Latest image
if [ -n "${SEND_LATEST}" ]
then
	# Define the output path
	OUTPUT_PATH=$(find "${INPUT_DIR}" -type f -printf "%T@ %p\n" \
		| sort -n | tail -1 | cut -f 2 -d ' ')

# Montage of images
elif [ -n "${SEND_MONTAGE}" ]
then
	# Input name of the files to use in the montage
	inputName=$(date +"%Y-%m-%d_%H")
	inputNameMinusHour=$(date -d "-1 hour" +"%Y-%m-%d_%H59")

	# Define the output path
	OUTPUT_PATH="${MONTAGE_OUTPUT_DIR}"/$(date +"%Y-%m-%d_%H0000.jpg")

	# Create the montage
	montage "${INPUT_DIR}/${inputNameMinusHour}"*.jpg "${INPUT_DIR}/${inputName}"*.jpg \
		-tile 1x6 -geometry +5+5 -background "#000000" "${OUTPUT_PATH}"

# Unknown
else
	exit 2
fi

# Send notification to ntfy.sh address
title=$(date +"%b %d @ %-I%p")

curl \
	-H "Title: ${title}" \
	-H "Tags: cat" \
	-H "Content-Type: image/jpeg" \
	-H "Filename: $(basename ${OUTPUT_PATH})" \
	-T "${OUTPUT_PATH}" \
	"${NTFY_ADDR}"

