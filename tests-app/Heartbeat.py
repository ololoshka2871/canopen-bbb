#!/usr/bin/env python
# -*- coding: utf-8 -*-


from common import *
import canopen
import time


def create_hb_cb(node):
    def hb_cb(arg):
        print('HB from {} -> State: {}'.format(node.id, canopen.nmt.NMT_STATES[arg]))
    return hb_cb


def main():
    network = create_network()
    node = canopen.RemoteNode(42, 'SCTB_CANopenPressureSensor0xC001.eds')
    node.associate_network(network)
    node.nmt.add_hearbeat_callback(create_hb_cb(node))

    print('Ready to capture Heartbeat messages, Press CTRL+C to exit')
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        network.disconnect()


if __name__ == '__main__':
    main()
