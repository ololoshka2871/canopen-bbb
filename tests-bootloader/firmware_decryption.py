# -*- coding: utf-8 -*-

from common import *
import can
import pytest
import struct
import time
from Crypto.Cipher import AES
from Crypto.Hash import SHA224


class TestFirmwareDecryption(object):
    @staticmethod
    def getkey(header):
        h = SHA224.new()
        h.update(header)
        digestsha224 = h.digest()
        key = [None] * 16
        for i in range(14):
            key[i] = digestsha224[i * 2]

        key[14] = digestsha224[len(digestsha224) - 3]
        key[15] = digestsha224[len(digestsha224) - 1]
        return ''.join(key)

    @classmethod
    def setup_class(cls):
        with open('app.deploy', 'rb') as f:
            cls.e_firmware = f.read()

        with open('app.bin', 'rb') as f:
            cls.firmware = f.read()

        if len(cls.e_firmware) > len(cls.firmware):
            cls.firmware += '\x00' * (len(cls.e_firmware) - len(cls.firmware))

    def test_firmware_equal(self):
        header1 = self.e_firmware[:headed_size]
        header2 = self.firmware[:headed_size]

        assert header1 == header2

    def test_decryption(self):
        key = TestFirmwareDecryption.getkey(self.e_firmware[0:9*4])
        iv = self.e_firmware[4:16 + 4]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        raw = self.e_firmware[:headed_size] + cipher.decrypt(self.e_firmware[headed_size:])

        assert raw == self.firmware
