
import canopen

# bootloader LSS id
vendor_id = 0x004f038C
product_id = 0xCB01
revision = 0
serial_number = 1


def create_network(device='can1'):
    network = canopen.Network()
    network.connect(channel=device, bustype='socketcan')
    return network


def bootloader_lss_configuration_state(network):
    assert network.lss.send_switch_state_selective(
            vendor_id, product_id, revision, serial_number)
    

def lss_waiting_state(network):
    network.lss.send_switch_state_global(network.lss.WAITING_STATE)

