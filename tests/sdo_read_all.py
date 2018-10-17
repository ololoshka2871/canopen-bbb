from common import *
import canopen


class ODEntry:
    def __init__(self, index, subindex=None):
        self.index = index
        self.subindex = subindex

    @staticmethod
    def createEntries(sdo, od_entrie):
        if isinstance(sdo[od_entrie], canopen.sdo.base.Record):
            return [str(ODEntry(od_entrie, sub)) for sub in sdo[od_entrie].keys()]
        else:
            return [str(ODEntry(od_entrie))]

    def __str__(self):
        return '{:X}sub{:X}'.format(self.index, self.subindex) if self.subindex is not None \
            else '{:X}'.format(self.index)

    @staticmethod
    def parce(s):
        v = s.split('sub')
        return ODEntry(int(v[0], 16), int(v[1], 16) if len(v) == 2 else None)

    def getvalue(self, sdo):
        if self.subindex is None:
            return sdo[self.index].raw
        else:
            return sdo[self.index][self.subindex].raw


def pytest_generate_tests(metafunc):
    node = canopen.RemoteNode(1, 'Bootloader.eds')
    entries = []
    for od_addr in node.sdo.keys():
        entries.extend(ODEntry.createEntries(node.sdo, od_addr))
    metafunc.parametrize('odEntry', entries)


class TestSDOReadAll(object):
    @classmethod
    def setup_class(cls):
        cls.network = create_network()
        cls.node_id = 16

        # lss prepare node
        lss_waiting_state(cls.network)
        lss_set_node_id(cls.network, cls.node_id)
        cls.node = canopen.RemoteNode(cls.node_id, 'Bootloader.eds')
        cls.node.associate_network(cls.network)

    def test_read_SDO_entries(self, odEntry):
        entry = ODEntry.parce(odEntry)
        if isinstance(self.node.sdo[entry.index], canopen.sdo.base.Array):
            for subindex in self.node.sdo[entry.index].keys():
                try:
                    v = self.node.sdo[entry.index][subindex].raw
                except canopen.sdo.exceptions.SdoAbortedError as f:
                    if f.code != 0x06010001:
                        raise f
        else:
            try:
                v = entry.getvalue(self.node.sdo)
            except canopen.sdo.exceptions.SdoAbortedError as f:
                if f.code != 0x06010001:
                    raise f
