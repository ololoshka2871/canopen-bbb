# -*- coding: utf-8 -*-

from common import *
from ODEntry import *
import canopen


def pytest_generate_tests(metafunc):
    node = canopen.RemoteNode(1, 'SCTB_CANopenPressureSensor0xC001.eds')
    entries = []
    for od_addr in node.sdo.keys():
        entries.extend(ODEntry.createEntries(node.sdo, od_addr))
    metafunc.parametrize('odEntry', entries)


class TestSDOReadAll(object):
    @classmethod
    def setup_class(cls):
        cls.testspeed = 125000

        if cls.testspeed != default_bitrate:
            set_interface_bitrate(default_bitrate)
            cls.network = create_network()
            cls.node_id = 16
            reset_network(cls.network)

            # lss prepare node
            lss_waiting_state(cls.network)
            lss_configure_node(cls.network, cls.node_id, cls.testspeed)
            cls.node = canopen.RemoteNode(cls.node_id, 'SCTB_CANopenPressureSensor0xC001.eds')
            cls.node.associate_network(cls.network)
            cls.node.nmt.state = 'RESET COMMUNICATION'
            cls.node.remove_network()
            cls.network.disconnect()

            set_interface_bitrate(cls.testspeed)

            cls.network = create_network()
            cls.node.associate_network(cls.network)
            time.sleep(0.5)
        else:
            cls.network = create_network()
            cls.node_id = 16
            reset_network(cls.network)

            # lss prepare node
            lss_configure_node(cls.network, cls.node_id, cls.testspeed)
            time.sleep(0.5)
            cls.node = canopen.RemoteNode(cls.node_id, 'SCTB_CANopenPressureSensor0xC001.eds')
            cls.node.associate_network(cls.network)
            cls.node.nmt.state = 'RESET COMMUNICATION'
            cls.node.nmt.wait_for_bootup(1)

    @classmethod
    def teardown_class(cls):
        if cls.testspeed != default_bitrate:
            cls.node.nmt.state = 'PRE-OPERATIONAL'
            lss_configure_node(cls.network, cls.node_id, default_bitrate)
            cls.node.nmt.state = 'RESET COMMUNICATION'
            cls.node.remove_network()
            cls.network.disconnect()

            set_interface_bitrate(default_bitrate)

    def test_read_SDO_entries(self, odEntry):
        entry = ODEntry.parce(odEntry)
        if isinstance(self.node.sdo[entry.index], canopen.sdo.base.Array) or \
                isinstance(self.node.sdo[entry.index], canopen.sdo.base.Record):
            if entry.subindex is None:
                return

            try:
                print('trying to read {}sub{}'.format(hex(entry.index), entry.subindex))
                v = entry.getvalue(self.node.sdo)
            except canopen.sdo.exceptions.SdoAbortedError as f:
                if entry.index == 0x1003 and entry.subindex > 0 and f.code == 0x08000023:
                    return  # лог ошибок может быть пуст

                if (entry.index in (6144, 6145, 6146, 6147, 6148)) \
                        and entry.subindex == 4 and f.code == 0x06090011:
                    return  # это так и должно быть, этого сабиндекса нет

                if entry.index == 0x1029 and entry.subindex == 3 and f.code == 0x06090011:
                    return  # это так и должно быть, этого сабиндекса нет

                elif f.code != 0x06010001:
                    raise f
        else:
            try:
                v = entry.getvalue(self.node.sdo)
            except canopen.sdo.exceptions.SdoAbortedError as f:
                if f.code != 0x06010001:
                    raise f
