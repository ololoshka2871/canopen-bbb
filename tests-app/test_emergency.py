# -*- coding: utf-8 -*-

# minimalmodbus required

from common import *
from ODEntry import *
import time
import minimalmodbus
import serial
import canopen


class TestEmergency(object):
    @classmethod
    def setup_class(cls):
        cls.network = create_network()
        cls.node_id = 42
        reset_network(cls.network)
        time.sleep(0.5)

        # lss prepare node
        lss_waiting_state(cls.network)
        cls.node = canopen.RemoteNode(cls.node_id, 'SCTB_CANopenPressureSensor0xC001.eds')
        cls.node.associate_network(cls.network)
        lss_set_node_id(cls.network, cls.node_id)
        cls.node.nmt.wait_for_bootup(1)
        # cls.node.emcy.wait
        time.sleep(1)

        instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 4)
        instrument.serial.baudrate = 57600         # Baud
        instrument.serial.bytesize = 8
        instrument.serial.parity = serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout = 0.05          # seconds
        cls.port = instrument

    @classmethod
    def teardown_class(cls):
        cls.node.remove_network()
        cls.network.disconnect()

    def test_all_emcy(self):
        def emcy_logger(error):
            print(' code={}\terr={}\tdata={}'.format(error.register, error.code, error.data.hex()))

        self.node.emcy.add_callback(emcy_logger)

        for flag in range(60):
            print("Set err: {} =>".format(flag), end='')
            self.port.write_register(0x7000, flag)  # set
            time.sleep(0.1)
            print("Rst err: {} =>".format(flag), end='')
            self.port.write_register(0x7001, flag)  # reset
            time.sleep(0.1)

