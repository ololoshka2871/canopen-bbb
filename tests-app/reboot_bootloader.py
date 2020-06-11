#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import *
import canopen
import argparse
import sys


def main():
    nw = create_network()

    parser = argparse.ArgumentParser(description='Reboot node to bootloader by send NMT STOP',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog='''
Example:
    \t{0} --nodeid 42
    \t{0} --all'''.format(sys.argv[0]))
    parser.add_argument('-N', '--nodeid', type=int, help='Node ID to connect to')
    parser.add_argument('--eds', required=False, type=str, help='Device electronic datasheet')
    parser.add_argument('-A', '--all', default=False, action='store_true',  help='Write value')

    args = parser.parse_args()

    if args.all:
        print("AllNodes -> Stop")
        nw.nmt.state = 'STOPPED'
        pass
    else:
        print("Node {} -> Stop".format(args.nodeid))
        node = canopen.RemoteNode(args.nodeid, args.eds)
        node.associate_network(nw)
        node.nmt.state = 'STOPPED'
        pass


if __name__ == '__main__':
    main()
