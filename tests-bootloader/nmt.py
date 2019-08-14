# -*- coding: utf-8 -*-

from common import *
import time
import pytest
import canopen


#  OPERATIONAL
#  STOPPED
#  PRE-OPERATIONAL


class TestNMT(object):
    @classmethod
    def setup_class(cls):
        cls.network = create_network()
        cls.node_id = 42

        # lss prepare node
        lss_waiting_state(cls.network)
        cls.node = canopen.RemoteNode(cls.node_id, 'Bootloader.eds')
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
        time.sleep(0.1)

    def test_reset_com(self):
        lss_set_node_id(self.network, self.node_id)
        self.network.nmt.state = 'RESET COMMUNICATION'
        self.node.nmt.wait_for_bootup(1)

    def test_reset(self):
        lss_set_node_id(self.network, self.node_id)
        self.network.nmt.state = 'RESET'
        self._reset_delay()
        lss_set_node_id(self.network, self.node_id)
        self.node.nmt.wait_for_bootup(1)

    def test_node_reset_com(self):
        lss_set_node_id(self.network, self.node_id)
        self.node.nmt.state = 'RESET COMMUNICATION'
        self.node.nmt.wait_for_bootup(1)

    def test_node_reset(self):
        lss_set_node_id(self.network, self.node_id)
        self.node.nmt.state = 'RESET'
        self._reset_delay()
        lss_set_node_id(self.network, self.node_id)
        self.node.nmt.wait_for_bootup(1)

    def test_node_preop_op(self):
        self.node.nmt.state = 'PRE-OPERATIONAL'
        self.node.nmt.state = 'OPERATIONAL'
        self.node.nmt.state = 'PRE-OPERATIONAL'

    @pytest.mark.parametrize('mode', ['PRE-OPERATIONAL', 'STOPPED', 'PRE-OPERATIONAL'])
    def test_disable_LSS_in_operation_mode(self, mode):
        self.network.nmt.state = 'OPERATIONAL'
        lss_configuration_state(self.network)

        with pytest.raises(canopen.lss.LssError) as e_info:
            self.network.lss.configure_node_id(self.node_id)
            self.network.lss.store_configuration()
        assert str(e_info.value) == 'LSS Error: 2'

        with pytest.raises(canopen.lss.LssError) as e_info:
            self.network.lss.configure_bit_timing(8)
        assert str(e_info.value) == 'LSS Error: 1'

        lss_waiting_state(self.network)
        self.network.nmt.state = 'PRE-OPERATIONAL'

    @pytest.mark.parametrize("test_speed", [125000, 50000, 20000, 10000])
    def test_switch_speed_reset(self, test_speed):
        if not self.network.bus:
            self.network = create_network()

        lss_configure_bit_timing(self.network, test_speed)
        lss_set_node_id(self.network, self.node_id)
        self.network.nmt.state = 'RESET COMMUNICATION'

        self.network.disconnect()
        set_interface_bitrate(test_speed)
        self.network = create_network()
        self.node.associate_network(self.network)

        assert self.node.sdo[0x1f56][1].raw is not None

        self.network.nmt.state = 'RESET'
        self.network.disconnect()
        time.sleep(0.1)
        set_interface_bitrate(10000)
        self.network = create_network()
        lss_set_node_id(self.network, self.node_id)
        self.node.associate_network(self.network)

        assert self.node.sdo[0x1f56][1].raw is not None
        self.network.disconnect()

    @pytest.mark.parametrize("bitrate,result",
                             [(1000000, False),
                              (800000, False),
                              (500000, False),
                              (250000, False),
                              (125000, True),
                              (50000, True),
                              (20000, True),
                              (10000, True)
                              ])
    def test_switch_speed_operational(self, bitrate, result):
        if self.network.bus:
            self.network.disconnect()

        self.network = create_network()
        self.network.nmt.state = 'PRE-OPERATIONAL'
        lss_set_node_id(self.network, self.node_id)

        lss_configuration_state(self.network)
        assert self._setDeviceBitrate(bitrate) == result
        lss_waiting_state(self.network)

        self.network.nmt.state = 'RESET COMMUNICATION'
        self.network.disconnect()
        if result:
            set_interface_bitrate(bitrate)

        self.network = create_network()
        self.node.associate_network(self.network)
        self.network.nmt.state = 'OPERATIONAL'
        assert 4 == self.node.sdo[0x1018][0].raw
        self.network.disconnect()
