# -*- coding: utf-8 -*-

from common import *
import can
from canopen.nmt import NmtError
import pytest
import struct
import time
from Crypto.Hash import SHA224

# Установлено, что на собаке скорости 10000 буфер передатчика собаки не более 182 байт


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
        key = [None] * 16
        for i in range(14):
            key[i] = digestsha224[i * 2]

        key[14] = digestsha224[len(digestsha224) - 3]
        key[15] = digestsha224[len(digestsha224) - 1]
        return ''.join(key)

    @classmethod
    def setup_class(cls):
        try:
            with open('app.bin', 'rb') as f:
                cls.raw_firmware = f.read()
        except:
            cls.raw_firmware = None

        try:
            with open('app.deploy', 'rb') as f:
                cls.encrypted_firmware = f.read()
        except:
            cls.encrypted_firmware = None

        test_speed = 125000
        cls.node_id = 16

        set_interface_bitrate(default_bitrate)
        cls.network = create_network()
        reset_network(cls.network)

        # lss prepare node
        lss_waiting_state(cls.network)
        lss_configure_bit_timing(cls.network, test_speed)
        lss_set_node_id(cls.network, cls.node_id)
        cls.network.nmt.state = 'RESET COMMUNICATION'

        cls.network.disconnect()
        set_interface_bitrate(test_speed)
        cls.network = create_network()

        cls.node = canopen.RemoteNode(cls.node_id, 'Bootloader.eds')
        cls.node.associate_network(cls.network)
        try:
            cls.node.nmt.wait_for_bootup(0.5)
        except NmtError:
            pass

    @classmethod
    def teardown_class(cls):
        # lss prepare node
        reset_network(cls.network)
        cls.network.disconnect()
        set_interface_bitrate(default_bitrate)

    # Попытка чтения текущегго приложения должна завершиться ошибкой - доступ - только запись
    def test_read_firmware(self):
        with pytest.raises(canopen.sdo.exceptions.SdoAbortedError) as e_info:
            len(self.node.sdo[0x1f50][1].raw)

        assert str(e_info.value) == 'Code 0x06010001, Attempt to read a write only object'

    @pytest.mark.parametrize('method,result', [
        (0, True),
        (1, True),
        (2, False),
        (-1, False)
    ])
    def test_select_encryption_method(self, method, result):
        if result:
            self.node.sdo[0x1f55][1].raw = method
            assert self.node.sdo[0x1f55][1].raw == method
        else:
            with pytest.raises(Exception) as e_info:
                self.node.sdo[0x1f55][1].raw = method
            if method < 0:
                assert str(e_info.value) == 'Value does not fit in specified type'
            else:
                assert str(e_info.value) == 'Code 0x06090031, Value of parameter written too high'

    # Записываем в область приложения нули блочным способом или нет, если ошибка
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

    # проверяем что в области проверки статуса приложения 0x1f56sub1 0 - invalid application
    def test_invalid_app_crc(self):
        assert self.node.sdo[0x1f56][1].raw == 0

    # Пытаемся запустить неверное приложение, в логе ошибок должен появится код APPLICATION_INCORRECT_OR_NOT_EXISTS
    def test_try_start_invalid_app(self):
        self.node.sdo[0x1F51][1].raw = 1
        error = Error_CODE(self.node.sdo[0x1003][1].raw)
        assert error.code == Error_CODES.APPLICATION_INCORRECT_OR_NOT_EXISTS

    # Сброс лога ошибок
    def test_reset_errors(self):
        self.node.sdo[0x1003][0].raw = 0
        assert self.node.sdo[0x1003][0].raw == 0
        with pytest.raises(canopen.sdo.exceptions.SdoAbortedError) as e_info:
            self.node.sdo[0x1003][1].raw is not None
        assert str(e_info.value) == 'Code 0x08000023, Object dictionary dynamic generation fails or no object ' \
                                    'dictionary is present'

    # Записываем корректный образ приложения
    def common_write_correct_app(self, fm, method):
        if not fm:
            return

        self.node.sdo[0x1f55][1].raw = method

        with self.node.sdo[0x1f50][1].open('wb', size=len(fm), block_transfer=False) as f:
            f.write(fm)
        if Error_CODE(self.node.sdo[0x1003][1].raw).code != Error_CODES.APPLICATION_READY_TO_START:
            raise RuntimeError('Write failed')

    def test_write_correct_raw_app(self):
        self.common_write_correct_app(self.raw_firmware, 0)

    def test_write_correct_encrypted_app(self):
        self.common_write_correct_app(self.encrypted_firmware, 1)

    def get_crc(self):
        fm = self.raw_firmware if self.raw_firmware else self.encrypted_firmware
        return struct.unpack('<I', fm[6 * 4:7 * 4])[0]

    # Сравниваем указанный в образе CRC32 образа приложения с тем, что вернет нам бутлоадер насчитавций фактическое
    # значение
    def test_correct_app_crc(self):
        r_crc = self.node.sdo[0x1f56][1].raw
        assert self.get_crc() == r_crc

    def test_write_incorrect_method(self):
        if self.raw_firmware and self.encrypted_firmware:
            with pytest.raises(RuntimeError) as e_info:
                self.common_write_correct_app(self.encrypted_firmware, 0)
            assert str(e_info.value) == 'Write failed'
