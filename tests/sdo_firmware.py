from common import *
import can
import pytest
import struct
import time

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


class TestSDOFirmwareRelated(object):
    @classmethod
    def setup_class(cls):
        cls.network = create_network()
        cls.node_id = 16

        # lss prepare node
        lss_waiting_state(cls.network)
        lss_set_node_id(cls.network, cls.node_id)
        cls.node = canopen.RemoteNode(cls.node_id, 'Bootloader.eds')
        cls.node.associate_network(cls.network)
        cls.firmware = open('app.bin', 'rb').read()

    def test_STATUS(self):
        assert self.node.sdo[0x1F57][1].raw in (FlashStatus.OK,
                                                FlashStatus.READY_TO_START,
                                                FlashStatus.INVALID_PROGRAM)

    def test_read_firmware(self):
        with pytest.raises(canopen.sdo.exceptions.SdoAbortedError) as e_info:
            len(self.node.sdo[0x1f50][1].raw)

        assert str(e_info.value) == 'Code 0x06010001, Attempt to read a write only object'

    def test_restore_after_invalid_write(self):
        data = bytearray([x & 0xff for x in range(183)])
        try:
            with self.node.sdo[0x1f50][1].open('wb', size=len(data), block_transfer=True) as f:
                f.write(data)
        except can.CanError:
            f.close()
            time.sleep(1.5)
            with self.node.sdo[0x1f50][1].open('wb', size=len(data), block_transfer=False) as f:
                f.write(data)

    def test_invalid_app_crc(self):
        assert self.node.sdo[0x1f56][1].raw == 0

    def test_try_start_invalid_app(self):
        self.node.sdo[0x1F51][1].raw = 1
        assert self.node.sdo[0x1F57][1].raw == FlashStatus.INVALID_PROGRAM

    def test_write_correct_app(self):
        data = self.firmware
        with self.node.sdo[0x1f50][1].open('wb', size=len(data), block_transfer=False) as f:
            f.write(data)
        assert self.node.sdo[0x1F57][1].raw == FlashStatus.OK

    def test_correct_app_crc(self):
        crc = struct.unpack('<I', self.firmware[6*4:7*4])[0]
        r_crc = self.node.sdo[0x1f56][1].raw
        assert crc == r_crc

    def test_start_correct_app(self):
        bootloader_start_app(self.node)
        with pytest.raises(canopen.sdo.exceptions.SdoCommunicationError) as e_info:
            status = self.node.sdo[0x1F57][1].raw

        assert str(e_info.value) == 'No SDO response received'
