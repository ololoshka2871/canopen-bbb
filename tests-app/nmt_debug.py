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

    def test_reset_all(self):
        self.network.nmt.state = 'RESET'
        self._reset_delay()
        lss_set_node_id(self.network, self.node_id)
        self.node.nmt.wait_for_bootup(1)
        assert self.node.nmt.state == 'PRE-OPERATIONAL'

    def test_new_speed_reset_comm(self):
        test_speed = 50000

        # set new speed
        lss_configure_node(self.network, self.node_id, test_speed)
        # apply and restart communication
        self.network.nmt.state = 'RESET COMMUNICATION'

        # apply host speed
        self.network.disconnect()
        set_interface_bitrate(test_speed)

        # reconnect
        self.network = create_network()
        self.node.associate_network(self.network)

        assert self.node.sdo[0x1200][0].raw is not None

    def test_goto_bootloader(self):
        self.network.nmt.state = 'STOPPED'

