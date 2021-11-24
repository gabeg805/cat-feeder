#!/bin/bash

outputname=$(date +"%Y%m%d_%H%M00")
outputdir="${HOME}/web/catfeeder/$(date +"%Y/%m/%d")"
hour=$(date +%H)
exposure=50
rotation=180
drc=low
shutter=200000
iso=200

sleep 1
mkdir -pv "${outputdir}"
builtin cd "${outputdir}"

#if [ ${hour} -le 6 -o ${hour} -ge 18 ]
#then
#	raspistill -v -n -t "${exposure}" -rot "${rotation}" -drc "${drc}" \
#		-ss "${shutter}" -ISO "${iso}" -o "${outputname}.jpg"
#else
	drc=off
	shutter=200000
	iso=100
	exposure=20
	awb=auto

	raspistill -v -n -t "${exposure}" -rot "${rotation}" \
		-awb "${awb}" -drc "${drc}" -ss "${shutter}" \
		-o "${outputname}.jpg"
	#raspistill -v -n -t "${exposure}" -rot "${rotation}" -o "${outputname}.jpg"
#fi

cwebp -q 50 "${outputname}.jpg" -o "${outputname}.webp"
rm -f "${outputname}.jpg"
cp -av "${outputname}.webp" /var/www/html/img/
#scp -P 27184 "${outputname}.webp" admin@69.138.194.162:/var/www/html/img/
