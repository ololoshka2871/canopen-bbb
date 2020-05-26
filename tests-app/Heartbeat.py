#!/usr/bin/env python
# -*- coding: utf-8 -*-


from common import *
import canopen
import time


test_node_id = 42


def create_hb_cb(node):
    def hb_cb(arg):
        print('HB from {} -> State: {}'.format(node.id, canopen.nmt.NMT_STATES[arg]))
    return hb_cb


def main():
    network = create_network()
    node = canopen.RemoteNode(test_node_id, 'SCTB_CANopenPressureSensor0xC001.eds')
    node.associate_network(network)

    reset_network(network)
    lss_set_node_id(network, test_node_id)
    node.nmt.wait_for_bootup(1)

    node.nmt.add_hearbeat_callback(create_hb_cb(node))

    print('Ready to capture Heartbeat messages, Press CTRL+C to exit')
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        network.disconnect()


if __name__ == '__main__':
    main()
