#!/usr/bin/bash

~/modpoll -t 0 \
    -b 57600 \
    -o 0.3 \
    -1 \
    -c 1 \
    -r 0x31 \
    -m rtu \
    -a 4 \
    -p none \
    /dev/ttyUSB0 \
    1