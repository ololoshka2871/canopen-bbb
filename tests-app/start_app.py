#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import *
import canopen


node_id = 42


def main():
    nw = create_network()

    lss_waiting_state(nw)
    lss_configuration_state(nw)
    lss_set_node_id(nw, node_id)
    lss_waiting_state(nw)

    node = canopen.RemoteNode(node_id, '../tests-bootloader/Bootloader.eds')
    node.associate_network(nw)
    bootloader_start_app(node)
    nw.disconnect()


if __name__ == '__main__':
    main()
