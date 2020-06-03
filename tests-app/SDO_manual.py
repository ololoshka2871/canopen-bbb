#!/usr/bin/env python
# -*- coding: utf-8 -*-


from common import *
from ODEntry import ODEntry
import argparse
import canopen
import ast
import sys


def prepare_node(node_id, eds_file):
    network = create_network()
    node = canopen.RemoteNode(node_id, eds_file)
    node.associate_network(network)
    node.nmt.state = 'PRE-OPERATIONAL'
    return node


def close(node):
    nw = node.network
    node.remove_network()
    nw.disconnect()


def read_index(node, index):
    entry = ODEntry.parce(index)
    v = entry.getvalue(node.sdo)
    return v, type(v)


def write_index(node, index, val):
    entry = ODEntry.parce(index)
    entry.setvalue(node.sdo, val)


def main():
    parser = argparse.ArgumentParser(description='Can Open manual SDO operator',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog='''
Example:
\t{0} --nodeid 42 --eds myeds.eds 2501sub1
\t{0} --nodeid 42 --eds myeds.eds -W 100 2300sub1'''.format(sys.argv[0]))
    parser.add_argument('-N', '--nodeid', required=True, type=int, help='Node ID to connect to')
    parser.add_argument('--eds', required=True, type=str, help='Device electronic datasheet')
    parser.add_argument('-W', '--write', help='Write value')
    parser.add_argument('index', type=str, nargs='+', help='Indexes of mapped objects (1234sub1)')
    args = parser.parse_args()

    node = prepare_node(args.nodeid, args.eds)

    if args.write:
        value = args.write
        index = args.index[0]
        print('Writing {} to {}'.format(value, index))
        write_index(node, index, value)
    else:
        for index in args.index:
            val, t = read_index(node, index)
            print('{} = {} {}'.format(index, val, t))

    close(node)


if __name__ == '__main__':
    main()
