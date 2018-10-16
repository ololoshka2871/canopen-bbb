import canopen
from common import *
import can
import pytest
import struct

# Установлено, что на скорости 10000 буфер передатчика не более 182 байт


def align(v, alignnment):
    if v & (alignnment - 1) == 0:
        return v
    return (v & ~(alignnment - 1)) + alignnment


def l2b(l):
    return b''.join(map(lambda v: v.to_bytes(4, 'little'), l))


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class TestSDO(object):
    @classmethod
    def setup_class(cls):
        cls.network = create_network()
        cls.node_id = 16

        # lss prepare node
        lss_waiting_state(cls.network)
        set_node_id(cls.network, cls.node_id)
        cls.node = canopen.RemoteNode(cls.node_id, 'Bootloader.eds')
        cls.node.associate_network(cls.network)
        cls.firmware = open('app.bin', 'rb').read()

    def _test_sdo1003(self):
        for k in self.node.sdo[0x1003].keys():
            print(self.node.sdo[0x1003][k].raw)

    def _test_sdo1029(self):
        for k in self.node.sdo[0x1029].keys():
            print(self.node.sdo[0x1029][k].raw)

    def _test_sdo1f56sub1(self):
        print(self.node.sdo[0x1f56][1].raw)

    def _test_write_sdo1029sub1(self):
        for i in (1, 2, 3, 4):
            self.node.sdo[0x1029][1].raw = i
            assert self.node.sdo[0x1029][1].raw == i

    def test_STATUS(self):
        assert self.node.sdo[0x2100].raw.decode("utf-8").rstrip('\0') in ('READY', 'NO APP', 'APP ERR')

    @pytest.mark.xfail(raises=can.CanError)
    def _test_incorrect_write_sdo1f50sub1(self):
        data = bytearray([x & 0xff for x in range(183)])
        with self.node.sdo[0x1f50][1].open('wb', size=len(data), block_transfer=True) as f:
            f.write(data)

    def _test_write128_sdo1f50sub1(self):
        data = bytearray([x & 0xff for x in range(182)])
        with self.node.sdo[0x1f50][1].open('wb', size=len(data), block_transfer=True) as f:
            f.write(data)

    def _test_write4096_sdo1f50sub1(self):
        data = self.firmware
        with self.node.sdo[0x1f50][1].open('wb', size=len(data), block_transfer=False) as f:
            f.write(data)

    def _test_app_crc_check(self):
        crc = struct.unpack('<I', self.firmware[6*4:7*4])[0]
        r_crc = self.node.sdo[0x1f56][1].raw
        assert crc == r_crc

    @pytest.mark.xfail(raises=canopen.sdo.exceptions.SdoAbortedError)
    def _test_sdo1f50sub1(self):
        len(self.node.sdo[0x1f50][1].raw)
