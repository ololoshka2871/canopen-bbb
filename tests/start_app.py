#!/usr/bin/env python

from common import *
import canopen


node_id = 42

nw = create_network()

lss_waiting_state(nw)
lss_configuration_state(nw)
lss_set_node_id(nw, node_id)
lss_waiting_state(nw)

node = canopen.RemoteNode(node_id, 'Bootloader.eds')
node.associate_network(nw)
bootloader_start_app(node)
