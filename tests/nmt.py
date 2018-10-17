
from common import *
import time


class TestNMT(object):
    @classmethod
    def setup_class(cls):
        cls.network = create_network()
        cls.node_id = 42

        # lss prepare node
        lss_waiting_state(cls.network)
        lss_set_node_id(cls.network, cls.node_id)
        cls.node = canopen.RemoteNode(cls.node_id, 'Bootloader.eds')
        cls.node.associate_network(cls.network)

    def _reset_delay(self):
        time.sleep(0.01)

    def test_reset_com(self):
        self.network.nmt.state = 'RESET COMMUNICATION'
        self.node.nmt.wait_for_bootup(1)

    def test_reset(self):
        self.network.nmt.state = 'RESET'
        self._reset_delay()
        lss_set_node_id(self.network, self.node_id)
        self.node.nmt.wait_for_bootup(1)

    def test_node_reset_com(self):
        self.node.nmt.state = 'RESET COMMUNICATION'
        self.node.nmt.wait_for_bootup(1)

    def test_node_reset(self):
        self.node.nmt.state = 'RESET'
        self._reset_delay()
        lss_set_node_id(self.network, self.node_id)
        self.node.nmt.wait_for_bootup(1)
