# -*- coding: utf-8 -*-

from common import *
import canopen
import time
import struct


class TestSettingsBlob(object):
    @classmethod
    def setup_class(cls):
        cls.network = create_network()
        cls.node_id = 42
        reset_network(cls.network)
        time.sleep(0.5)

        # lss prepare node
        lss_waiting_state(cls.network)
        cls.node = canopen.RemoteNode(cls.node_id, 'Bootloader.eds')
        cls.node.associate_network(cls.network)
        lss_set_node_id(cls.network, cls.node_id)
        cls.node.nmt.wait_for_bootup(1)
        time.sleep(1)

    @classmethod
    def teardown_class(cls):
        cls.node.remove_network()
        cls.network.disconnect()

    def testReadSettingsBlob(self):
        data = self.node.sdo[0x1f5A][1].raw
        assert len(data) > 3 * 4

    def testwriteFakeSettings_verify(self):
        fake_settings = struct.pack('<IIIIIIIIII',
                                    1, 2, 10 * 4,
                                    1, 2, 3, 4, 5, 6, 7)
        self.node.sdo[0x1f5A][1].raw = fake_settings

        assert (self.node.sdo[0x1f5A][1].raw == fake_settings)
