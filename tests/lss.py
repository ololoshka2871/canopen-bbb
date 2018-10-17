
import pytest
import canopen
from canopen_lss_fastscan import fast_scan
from common import *

@pytest.fixture
def network():
    return create_network()


# not working in library
#def test_identify_remote_slave(network):
#    assert network.lss.send_identify_remote_slave(vendor_id, product_id, 
#        0, 1, 1, 2)

def test_set_config_mode(network):
    network.lss.send_switch_state_global(network.lss.CONFIGURATION_STATE)
    network.lss.send_switch_state_global(network.lss.WAITING_STATE)


def test_set_config_mode_by_id(network):
    lss_configuration_state(network)
    lss_waiting_state(network)
    

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

    lss_configuration_state(network)

    for speed_grade, res in test_matrix:
        try:
            network.lss.configure_bit_timing(speed_grade)
            passed = res == True
        except canopen.lss.LssError as e:
            passed = str(e) == 'LSS Error: 1' and res == False

        if not passed:
            network.lss.send_switch_state_global(network.lss.WAITING_STATE)
            raise Exception('Exception at speed {}'.format(speed_grade))

    lss_waiting_state(network)    


def test_inquire_lss_address(network):
    lss_configuration_state(network)
    
    assert boot_vendor_id == network.lss.inquire_lss_address(canopen.lss.CS_INQUIRE_VENDOR_ID)
    assert 0 != network.lss.inquire_lss_address(canopen.lss.CS_INQUIRE_PRODUCT_CODE)
    assert 0 < network.lss.inquire_lss_address(canopen.lss.CS_INQUIRE_REVISION_NUMBER)
    assert network.lss.inquire_lss_address(canopen.lss.CS_INQUIRE_SERIAL_NUMBER) is not None

    lss_waiting_state(network)


def test_set_node_id(network):
    lss_configuration_state(network)

    for node_id in (1, 15, 127, 255):
        network.lss.configure_node_id(node_id)
        assert node_id == network.lss.inquire_node_id()

    lss_waiting_state(network)
