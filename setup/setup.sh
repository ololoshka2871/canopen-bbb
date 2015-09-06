#!/bin/bash

dtbo_err () {
	echo "Error loading device tree overlay file: $DTBO" >&2
	exit 1
}

pin_err () {
	echo "Error exporting pin:$PIN" >&2
	exit 1
}

dir_err () {
	echo "Error setting direction:$DIR on pin:$PIN" >&2
	exit 1
}

SLOTS=/sys/devices/bone_capemgr.*/slots
OVERLAY=BB-DCAN1-TJA1055

# Make sure required device tree overlay(s) are loaded
for DTBO in $OVERLAY ; do

	if grep -q $DTBO $SLOTS ; then
		echo $DTBO overlay found
	else
		echo Loading $DTBO overlay
		sudo -A su -c "echo $DTBO > $SLOTS" || dtbo_err
		sleep 1
	fi
done;

# Export GPIO pins
# This really only needs to be done to enable the low-level clocks for the GPIO
# modules.  There is probably a better way to do this...
while read PIN DIR JUNK ; do
        case "$PIN" in
        ""|\#*)	
		continue ;;
        *)
		[ -r /sys/class/gpio/gpio$PIN ] && continue
                sudo -A su -c "echo $PIN > /sys/class/gpio/export" || pin_err
		sudo -A su -c "echo $DIR > /sys/class/gpio/gpio$PIN/direction" || dir_err
                ;;
        esac

done <<- EOF
#OUTPUTS
	60	out	# STB
    50  out # EN
    51  out # WAKE

#INPUTS
    2   in  # ERR
EOF

ip link set can0 up type can bitrate 125000 loopback off
./set_tja1055Mode.py 1 1 1
