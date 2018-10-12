import canopen
from common import *
import can
import pytest
import random
import zlib

# Установлено, что на скорости 10000 буфер передатчика не более 182 байт

def align(v, alignnment):
    if v & (alignnment - 1) == 0:
        return v
    return (v & (alignnment - 1)) + alignnment


def l2b(l):
    return b''.join(map(lambda v: v.to_bytes(4, 'little'), l))


class correctProgrammHeader:
    def __init__(self):
        self.app_base = 0x8004800
        self.PAGE_SIZE = 2048

        self.magic = 0x41707000
        self.vendor_id = 0x004f038C
        self.product_id = 0x0000CD01
        self.version = 1

    def serialise(self):
        image = [int(x) for x in range(int(2 * self.PAGE_SIZE / 4))]

        _test_start = 9 * 4

        image[0] = self.magic
        image[1] = self.app_base + align(9 * 4, 16)  # start
        image[2] = image[1] + align(random.randint(256, self.PAGE_SIZE - 256), 4)  # end
        image[3] = self.vendor_id
        image[4] = self.product_id
        image[5] = self.version
        image[6] = zlib.crc32(l2b(image[(image[1] - self.app_base):(image[2] - self.app_base)]))
        image[7] = self.app_base + self.PAGE_SIZE
        image[8] = image[2] - 128

        return l2b(image)


class TestSDO(object):
    @classmethod
    def setup_class(cls):
        cls.network = create_network()
        cls.node_id = 16

        # lss prepare node
        set_bootloader_node_id(cls.network, cls.node_id)
        cls.node = canopen.RemoteNode(cls.node_id, 'Bootloader.eds')
        cls.node.associate_network(cls.network)

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

    @pytest.mark.xfail(raises=can.CanError)
    def test_incorrect_write_sdo1f50sub1(self):
        data = bytearray([x & 0xff for x in range(183)])
        with self.node.sdo[0x1f50][1].open('wb', size=len(data), block_transfer=True) as f:
            f.write(data)

    def test_write128_sdo1f50sub1(self):
        data = bytearray([x & 0xff for x in range(182)])
        with self.node.sdo[0x1f50][1].open('wb', size=len(data), block_transfer=True) as f:
            f.write(data)

    def test_write4096_sdo1f50sub1(self):
        data = correctProgrammHeader().serialise()
        with self.node.sdo[0x1f50][1].open('wb', size=len(data), block_transfer=False) as f:
            f.write(data)

    def _test_sdo1f50sub1(self):
        print('\nObject size: {}'.format(len(self.node.sdo[0x1f50][1].raw)))
