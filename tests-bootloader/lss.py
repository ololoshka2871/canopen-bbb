# -*- coding: utf-8 -*-

import pytest
import canopen
from canopen_lss_fastscan import fast_scan
from common import *
import time


class TestLSS(object):
    @classmethod
    def setup_class(cls):
        set_interface_bitrate(10000)
        cls.network = create_network()
        cls.network.nmt.state = 'RESET'
        time.sleep(0.1)

    @classmethod
    def teardown_class(cls):
        cls.network.disconnect()

    # not working in library
    #def test_identify_remote_slave(network):
    #    assert network.lss.send_identify_remote_slave(vendor_id, product_id,
    #        0, 1, 1, 2)

    def test_set_config_mode(self):
        self.network.lss.send_switch_state_global(self.network.lss.CONFIGURATION_STATE)
        self.network.lss.send_switch_state_global(self.network.lss.WAITING_STATE)

    def test_set_config_mode_by_id(self):
        lss_configuration_state(self.network)
        lss_waiting_state(self.network)

    @pytest.mark.parametrize('speed_grade,result', [
        (0, False),
        (1, False),
        (2, False),
        (3, False),
        (4, True),
        (6, True),
        (7, True),
        (8, True)
    ])
    def test_configure_bit_timing(self, speed_grade, result):
        lss_configuration_state(self.network)

        if result:
            try:
                self.network.lss.configure_bit_timing(speed_grade)
            except canopen.lss.LssError as e:
                self.network.lss.send_switch_state_global(self.network.lss.WAITING_STATE)
                raise e
        else:
            with pytest.raises(canopen.lss.LssError) as e_info:
                self.network.lss.configure_bit_timing(speed_grade)
            assert str(e_info.value) == 'LSS Error: 1'

    def test_inquire_lss_address(self):
        lss_configuration_state(self.network)

        assert boot_vendor_id == self.network.lss.inquire_lss_address(canopen.lss.CS_INQUIRE_VENDOR_ID)
        assert 0 != self.network.lss.inquire_lss_address(canopen.lss.CS_INQUIRE_PRODUCT_CODE)
        assert self.network.lss.inquire_lss_address(canopen.lss.CS_INQUIRE_REVISION_NUMBER) is not None
        assert self.network.lss.inquire_lss_address(canopen.lss.CS_INQUIRE_SERIAL_NUMBER) is not None

        lss_waiting_state(self.network)

    def test_set_node_id(self):
        lss_configuration_state(self.network)

        for node_id in (1, 15, 127, 255):
            self.network.lss.configure_node_id(node_id)
            assert node_id == self.network.lss.inquire_node_id()

        lss_waiting_state(self.network)

    def test_set_node_id_reset_comm(self):
        lss_configuration_state(self.network)

        node_id = 15
        self.network.lss.configure_node_id(node_id)
        assert node_id == self.network.lss.inquire_node_id()
        self.network.lss.store_configuration()
        lss_waiting_state(self.network)

        node = canopen.RemoteNode(node_id, 'Bootloader.eds')
        node.associate_network(self.network)
        node.nmt.state = 'RESET COMMUNICATION'

        time.sleep(0.1)

        lss_configuration_state(self.network)
        id = self.network.lss.inquire_node_id()
        lss_waiting_state(self.network)
        assert id == node_id

    @pytest.mark.parametrize('node_id', [
        97,
        1,
        #5,
        #10,
        #18,
        #36,
    ])
    def test_change_lss_config_after_initial_set(self, node_id):
        lss_configuration_state(self.network)

        try:
            self.network.lss.configure_node_id(node_id)
            self.network.lss.store_configuration()

            node = canopen.RemoteNode(node_id, 'Bootloader.eds')
            node.associate_network(self.network)

        finally:
            lss_waiting_state(self.network)
