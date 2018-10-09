import canopen
from common import *


class TestSDO(object):
    @classmethod
    def setup_class(cls):
        cls.network = create_network()
        cls.node_id = 16

        # lss prepare node
        set_bootloader_node_id(cls.network, cls.node_id)
        cls.node = canopen.RemoteNode(cls.node_id, 'Bootloader.eds')
        cls.node.associate_network(cls.network)

    def test_sdo1003(self):
        for k in self.node.sdo[0x1003].keys():
            print(self.node.sdo[0x1003][k].raw)

    def test_sdo1029(self):
        for k in self.node.sdo[0x1029].keys():
            print(self.node.sdo[0x1029][k].raw)

    def test_sdo1f50sub1(self):
        pass


