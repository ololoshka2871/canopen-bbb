
import canopen
from common import *

speed_map = {
    10000 : 8,
    20000 : 7,
    50000 : 6,
    125000 : 4,
    250000 : 3,
    500000 : 2,
    800000 : 1,
    1000000 : 0,
}

def set_bitrate(speed):
    nw = create_network()
    
    # put device in config mode
    bootloader_lss_configuration_state(nw)
    
    grade = speed_map[speed]

    # set new bit timing
    nw.lss.configure_bit_timing(grade)

    # store configuration
    nw.lss.store_configuration()

    # activate new bitrate
    nw.lss.activate_bit_timing(100)

    # put device to waiting mode back
    lss_waiting_state(nw)

