
import pytest
import time
import canopen
from common import *

@pytest.fixture
def network():
    return create_network()


def set_bootloader_node_id(network, node_id):
    bootloader_lss_configuration_state(network)
    network.lss.configure_node_id(node_id)
    network.lss.store_configuration()
    lss_waiting_state(network)


class TestNMT(object):
    @classmethod
    def setup_class(cls):
        cls.network = create_network()
        cls.node_id = 42

        # lss prepare node
        set_bootloader_node_id(cls.network, cls.node_id)
        cls.node = canopen.RemoteNode(cls.node_id, 'Bootloader.eds')
        cls.node.associate_network(cls.network)

    def test_reset_com(self):
        self.network.nmt.state = 'RESET COMMUNICATION'
        self.node.nmt.wait_for_bootup(1)

    def test_reset(self):
        self.network.nmt.state = 'RESET'
        set_bootloader_node_id(self.network, self.node_id)
        self.node.nmt.wait_for_bootup(1)

    def test_node_reset_com(self):
        self.node.nmt.state = 'RESET COMMUNICATION'
        self.node.nmt.wait_for_bootup(1)

    def test_node_reset(self):
        self.node.nmt.state = 'RESET'
        set_bootloader_node_id(self.network, self.node_id)
        self.node.nmt.wait_for_bootup(1)
