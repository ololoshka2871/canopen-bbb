
import canopen

# bootloader LSS id
boot_vendor_id = 0x004f038C
boot_product_id = 0xCB01
boot_revision = 0
boot_serial_number = 1


def create_network(device='can1'):
    network = canopen.Network()
    network.connect(channel=device, bustype='socketcan')
    return network


def bootloader_lss_configuration_state(network):
    try:
        network.lss.send_switch_state_selective(
            boot_vendor_id, boot_product_id, boot_revision, boot_serial_number)
    except canopen.lss.LssError:
        network.lss.send_switch_state_global(network.lss.CONFIGURATION_STATE)
    

def lss_waiting_state(network):
    network.lss.send_switch_state_global(network.lss.WAITING_STATE)


def set_node_id(network, node_id):
    bootloader_lss_configuration_state(network)
    network.lss.configure_node_id(node_id)
    network.lss.store_configuration()
    lss_waiting_state(network)
