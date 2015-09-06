
import canopen
from lss import network, vendor_id, product_id, revision, serial_number

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
    nw = network()
    # put device in config mode
    assert nw.lss.send_switch_state_selective(
            vendor_id, product_id, revision, serial_number)

    grade = speed_map[speed]

    print('New speed grade {}'.format(grade))

    # set new bit timing
    nw.lss.configure_bit_timing(grade)

    # store configuration
    nw.lss.store_configuration()

    # activate new bitrate
    nw.lss.activate_bit_timing(100)

    # put device to waiting mode back
    nw.lss.send_switch_state_global(nw.lss.WAITING_STATE)

