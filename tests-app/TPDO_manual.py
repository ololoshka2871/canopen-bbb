#!/usr/bin/env python
# -*- coding: utf-8 -*-


from common import *
from ODEntry import ODEntry
import argparse
import canopen
import time
import datetime
import sys

first_result = True


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


def reset_com_if_nessucery(node):
    error_flags = node.sdo[0x1001].raw
    if error_flags != 0:
        print('Node has errors: {}, resetting communication'.format(error_flags))
        node.nmt.state = 'RESET COMMUNICATION'
        node.nmt.wait_for_bootup()


def create_table_header(msg):
    columns = [res.name for res in msg]
    print('Date;{}'.format(';'.join(columns)))


def print_result(msg):
    results = [res.raw for res in msg]
    now = datetime.datetime.now()
    nowfmt = now.strftime('%Y-%m-%dT%H:%M:%S') + ('-%02d' % (now.microsecond / 10000))

    print('{};{}'.format(nowfmt, ';'.join(map(str, results))))


def tpdo_cb(msg):
    global first_result
    if first_result:
        create_table_header(msg)
        first_result = False
    print_result(msg)


def add_tpo_variable(tpdo, index):
    entry = ODEntry.parce(index)
    print('Mapping {}...'.format(entry))
    if entry.subindex is None:
        tpdo.add_variable(entry.index)
    else:
        tpdo.add_variable(entry.index, entry.subindex)


def do_reading(node, sync_period):
    print('Start reading...')
    node.nmt.state = 'OPERATIONAL'
    if sync_period > 0:
        node.network.sync.start(sync_period)
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        pass
    node.network.sync.stop()
    node.nmt.state = 'PRE-OPERATIONAL'


def main():
    parser = argparse.ArgumentParser(description='Can Open manual TPDO reader',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog='''Example:
\t{0} --nodeid 16 --eds myeds.eds --tpdo 1 2501sub1
\t{0} --nodeid 16 --eds myeds.eds --tpdo 1 --noconfig
'''.format(sys.argv[0]))
    parser.add_argument('-N', '--nodeid', required=True, type=int, help='Node ID to connect to')
    parser.add_argument('--eds', required=True, type=str, help='Device electronic datasheet')
    parser.add_argument('-T', '--tpdo', required=True, type=int, help='TPDO number to use')
    parser.add_argument('-Y', '--noconfig', default=False, action="store_true",
                        help="Skip configuration, allrady have correct, or readonly")
    parser.add_argument('-t', '--transtype', default=254, type=int, help="TPDO transmission type")
    parser.add_argument('--event_timer', type=int, default=100, help="TPO event timer value, ms")
    parser.add_argument('-S', '--sync', type=float, default=0, help='SYNC period')
    parser.add_argument('index', type=str, nargs='?', help='Indexes of mapped objects (1234sub1)')
    args = parser.parse_args()

    node = prepare_node(args.nodeid, args.eds)

    reset_com_if_nessucery(node)

    assert args.tpdo > 0

    node.tpdo.read()
    tpdo = node.tpdo[args.tpdo]
    if not args.noconfig:
        if 1 <= args.transtype <= 0xF0:
            assert args.sync > 0

        tpdo.clear()

        for index in args.index:
            add_tpo_variable(tpdo, index)

        tpdo.trans_type = args.transtype
        tpdo.event_timer = args.event_timer
        tpdo.enabled = True

        node.tpdo.save()

    tpdo.add_callback(tpdo_cb)

    do_reading(node, args.sync)

    tpdo.clear()
    close(node)


if __name__ == '__main__':
    main()
