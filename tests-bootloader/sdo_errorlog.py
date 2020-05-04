# -*- coding: utf-8 -*-

from common import *
import can
import pytest


class TestSDOErrorLogRelated(object):
    @classmethod
    def setup_class(cls):
        test_speed = default_bitrate
        cls.node_id = 16
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
        cls.node.nmt.wait_for_bootup()

    @classmethod
    def teardown_class(cls):
        # lss prepare node
        reset_network(cls.network)
        cls.network.disconnect()
        set_interface_bitrate(default_bitrate)

    # Проверка чтения поличества ошибок (может быть любое число 0-255)
    def test_read_error_log_depth(self):
        assert 255 >= self.node.sdo[0x1003][0].raw >= 0

    # Проверка сброса лога
    def test_reset_error_log(self):
        self.node.sdo[0x1003][0].raw = 0
        assert 0 == self.node.sdo[0x1003][0].raw

    # Проверка того, что запись отличного от 0 значения в 0x1003sub0 вызывает ошибку
    def test_incorrect_reset_error_log(self):
        with pytest.raises(canopen.sdo.exceptions.SdoAbortedError) as e_info:
            self.node.sdo[0x1003][0].raw = 1
        assert str(e_info.value) == 'Code 0x06010000, Unsupported access to an object'

    # Сброс лога, затем попытка прочитать верхушку, должна вернуться ошибка
    def test_try_read_empty_error_log_entry(self):
        self.node.sdo[0x1003][0].raw = 0
        with pytest.raises(canopen.sdo.exceptions.SdoAbortedError) as e_info:
            self.node.sdo[0x1003][1].raw is not None
        assert str(e_info.value) == 'Code 0x08000023, Object dictionary dynamic generation fails or no object ' \
                                    'dictionary is present'

    # Попытка чтения других записей лога - должна возвращать ошибку, так как их не существует
    def test_try_read_missing_error_log_entries(self):
        for i in range(2, 256):
            try:
                self.node.sdo[0x1003][i].raw is not None
            except canopen.sdo.exceptions.SdoAbortedError as e_info:
                assert str(e_info) == 'Code 0x06090011, Subindex does not exist'

    # Установка специального значения в лог ошибок - чисто ради теста.
    def test_read_error_value(self):
        try:
            self.node.sdo[0x1003][0].raw = 254
            assert self.node.sdo[0x1003][1].raw == 0xff1300fe  # TEST_ERROR_VALUE
        except canopen.sdo.exceptions.SdoAbortedError as e_info:
            assert str(e_info) == 'Code 0x06010000, Unsupported access to an object'
