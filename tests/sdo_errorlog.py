from common import *
import can
import pytest


class TestSDOErrorLogRelated(object):
    @classmethod
    def setup_class(cls):
        test_speed = 10000
        cls.node_id = 16
        cls.network = create_network()
        reset_network(cls.network)

        # lss prepare node
        lss_waiting_state(cls.network)
        lss_configure_bit_timing(cls.network, test_speed)
        lss_set_node_id(cls.network, cls.node_id)
        cls.network.nmt.state = 'RESET COMMUNICATION'

        cls.network.disconnect()
        set_interface_bitrate(test_speed)
        cls.network = create_network()

        cls.node = canopen.RemoteNode(cls.node_id, 'Bootloader.eds')
        cls.node.associate_network(cls.network)

    @classmethod
    def teardown_class(cls):
        # lss prepare node
        reset_network(cls.network)
        cls.network.disconnect()
        set_interface_bitrate(10000)

    def test_read_error_log_depth(self):
        len = self.node.sdo[0x1f50][0]
        assert len is not None
