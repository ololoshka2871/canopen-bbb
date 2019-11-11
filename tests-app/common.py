# -*- coding: utf-8 -*-

import canopen
import struct
import subprocess
import time


# bootloader LSS id
boot_vendor_id = 0x004f038C
boot_product_id = 0xC001
boot_revision = 0
boot_serial_number = 1

default_interface = 'can0'


speed_map = {
    10000: 8,
    20000: 7,
    50000: 6,
    125000: 4,
    250000: 3,
    500000: 2,
    800000: 1,
    1000000: 0,
}

headed_size = 9 * 4


class Error_CODE(object):
    def __init__(self, code):
        self.code = code
        self.Class = code >> 12 & 0x0F
        self.additional_info = code & 0x0FFF


class ErrorCategorie:
    NO_ERROR = 0x0000
    GENERIC_ERROR_GROUP = 0x1000
    CURRENT_ERROR_GROUP = 0x2000
    VOLTAGE_ERROR_GROUP = 0x3000
    TEMPERATURE_ERROR_GROUP = 0x4000
    DEVICE_HARDWARE_ERROR_GROUP = 0x5000
    DEVICE_SOFTWARE_ERROR_GROUP = 0x6000
    ADDITIONAL_MODULES_ERROR_GROUP = 0x7000
    MONITORING_ERROR_GROUP = 0x8000
    EXTERNAL_ERROR_GROUP = 0x9000
    ADDITIONAL_FUNCTIONS_GROUP = 0xF000


class Error_CODES:
    NO_ERROR = ErrorCategorie.NO_ERROR  #
    FLASH_UNLOCK_FAILED = ErrorCategorie.DEVICE_HARDWARE_ERROR_GROUP | 0x550
    FLASH_ERASE_FAILED = ErrorCategorie.DEVICE_HARDWARE_ERROR_GROUP | 0x580
    FLASH_WRITE_FAILED = ErrorCategorie.DEVICE_HARDWARE_ERROR_GROUP | 0x590
    APPLICATION_INCORRECT_OR_NOT_EXISTS = ErrorCategorie.DEVICE_SOFTWARE_ERROR_GROUP | 0x200
    #WRITE_TRANSACTION_WAS_CANCELED = ErrorCategorie.DEVICE_SOFTWARE_ERROR_GROUP | 0x220
    FLASH_SEQUENCE_CORRUPT = ErrorCategorie.DEVICE_SOFTWARE_ERROR_GROUP | 0x251
    #FLASH_SEQUENCE_BUSY = ErrorCategorie.DEVICE_SOFTWARE_ERROR_GROUP | 0x253
    APPLICATION_TOO_LARGE = ErrorCategorie.DEVICE_SOFTWARE_ERROR_GROUP | 0x300
    #FLASH_ADDRESS_OUT_OF_RANGE = ErrorCategorie.DEVICE_SOFTWARE_ERROR_GROUP | 0x330
    #FLASH_IMAGE_SIZE_ODD = ErrorCategorie.DEVICE_SOFTWARE_ERROR_GROUP | 0x340
    FLASH_ALIGNMENT_ERROR = ErrorCategorie.DEVICE_SOFTWARE_ERROR_GROUP | 0x5A0
    APPLICATION_READY_TO_START = ErrorCategorie.DEVICE_SOFTWARE_ERROR_GROUP | 0x2FF


def create_network(device=default_interface):
    network = canopen.Network()
    network.connect(channel=device, bustype='socketcan')
    return network


def lss_configuration_state(network):
    try:
        network.lss.send_switch_state_selective(
            boot_vendor_id, boot_product_id, boot_revision, boot_serial_number)
    except canopen.lss.LssError:
        network.lss.send_switch_state_global(network.lss.CONFIGURATION_STATE)
    

def lss_waiting_state(network):
    network.lss.send_switch_state_global(network.lss.WAITING_STATE)


def reset_network(network):
    network.nmt.state = 'RESET'
    time.sleep(0.1)


def network_operational(network):
    network.nmt.state = 'OPERATIONAL'
    time.sleep(0.1)


def lss_configure_bit_timing(network, speed):
    lss_configuration_state(network)
    network.lss.configure_bit_timing(speed_map[speed])
    network.lss.store_configuration()
    lss_waiting_state(network)


def lss_set_node_id(network, node_id):
    lss_configuration_state(network)
    network.lss.configure_node_id(node_id)
    network.lss.store_configuration()
    lss_waiting_state(network)


def lss_configure_node(network, node_id, speed):
    lss_configuration_state(network)
    network.lss.configure_node_id(node_id)
    network.lss.configure_bit_timing(speed_map[speed])
    network.lss.store_configuration()
    lss_waiting_state(network)


def bootloader_start_app(node):
    node.sdo[0x1F51][1].raw = 1


def set_interface_bitrate(bitrate, interface=default_interface):
    commad_down = 'sudo ip link set {} down'.format(interface)
    commad_up = 'sudo ip link set {} up type can bitrate {} loopback off'.format(interface, bitrate)

    if _execute_command(commad_down) > 0:
        raise Exception("Interface Down exception")
    if _execute_command(commad_up) > 0:
        raise Exception("Interface UP exception")


def _execute_command(command):
    process = subprocess.Popen(command.split(' '))
    return process.wait()
