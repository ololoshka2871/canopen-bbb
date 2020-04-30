# -*- coding: utf-8 -*-

import pytest
import canopen
from common import *
import time


class TestLSSBitrates(object):
    @classmethod
    def setup_class(cls):
        set_interface_bitrate(default_bitrate)
        nw = create_network()
        nw.nmt.state = 'RESET'
        nw.disconnect()
        time.sleep(0.1)

    @staticmethod
    def _setDeviceBitrate(network, bitrate):
        grade = speed_map[bitrate]
        try:
            network.lss.configure_bit_timing(grade)
            network.lss.store_configuration()
            network.lss.activate_bit_timing(100)
            return True
        except canopen.lss.LssError:
            return False

    @pytest.mark.parametrize("bitrate,result",
        [(1000000, False),
         (800000, False),
         (500000, False),
         (250000, False),
         (125000, True),
         (50000, True),
         (20000, True),
         (10000, True),
         (default_bitrate, True)
         ])
    def testBitrate(self, bitrate, result):
        network = create_network()
        lss_waiting_state(network)

        lss_configuration_state(network)
        assert self._setDeviceBitrate(network, bitrate) == result
        network.disconnect()

        if result:
            set_interface_bitrate(bitrate)
