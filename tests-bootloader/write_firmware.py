#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import *
import canopen
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description='CAN DDT firmware updater')

    parser.add_argument('-eds', type=str, required=True, help="EDS file")
    parser.add_argument('-N', type=int, required=True, help="target Node ID")
    parser.add_argument('-f', type=str, required=True, help="Firmware image")

    args = parser.parse_args()

    if not os.path.exists(args.f):
        print('Firmware image file "{}" not found!'.format(args.f))
        exit(1)

    if not os.path.exists(args.eds):
        print('EDS file "{}" not found!'.format(args.eds))
        exit(1)

    _, ext = os.path.splitext(args.f)
    if ext == '.deploy':
        encrypted = 1
        print("Encrypted image found")
    else:
        encrypted = 0
        print("Raw image found")

    nw = canopen.Network()
    nw.connect(channel='can0', bustype='socketcan')

    node = canopen.RemoteNode(args.N, args.eds)
    node.associate_network(nw)

    with open(args.f, 'rb') as f:
        fm = f.read()

    node.sdo[0x1f55][1].raw = encrypted
    with node.sdo[0x1f50][1].open('wb', size=len(fm), block_transfer=False) as f:
        f.write(fm)

    if Error_CODE(node.sdo[0x1003][1].raw).code != Error_CODES.APPLICATION_READY_TO_START:
        raise RuntimeError('Write failed')


if __name__ == '__main__':
    main()

