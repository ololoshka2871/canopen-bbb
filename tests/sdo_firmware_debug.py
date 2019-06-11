# -*- coding: utf-8 -*-

from common import *
import can
import pytest
import struct
import time
from Crypto.Cipher import AES
from Crypto.Hash import SHA224
import hexdump

# Установлено, что на скорости 10000 буфер передатчика собаки не более 182 байт


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


class TestSDOFirmwareRelated(object):
    @staticmethod
    def getkey(header):
        h = SHA224.new()
        h.update(header)
        digestsha224 = h.digest()
        print("header=")
        hexdump.hexdump(header)
        print("sha224=")
        hexdump.hexdump(digestsha224)
        key = [None] * 16
        for i in range(14):
            key[i] = digestsha224[i * 2]

        key[14] = digestsha224[len(digestsha224) - 3]
        key[15] = digestsha224[len(digestsha224) - 1]
        return ''.join(key)

    @classmethod
    def setup_class(cls):
        with open('app.bin', 'rb') as f:
            cls.firmware = f.read()

        key = TestSDOFirmwareRelated.getkey(cls.firmware[0:9*4])

        cls.e_firmware = cls.firmware[:]

        cripted_part_len = len(cls.e_firmware[9 * 4:])
        if cripted_part_len % AES.block_size != 0:
            to_add = AES.block_size - cripted_part_len % AES.block_size
            cls.e_firmware += b'\x00' * to_add

        iv = cls.firmware[4:16 + 4]
        print("iv=")
        hexdump.hexdump(iv)
        print("key=")
        hexdump.hexdump(key)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        cls.e_firmware = cls.e_firmware[0:9*4] + cipher.encrypt(cls.e_firmware[9 * 4:])

        test_speed = 10000
        cls.node_id = 18
        cls.network = create_network()
        reset_network(cls.network)

        # lss prepare node
        lss_waiting_state(cls.network)
        lss_configure_bit_timing(cls.network, test_speed)
        lss_set_node_id(cls.network, cls.node_id)

        cls.node = canopen.RemoteNode(cls.node_id, 'Bootloader.eds')
        cls.node.associate_network(cls.network)

    @classmethod
    def teardown_class(cls):
        # lss prepare node
        reset_network(cls.network)
        cls.network.disconnect()
        set_interface_bitrate(10000)

    def test_write_correct_app(self):
        data = self.e_firmware
        hexdump.hexdump(data[:128])
        with self.node.sdo[0x1f50][1].open('wb', size=len(data), block_transfer=False) as f:
            f.write(data)
        assert Error_CODE(self.node.sdo[0x1003][1].raw).code == Error_CODES.APPLICATION_READY_TO_START

