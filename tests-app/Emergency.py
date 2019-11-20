#!/usr/bin/env python
# -*- coding: utf-8 -*-


from common import *
import canopen
import time


def create_emcy_cb(node):
    def emcy_cb(arg):
        print('EMCY from {} -> code: 0x{:X}, data: {}, register: 0x{:X}, timestamp: {}'
              .format(node.id, arg.code, arg.data, arg.register, arg.timestamp))
    return emcy_cb


def main():
    network = create_network()
    network.nmt.state = 'OPERATIONAL'
    node = canopen.RemoteNode(42, 'SCTB_CANopenPressureSensor0xC001.eds')
    node.associate_network(network)
    node.emcy.add_callback(create_emcy_cb(node))

    print('Ready to capture EMCY, Press CTRL+C to exit')
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        network.disconnect()


if __name__ == '__main__':
    main()
