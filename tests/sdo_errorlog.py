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
        l = self.node.sdo[0x1003][0].raw
        assert l is not None

    def test_reset_error_log(self):
        self.node.sdo[0x1003][0].raw = 0

    def test_incorrect_reset_error_log(self):
        with pytest.raises(canopen.sdo.exceptions.SdoAbortedError) as e_info:
            self.node.sdo[0x1003][0].raw = 1
        assert str(e_info.value) == 'Code 0x06010000, Unsupported access to an object'

    def test_try_read_missing_error_log_entries(self):
        for i in range(1, 256):
            with pytest.raises(canopen.sdo.exceptions.SdoAbortedError) as e_info:
                len(self.node.sdo[0x1003][i].raw)
            assert str(e_info.value) == 'Code 0x08000023'


