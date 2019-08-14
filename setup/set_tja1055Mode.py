#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pin import GPIO
import sys

stb_pin = 60
en_pin = 50
wake_pin = 51


def print_usage():
    print('Usage: {} [STB_STATE] [EN_STATE] [WAKE_STATE]'.format(sys.argv[0]))


def main():
    if '-h' in sys.argv:
        print_usage()
        exit(1)

    STB = GPIO(stb_pin, False)
    EN = GPIO(en_pin, False)
    WAKE = GPIO(wake_pin, False)

    print('Prev pins state: STB={}\tEN={}\tWAKE={}'.format(
        STB.get_val(), EN.get_val(), WAKE.get_val()))
    
    if len(sys.argv) > 1:
        newval = int(sys.argv[1])
        STB.set_val(newval)
    
    if len(sys.argv) > 2:
        newval = int(sys.argv[2])
        EN.set_val(newval)

    if len(sys.argv) > 3:
        newval = int(sys.argv[3])
        WAKE.set_val(newval)

    if len(sys.argv) > 1:
        print('New pins state: STB={}\tEN={}\tWAKE={}'.format(
        STB.get_val(), EN.get_val(), WAKE.get_val()))
    exit(0)


if __name__ == '__main__':
    main() 
