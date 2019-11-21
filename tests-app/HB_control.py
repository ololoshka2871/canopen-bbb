from common import *
import pytest
import time


class TestHBControl(object):
    @classmethod
    def setup_class(cls):
        cls.network = create_network()
        cls.node_id = 16
        reset_network(cls.network)

        # lss prepare node
        lss_set_node_id(cls.network, cls.node_id)
        cls.node = canopen.RemoteNode(cls.node_id, 'SCTB_CANopenPressureSensor0xC001.eds')
        cls.node.associate_network(cls.network)

    @classmethod
    def teardown_class(cls):
        cls.node.remove_network()
        cls.network.disconnect()

    @pytest.mark.parametrize('timeout', [1000, 500, 250, 125, 50, 10, 7, 3, 0, 1500])
    def test_HB_timeout(self, timeout):
        if timeout < 10 and timeout != 0:
            with pytest.raises(canopen.sdo.exceptions.SdoAbortedError) as excinfo:
                self.node.sdo[0x1017].raw = timeout
            assert excinfo.value.code == 0x06090032  # value too low
            return
        else:
            self.node.sdo[0x1017].raw = timeout
        if timeout > 0:
            self.node.nmt.wait_for_heartbeat()
            self.node.nmt.wait_for_heartbeat(timeout * 0.001 + 0.001)
        else:
            with pytest.raises(canopen.nmt.NmtError) as excinfo:
                self.node.nmt.wait_for_heartbeat(1)
        time.sleep(0.1)
