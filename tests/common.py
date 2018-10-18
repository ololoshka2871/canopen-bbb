
import canopen
import re
import subprocess
import time


# bootloader LSS id
boot_vendor_id = 0x004f038C
boot_product_id = 0xCB01
boot_revision = 0
boot_serial_number = 1

default_interface = 'can1'


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


class FlashStatus:
    NO_OPERATION = 0
    OK = 1
    LOCKED = 2
    ADDRESS_OUT_OF_RANGE = 3
    ERASE_FAIL = 4
    WRITE_FAIL = 5
    ALIGNMENT_ERROR = 6
    SEQUENCE_CORRUPT = 7
    INVALID_PROGRAM = 8
    READY_TO_START = 9


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


def lss_set_node_id(network, node_id):
    lss_configuration_state(network)
    network.lss.configure_node_id(node_id)
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
