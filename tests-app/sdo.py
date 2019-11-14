# -*- coding: utf-8 -*-

from common import *
from ODEntry import *
import canopen
import pytest
import random
import string
import math


def random_float():
    return float(random.uniform(-10, 10))


def is_floats_equal(f1, f2, max_diff=1e-6):
    return math.fabs(f1 - f2) < max_diff


class TestSDO(object):
    @classmethod
    def setup_class(cls):
        cls.network = create_network()
        cls.node_id = 19
        cls.correct_password = '_PASSWORD_'
        reset_network(cls.network)

        # lss prepare node
        lss_waiting_state(cls.network)
        lss_set_node_id(cls.network, cls.node_id)
        cls.node = canopen.RemoteNode(cls.node_id, 'SCTB_CANopenPressureSensor0xC001.eds')
        cls.node.associate_network(cls.network)
        cls.node.nmt.state = 'OPERATIONAL'

    @classmethod
    def teardown_class(cls):
        cls.node.nmt.state = 'PRE-OPERATIONAL'
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
                              '1014',
                              '1022',
                              '1200sub1',
                              '1200sub2',
                              '2100',
                              '2360',
                              '2500sub1',
                              '2500sub2',
                              '2501sub1',
                              '2501sub2',
                              '2510sub1',
                              '2510sub2',
                              '2510sub3',
                              '2510sub4',
                              '25FFsub1',
                              '25FFsub2',
                              '25FFsub3',
                              '25FFsub4',
                              '25FFsub5',
                              '25FFsub6'])
    def test_ro_entries(self, ro_entry):
        """
        Все по честному, либа действительно пытается записать в эти индексы,
        и должна получить верный код ошибки
        """
        entry = ODEntry.parce(ro_entry)
        assert entry.getvalue(self.node.sdo) is not None

        with pytest.raises(canopen.sdo.exceptions.SdoAbortedError) as excinfo:
            entry.setvalue(self.node.sdo, entry.getvalue(self.node.sdo))

        assert excinfo.value.code == 0x06010002  # readonly

    @staticmethod
    def randomString(stringLength=10):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    @pytest.mark.parametrize("e,testvalue", [
        ('1005', 129),
        ('1006', 1001),
        ('1007', 100),
        ('1015', 10),
        ('1017', 1500),
        ('1019', 2),
        ('1029sub1', 0),
        ('1029sub2', 0),
        ('1029sub4', 0),
        ('1029sub5', 0),
        ('1029sub6', 0),

        # TPDO 1
        ('1800sub2', 1),
        ('1800sub3', 10),
        ('1800sub5', 100),
        ('1800sub6', 2),
        ('1a00sub1', 0x25000120),
        ('1a00sub2', 0x25000120),
        ('1a00sub3', 0),
        ('1a00sub4', 0),
        ('1a00sub5', 0),
        ('1a00sub6', 0),
        ('1a00sub7', 0),
        ('1a00sub8', 0),

        # TPDO 2
        ('1801sub2', 1),
        ('1801sub3', 10),
        ('1801sub5', 100),
        ('1801sub6', 2),
        ('1a01sub1', 0x25000120),
        ('1a01sub2', 0x25000120),
        ('1a01sub3', 0),
        ('1a01sub4', 0),
        ('1a01sub5', 0),
        ('1a01sub6', 0),
        ('1a01sub7', 0),
        ('1a01sub8', 0),

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

        # TPDO 5
        ('1804sub2', 1),
        ('1804sub3', 10),
        ('1804sub5', 100),
        ('1804sub6', 2),
        ('1a04sub1', 0x25000120),
        ('1a04sub2', 0x25000120),
        ('1a04sub3', 0),
        ('1a04sub4', 0),
        ('1a04sub5', 0),
        ('1a04sub6', 0),
        ('1a04sub7', 0),
        ('1a04sub8', 0),

        ('1F80', 0),
        ('2300sub1', 100),
        ('2300sub2', 100),
        ('230A', '0123456789'),
        ('2310', 1),
        ('2320sub1', 2),
        ('2320sub2', -1),
        ('2350', 3),
    ])
    def test_wr_entries(self, e, testvalue):
        entry = ODEntry.parce(e)

        currentValue = entry.getvalue(self.node.sdo)
        assert currentValue is not None
        entry.setvalue(self.node.sdo, testvalue)
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
