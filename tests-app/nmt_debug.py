# -*- coding: utf-8 -*-

from common import *
import time
import pytest
import canopen
from start_app import node_id as start_node_id
from start_app import main as start_app


#  OPERATIONAL
#  STOPPED
#  PRE-OPERATIONAL


class TestNMT(object):
    @classmethod
    def setup_class(cls):
        start_app()
        cls.network = create_network()
        cls.node_id = 36

        # lss prepare node
        lss_waiting_state(cls.network)
        cls.node = canopen.RemoteNode(cls.node_id, 'SCTB_CANopenPressureSensor0xC001.eds')
        cls.node.associate_network(cls.network)

    def _setDeviceBitrate(self, bitrate):
        grade = speed_map[bitrate]
        try:
            self.network.lss.configure_bit_timing(grade)
            self.network.lss.store_configuration()
            self.network.lss.activate_bit_timing(100)
            return True
        except canopen.lss.LssError:
            return False

    def _reset_delay(self):
        time.sleep(0.5)

    def test_reset_all(self):  # <--- todo
        self.network.nmt.state = 'RESET'
        self._reset_delay()
        lss_set_node_id(self.network, self.node_id)
        self.node.nmt.wait_for_bootup(1)
        assert self.node.nmt.state == 'PRE-OPERATIONAL'