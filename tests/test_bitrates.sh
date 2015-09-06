#!/bin/bash

if [[ $# -eq 1 ]]; then
    INTERFACE=$1
else
    INTERFACE=can0
fi

echo "Init $INTERFACE..."
ip link set $INTERFACE down
ip link set $INTERFACE up type can bitrate 10000 loopback off

echo "Initial test"

pytest -s lss.py

if [[ $? -ne 0 ]]; then
    echo "Test failed!"
    exit 1
fi

for speed in 20000 50000 125000
do
    echo "Set device bitrate to $speed..."
    python -c "from set_bitrate import *; set_bitrate($speed)"

    echo "Set device my to $speed..."
    ip link set $INTERFACE down
    ip link set $INTERFACE up type can bitrate $speed loopback off

    pytest -s lss.py

    if [[ $? -ne 0 ]]; then 
        echo "Failed at speed $speed.."
        exit 1
    fi
done
