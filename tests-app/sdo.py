# -*- coding: utf-8 -*-

from common import *
from ODEntry import *
import datetime
import canopen
import pytest
import random
import string
import math
import time


def random_float():
    return float(random.uniform(-10, 10))


def is_floats_equal(f1, f2, max_diff=1e-6):
    return math.fabs(f1 - f2) < max_diff


def current_year():
    return datetime.datetime.now().year


class TestSDO(object):
    @classmethod
    def setup_class(cls):
        cls.network = create_network()
        cls.node_id = 42
        cls.correct_password = b'_PASSWORD_'
        reset_network(cls.network)
        time.sleep(0.5)

        # lss prepare node
        lss_waiting_state(cls.network)
        cls.node = canopen.RemoteNode(cls.node_id, 'SCTB_CANopenPressureSensor0xC001.eds')
        cls.node.associate_network(cls.network)
        lss_set_node_id(cls.network, cls.node_id)
        cls.node.nmt.wait_for_bootup(1)
        time.sleep(1)

    @classmethod
    def teardown_class(cls):
        cls.node.remove_network()
        cls.network.disconnect()

    @pytest.mark.parametrize("ro_entry",
                             ['1000',
                              '1001',
                              '1018sub1',
                              '1018sub2',
                              '1018sub3',
                              '1018sub4',
                              '1008',
                              '1009',
                              '100a',
                              '1022',
                              '2100',
                              '2360',
                              '2500sub1',
                              '2500sub2',
                              '2500sub3',
                              '2501sub1',
                              '2501sub2',
                              '2501sub3',
                              '2510sub1',
                              '2510sub2',
                              '2510sub3',
                              '2510sub4',
                              '2510sub5',
                              '25FFsub1',
                              '25FFsub2',
                              '25FFsub3',
                              '25FFsub4',
                              '25FFsub5',
                              '25FFsub6',
                              '25FFsub7',
                              '25FFsub8',
                              '6001sub1'])
    def test_ro_entries(self, ro_entry):
        """
        Все по честному, либа действительно пытается записать в эти индексы,
        и должна получить верный код ошибки
        """
        entry = ODEntry.parce(ro_entry)
        v = entry.getvalue(self.node.sdo)
        assert v is not None

        with pytest.raises(canopen.sdo.exceptions.SdoAbortedError) as excinfo:
            entry.setvalue(self.node.sdo, v)

        assert excinfo.value.code == 0x06010002  # readonly

    def _test_defaults_common(self):
        test_items = (
            ('1000', 0x301BB),

            # resetable values
            ('1005', 0x80),
            ('1006', 0),
            ('1007', 0),
            ('1014', self.node_id + 0x80),
            ('1015', 100),
            ('1017', 1000),
            ('1029sub1', 1),
            ('1029sub2', 1),
            ('1029sub4', 0),
            ('1029sub5', 0),
            ('1029sub6', 0),
            ('1200sub1', self.node_id + 0x600),
            ('1200sub2', self.node_id + 0x580),

            # TPDO 1
            ('1800sub1', 0x180 + self.node_id),
            ('1800sub2', 0xFE),
            ('1800sub3', 2000),
            ('1800sub5', 1000),
            ('1800sub6', 0),
            ('1a00sub0', 1),
            ('1a00sub1', 0x61000120),

            # TPDO 2
            ('1801sub1', 0x280 + self.node_id),
            ('1801sub2', 0xFE),
            ('1801sub3', 2000),
            ('1801sub5', 1000),
            ('1801sub6', 0),
            ('1a01sub0', 1),
            ('1a01sub1', 0x61010120),

            # TPDO 3
            ('1802sub1', (0x380 + self.node_id) | (1 << 31)),
            ('1802sub2', 0xFE),
            ('1802sub3', 0),
            ('1802sub5', 0),
            ('1802sub6', 0),
            ('1a02sub0', 0),
            ('1a02sub1', 0),
            ('1a02sub2', 0),
            ('1a02sub3', 0),
            ('1a02sub4', 0),
            ('1a02sub5', 0),
            ('1a02sub6', 0),
            ('1a02sub7', 0),
            ('1a02sub8', 0),


            # TPDO 4
            ('1803sub1', (0x480 + self.node_id) | (1 << 31)),
            ('1803sub2', 0xFE),
            ('1803sub3', 0),
            ('1803sub5', 0),
            ('1803sub6', 0),
            ('1a03sub0', 0),
            ('1a03sub1', 0),
            ('1a03sub2', 0),
            ('1a03sub3', 0),
            ('1a03sub4', 0),
            ('1a03sub5', 0),
            ('1a03sub6', 0),
            ('1a03sub7', 0),
            ('1a03sub8', 0),

            ('1F80', 4),
            ('2300sub1', 1000),
            ('2300sub2', 1000),
            ('2310', 0x004E0000),
            ('2320sub1', 3),
            ('2320sub2', 3),
            ('2350', (1 << 4) | (1 << 3) | (1 << 2) | (1 << 1) | (1 << 0)),

            ('2450sub1', 0),
            ('2450sub1', 0),

            ('6001sub1', 1)
        )

        for element in test_items:
            entry = ODEntry.parce(element[0])
            v = entry.getvalue(self.node.sdo)
            print('Test item: {}'.format(entry))
            assert v == element[1]

    def test_default_values(self):
        self._test_defaults_common()

    @staticmethod
    def randomString(stringLength=10):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return b''.join(random.choice(letters).encode() for i in range(stringLength))

    @pytest.mark.parametrize("e,testvalue", [
        ('1005', 129),
        ('1006', 1001),
        ('1007', 100),
        ('1014', 0x183),
        ('1015', 10),
        ('1017', 1500),
        ('1019', 2),
        ('1029sub1', 0),
        ('1029sub2', 0),
        ('1029sub4', 0),
        ('1029sub5', 0),
        ('1029sub6', 0),

        # TPDO 1 disabled. Can't change values while enabled
        # ('1800sub2', 1),
        # ('1800sub3', 10),
        # ('1800sub5', 100),
        # ('1800sub6', 2),

        # TPDO 2 disabled. Can't change values while enabled
        # ('1801sub2', 1),
        # ('1801sub3', 10),
        # ('1801sub5', 100),
        # ('1801sub6', 2),

        # TPDO 3
        ('1802sub2', 1),
        ('1802sub3', 10),
        ('1802sub5', 100),
        ('1802sub6', 2),
        ('1a02sub1', 0x25000120),
        ('1a02sub2', 0x25000120),
        ('1a02sub3', 0),
        ('1a02sub4', 0),
        ('1a02sub5', 0),
        ('1a02sub6', 0),
        ('1a02sub7', 0),
        ('1a02sub8', 0),

        # TPDO 4
        ('1803sub2', 1),
        ('1803sub3', 10),
        ('1803sub5', 100),
        ('1803sub6', 2),
        ('1a03sub1', 0x25000120),
        ('1a03sub2', 0x25000120),
        ('1a03sub3', 0),
        ('1a03sub4', 0),
        ('1a03sub5', 0),
        ('1a03sub6', 0),
        ('1a03sub7', 0),
        ('1a03sub8', 0),

        ('1F80', 0),
        ('2005sub1', 2020),
        ('2005sub2', 10),
        ('2005sub3', 13),
        ('2300sub1', 100),
        ('2300sub2', 100),
        ('230A', b'0123456789'),
        ('2310', 0x00A40000),
        ('2320sub1', 2),
        ('2320sub2', -1),
        ('2350', 0xf),
        ('2450sub1', 10),
        ('2450sub2', -42),
    ])
    def test_wr_entries(self, e, testvalue):
        entry = ODEntry.parce(e)

        currentValue = entry.getvalue(self.node.sdo)
        assert currentValue is not None
        entry.setvalue(self.node.sdo, testvalue)
        if entry.index == 0x1014:
            assert testvalue + self.node_id == entry.getvalue(self.node.sdo)
        else:
            assert testvalue == entry.getvalue(self.node.sdo)

        entry.setvalue(self.node.sdo, currentValue)

    @pytest.mark.parametrize("e,testvalue", [
        ('2400sub1', random_float()),
        ('2400sub2', random_float()),
        ('2400sub3', random_float()),
        ('2400sub4', random_float()),
        ('2400sub5', random_float()),
        ('2400sub6', random_float()),
        ('2400sub7', random_float()),
        ('2400sub8', random_float()),
        ('2400sub9', random_float()),
        ('2400subA', random_float()),
        ('2400subB', random_float()),
        ('2400subC', random_float()),
        ('2400subD', random_float()),
        ('2400subE', random_float()),
        ('2400subF', random_float()),
        ('2400sub10', random_float()),
        ('2400sub11', random_float()),
        ('2400sub12', random_float()),

        ('2401sub1', random_float()),
        ('2401sub2', random_float()),
        ('2401sub3', random_float()),
        ('2401sub4', random_float()),
        ('2401sub5', random_float()),

        ('2402sub1', random_float()),
        ('2402sub2', random_float()),
        ('2402sub3', random_float()),
        ('2402sub4', random_float()),
        ('2402sub5', random_float()),

        ('24FF', 10000001),

        ('2370sub1', 12),
        ('2370sub2', 2001),
        ('2370sub3', 2030),

        ('2375sub1', -60),
        ('2375sub2', 100),
        ('2375sub3', 120),
        ('2375sub4', 105),

        ('237Asub1', 10),
        ('237Asub2', 95),

        ('23A0sub1', 13),
        ('23A0sub2', 9600),
        ('23A0sub3', 1),
        ('23A0sub4', False),
    ])
    def test_wr_passwordProtected(self, e, testvalue):
        entry = ODEntry.parce(e)

        currentValue = entry.getvalue(self.node.sdo)
        assert currentValue is not None

        # incorrect pass write attempt
        self.node.sdo[0x230A].raw = self.randomString(len(self.correct_password))
        with pytest.raises(canopen.sdo.exceptions.SdoAbortedError) as excinfo:
            entry.setvalue(self.node.sdo, testvalue)
        assert excinfo.value.code == 0x06010000

        assert (is_floats_equal(currentValue, entry.getvalue(self.node.sdo))) or \
               (math.isnan(currentValue) and math.isnan(entry.getvalue(self.node.sdo)))

        self.node.sdo[0x230A].raw = self.correct_password
        entry.setvalue(self.node.sdo, testvalue)
        assert is_floats_equal(testvalue, entry.getvalue(self.node.sdo))
        entry.setvalue(self.node.sdo, currentValue)  # restore

    def test_settings_save(self):
        # список ячеек и того, что будем записывать
        celllist = (
            '1014',
            '1015',

            # '2005sub1',
            '2005sub2',
            '2005sub3',

            '2400sub1',
            '2400sub2',
            '2400sub3',
            '2400sub4',
            '2400sub5',
            '2400sub6',
            '2400sub7',
            '2400sub8',
            '2400sub9',
            '2400subA',
            '2400subB',
            '2400subC',
            '2400subD',
            '2400subE',
            '2400subF',
            '2400sub10',
            '2400sub11',
            '2400sub12',

            '2401sub1',
            '2401sub2',
            '2401sub3',
            '2401sub4',
            '2401sub5',

            '2402sub1',
            '2402sub2',
            '2402sub3',
            '2402sub4',
            '2402sub5',

            '24FF',
            '2370sub1',
            '2370sub2',
            '2370sub3',
            '2375sub1',
            '2375sub2',
            '2375sub3',
            '2375sub4',
            '237Asub1',
            '237Asub2',
            '23A0sub1',
            '23A0sub2',
            '23A0sub3',
            '23A0sub4',

            '2450sub1',
            '2450sub2',

            '2310',
        )
        testvals = [0x325, 10] + \
                   [  # 2021,
                    4, 6] + \
                   [random_float() for i in range(28)] + \
                   [9999999, 3, 500, 600, -10, 70, 100, 103, 5, 75, 32, 9600, 3, True, 0.1, -3.84] + \
                   [0x00AB0000]

        # верный пароль
        self.node.sdo[0x230A].raw = self.correct_password

        # чтение старых значений
        oldvalues = [None] * len(testvals)
        for i in range(len(celllist)):
            entry = ODEntry.parce(celllist[i])
            oldvalues[i] = entry.getvalue(self.node.sdo)

        # запись
        for i in range(len(celllist)):
            entry = ODEntry.parce(celllist[i])
            entry.setvalue(self.node.sdo, testvals[i])

        # сохранение
        self.node.store()

        # ребут
        self.node.nmt.state = 'RESET'
        time.sleep(1)
        lss_set_node_id(self.network, self.node_id)
        self.node.nmt.wait_for_bootup(1)

        # проверка
        for i in range(len(celllist)):
            entry = ODEntry.parce(celllist[i])
            v = entry.getvalue(self.node.sdo)
            if entry.index == 0x1014:
                assert testvals[i] + self.node_id == v
            else:
                if type(v) is float:
                    assert is_floats_equal(v, testvals[i])
                else:
                    assert v == testvals[i]

        # Для восстановления также нужен пароль
        self.node.sdo[0x230A].raw = self.correct_password

        # восстановление оригинальных значений
        for i in range(len(celllist)):
            entry = ODEntry.parce(celllist[i])
            entry.setvalue(self.node.sdo, oldvalues[i])

        # запись
        self.node.store()

        # ребут
        self.node.nmt.state = 'RESET'
        time.sleep(1)
        lss_set_node_id(self.network, self.node_id);
        self.node.nmt.wait_for_bootup(1)

    @pytest.mark.parametrize("subindex,value", [
        (1, 1970),
        (1, 0),
        (1, current_year() - 1),
        (1, 2100),
        (2, 0),
        (2, 13),
        (3, 0),
        (2, 32),
    ])
    def test_incorrect_calibrationDate(self, subindex, value):
        with pytest.raises(canopen.sdo.exceptions.SdoAbortedError) as excinfo:
            self.node.sdo[0x2005][subindex].raw = value

        assert (excinfo.value.code == 0x6090031 or excinfo.value.code == 0x6090032)

    def test_reset_defaults(self):
        def disable_tpdo(index):
            entry = ODEntry.parce(index)
            return index, entry.getvalue(self.node.sdo) | (1 << 31)

        test_items = (
            # resetable values
            ('1005', 0x81),
            ('1006', 10),
            ('1007', 29),
            ('1014', self.node_id + 0x83),
            ('1015', 123),
            ('1017', 1234),
            ('1029sub1', 0),
            ('1029sub2', 0),
            ('1029sub4', 1),
            ('1029sub5', 1),
            ('1029sub6', 1),
            ('1200sub1', self.node_id + 0x601),
            ('1200sub2', self.node_id + 0x581),

            # Суть в том, что чтобы изменить TPDO нужно сначало отключить его (|= 1 << 31)
            # TPDO 1
            disable_tpdo('1800sub1'),
            ('1800sub1', 0x183 | (1 << 31)),
            ('1800sub2', 0x30),
            ('1800sub3', 1289),
            ('1800sub5', 555),
            ('1800sub6', 23),

            # TPDO 2
            disable_tpdo('1801sub1'),
            ('1801sub1', 0x286 | (1 << 31)),
            ('1801sub2', 0xFF),
            ('1801sub3', 512),
            ('1801sub5', 1024),
            ('1801sub6', 37),

            # TPDO 3
            disable_tpdo('1802sub1'),
            ('1802sub1', 0x386 | (1 << 31)),
            ('1802sub2', 0x78),
            ('1802sub3', 123),
            ('1802sub5', 321),
            ('1802sub6', 8),
            ('1a02sub0', 1),
            ('1a02sub1', 0x23200108),
            ('1a02sub2', 0),
            ('1a02sub3', 0),
            ('1a02sub4', 0),
            ('1a02sub5', 0),
            ('1a02sub6', 0),
            ('1a02sub7', 0),
            ('1a02sub8', 0),

            # TPDO 4
            disable_tpdo('1803sub1'),
            ('1803sub1', 0x481 | (1 << 31)),
            ('1803sub2', 0xF0),
            ('1803sub3', 321),
            ('1803sub5', 5),
            ('1803sub6', 7),
            ('1a03sub0', 2),
            ('1a03sub1', 0x25000120),
            ('1a03sub2', 0x25000220),
            ('1a03sub3', 0),
            ('1a03sub4', 0),
            ('1a03sub5', 0),
            ('1a03sub6', 0),
            ('1a03sub7', 0),
            ('1a03sub8', 0),

            ('1F80', 0),
            ('2300sub1', 128),
            ('2300sub2', 256),
            ('2310', 0x00220000),
            ('2320sub1', 0),
            ('2320sub2', 1),
            ('2350', 0),
            ('2450sub1', -0.53),
            ('2450sub2', -7.81),
        )

        for element in test_items:
            entry = ODEntry.parce(element[0])
            print('Writing: {}'.format(entry))
            entry.setvalue(self.node.sdo, element[1])

        self.node.sdo[0x1011][1].raw = 1  # reset
        self.node.store()

        self.node.nmt.state = 'RESET COMMUNICATION'
        self.node.nmt.wait_for_bootup(1)

        self._test_defaults_common()

    @pytest.mark.parametrize("code", [
        0x00220000,  # Pa
        0x004E0000,  # Bar
        0x00A10000,  # AT
        0x00A20000,  # mmH2O
        0x00A30000,  # mmHG
        0x00A40000,  # ATM
        0x00AB0000,  # PSI
        pytest.param(0, marks=pytest.mark.xfail),
        pytest.param(1, marks=pytest.mark.xfail),
        pytest.param(0xFFFFFFFF, marks=pytest.mark.xfail),
        pytest.param(0x00220001, marks=pytest.mark.xfail),
    ])
    def test_measure_units(self, code):
        self.node.sdo[0x2310].raw = code

        assert self.node.sdo[0x6100][2].raw == code  # check mapping

    @pytest.mark.parametrize("chanel", (0, 1))
    @pytest.mark.parametrize("value", (-100, -3.5, 1.3, 100, 0))
    def test_zero_correction(self, chanel, value):
        mapping = (('2450sub1', '2500sub1'), ('2450sub2', '2500sub2'))

        correction_index = ODEntry.parce(mapping[chanel][0])
        result_index = ODEntry.parce(mapping[chanel][1])

        measure_time = int(self.node.sdo[0x2300][chanel + 1].raw * 1.1 / 1000)

        correction_index.setvalue(self.node.sdo, 0)
        time.sleep(measure_time)
        base_value = result_index.getvalue(self.node.sdo)
        correction_index.setvalue(self.node.sdo, value)
        time.sleep(measure_time)
        corrected_value = result_index.getvalue(self.node.sdo)

        assert math.fabs(base_value + value - corrected_value) < 2

    @pytest.mark.parametrize("index", (0x6100, 0x6101))
    def test_user_limits(self, index):
        valueEntry = ODEntry(index, 1)
        flagsEntry = ODEntry(index, 3)

        UpperLimitEntry = ODEntry(index, 4)
        LowerLimitEntry = ODEntry(index, 5)

        currentValue = valueEntry.getvalue(self.node.sdo)

        UpperLimitEntry.setvalue(self.node.sdo, currentValue - 10)
        assert flagsEntry.getvalue(self.node.sdo) == 1 << 1

        UpperLimitEntry.setvalue(self.node.sdo, currentValue + 10)
        assert flagsEntry.getvalue(self.node.sdo) & (1 << 1) == 0

        LowerLimitEntry.setvalue(self.node.sdo, currentValue + 10)
        assert flagsEntry.getvalue(self.node.sdo) == 1 << 2

        LowerLimitEntry.setvalue(self.node.sdo, currentValue - 10)
        assert flagsEntry.getvalue(self.node.sdo) & (1 << 2) == 0
