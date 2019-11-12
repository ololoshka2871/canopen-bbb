# -*- coding: utf-8 -*-

from common import *
from ODEntry import *
import canopen
import pytest


class TestSDO(object):
    @classmethod
    def setup_class(cls):
        set_interface_bitrate(10000)
        cls.network = create_network()
        cls.node_id = 19
        reset_network(cls.network)

        # lss prepare node
        lss_waiting_state(cls.network)
        lss_configure_node(cls.network, cls.node_id, 125000)
        cls.node = canopen.RemoteNode(cls.node_id, 'SCTB_CANopenPressureSensor0xC001.eds')
        cls.node.associate_network(cls.network)
        cls.node.nmt.state = 'RESET COMMUNICATION'
        cls.node.remove_network()
        cls.network.disconnect()

        set_interface_bitrate(125000)
        cls.network = create_network()
        cls.node.associate_network(cls.network)
        cls.node.nmt.state = 'OPERATIONAL'

    @classmethod
    def teardown_class(cls):
        cls.node.nmt.state = 'PRE-OPERATIONAL'
        lss_configure_node(cls.network, cls.node_id, 10000)
        cls.node.nmt.state = 'RESET COMMUNICATION'
        cls.node.remove_network()
        cls.network.disconnect()

        set_interface_bitrate(10000)

    @pytest.mark.parametrize("ro_entry",
                             ['1000',
                              '1001',
                              '1018sub0',
                              '1018sub1',
                              '1018sub2',
                              '1018sub3',
                              '1018sub4'])
    def test_ro_entries(self, ro_entry):
        entry = ODEntry.parce(ro_entry)
        assert entry.getvalue(self.node.sdo) is not None
