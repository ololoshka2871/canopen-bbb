# -*- coding: utf-8 -*-

from common import *
from ODEntry import *
import canopen
import pytest
import time


class TestSDO(object):
    @classmethod
    def setup_class(cls):
        cls.network = create_network()
        cls.node_id = 19
        reset_network(cls.network)

        # lss prepare node
        cls.node = canopen.RemoteNode(cls.node_id, 'SCTB_CANopenPressureSensor0xC001.eds')
        cls.node.associate_network(cls.network)
        lss_waiting_state(cls.network)
        lss_set_node_id(cls.network, cls.node_id)
        cls.node.nmt.wait_for_bootup(0.5)

    @classmethod
    def teardown_class(cls):
        cls.node.nmt.state = 'PRE-OPERATIONAL'
        cls.node.remove_network()
        cls.network.disconnect()

    def test_clear_tpo_config(self):
        self.node.tpdo.read()
        for tpdoN in self.node.tpdo:
            self.node.tpdo[tpdoN].clear()
        self.node.tpdo.save()

    def test_simple_tpdo(self):
        def tpfo_cb(msg):
            print('%s received' % msg.name)
            for var in msg:
                print('-> {} = {}'.format(var.name, var.raw))

        self.node.tpdo.read()
        tpdo = self.node.tpdo[1]
        tpdo.add_variable(0x2500, 1)
        tpdo.add_variable(0x2500, 2)
        tpdo.trans_type = 254
        tpdo.event_timer = 1000
        tpdo.enabled = True
        self.node.tpdo.save()

        tpdo.add_callback(tpfo_cb)
        self.node.nmt.state = 'OPERATIONAL'
        time.sleep(2)
        self.node.nmt.state = 'PRE-OPERATIONAL'
