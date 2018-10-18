
import pytest
import canopen
from common import *


class TestLSSBitrates(object):
    @classmethod
    def setup_class(cls):
        set_interface_bitrate(10000)
        cls.network = None

    def _setDeviceBitrate(self, bitrate):
        grade = speed_map[bitrate]
        try:
            self.network.lss.configure_bit_timing(grade)
            self.network.lss.store_configuration()
            self.network.lss.activate_bit_timing(100)
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
         (10000, True)])
    def testBitrate(self, bitrate, result):
        self.network = create_network()
        lss_waiting_state(self.network)

        lss_configuration_state(self.network)
        assert self._setDeviceBitrate(bitrate) == result
        self.network.disconnect()

        if result:
            set_interface_bitrate(bitrate)
