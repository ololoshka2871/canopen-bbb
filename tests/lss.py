
import pytest
import canopen
from canopen_lss_fastscan import fast_scan

# bootloader LSS id
vendor_id = 0x004f038C
product_id = 0xCB01
revision = 0
serial_number = 1

@pytest.fixture
def network():
    network = canopen.Network()
    network.connect(channel='can0', bustype='socketcan')
    return network


# not working in library
#def test_identify_remote_slave(network):
#    assert network.lss.send_identify_remote_slave(vendor_id, product_id, 
#        0, 1, 1, 2)

def test_set_config_mode(network):
    network.lss.send_switch_state_global(network.lss.CONFIGURATION_STATE)
    network.lss.send_switch_state_global(network.lss.WAITING_STATE)


def test_set_config_mode_by_id(network):
    assert network.lss.send_switch_state_selective(
            vendor_id, product_id, revision, serial_number)
    network.lss.send_switch_state_global(network.lss.WAITING_STATE)
    

def test_configure_bit_timing(network):
    test_matrix = (
        (0, False),
        (1, False),
        (2, False),
        (3, False),
        (4, True),
        (6, True),
        (7, True),
        (8, True)
    )
    
    assert network.lss.send_switch_state_selective(
            vendor_id, product_id, revision, serial_number)

    for speed_grade, res in test_matrix:
        try:
            network.lss.configure_bit_timing(speed_grade)
            passed = res == True
        except canopen.lss.LssError as e:
            passed = str(e) == 'LSS Error: 1' and res == False

        if not passed:
            network.lss.send_switch_state_global(network.lss.WAITING_STATE)
            raise Exception('Exception at speed {}'.format(speed_grade))
    
    network.lss.send_switch_state_global(network.lss.WAITING_STATE)


def test_inquire_lss_address(network):
    assert network.lss.send_switch_state_selective(
             vendor_id, product_id, revision, serial_number)
    
    assert vendor_id == network.lss.inquire_lss_address(canopen.lss.CS_INQUIRE_VENDOR_ID)
    assert product_id == network.lss.inquire_lss_address(canopen.lss.CS_INQUIRE_PRODUCT_CODE)
    assert revision == network.lss.inquire_lss_address(canopen.lss.CS_INQUIRE_REVISION_NUMBER)
    assert serial_number == network.lss.inquire_lss_address(canopen.lss.CS_INQUIRE_SERIAL_NUMBER)

    network.lss.send_switch_state_global(network.lss.WAITING_STATE)

def test_set_node_id(network):
    assert network.lss.send_switch_state_selective(
            vendor_id, product_id, revision, serial_number)

    for node_id in (1, 15, 127, 255):
        network.lss.configure_node_id(node_id)
        assert node_id == network.lss.inquire_node_id()
    network.lss.send_switch_state_global(network.lss.WAITING_STATE)

