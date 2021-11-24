#!/bin/bash

parentdir="${HOME}/web/catfeeder"
notpaths=

# Cycle through past 2 weeks
for cycle in $(seq 0 14)
do

	datedir=$(date -d "now - ${cycle} days" +"%Y/%m/%d")
	datestring=$(date -d "now - ${cycle} days" +"%b %d %Y")
	outputdir="${parentdir}/${datedir}"
	outputname=$(date -d "now - ${cycle} days" +"%Y%m%d_")

	if [ ! -d "${outputdir}" ]
	then
		continue
	fi

	notpaths="! -name \"*${outputname}*\" ${notpaths}"

	#if [ ${cycle} -gt 0 ]
	#then
	#	echo
	#fi

	#echo ":: Syncing date '${datestring}'"

	#rsync --delete --ignore-existing -ahvze 'ssh -p 27184' \
	#	"${outputdir}"/*.webp \
	#	admin@74.96.225.37:/var/www/html/img/

done

find /var/www/html/img -type f ${notpaths}
