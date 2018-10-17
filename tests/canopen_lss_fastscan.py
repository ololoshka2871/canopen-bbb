#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import canopen
from canopen.lss import ListMessageNeedResponse, LssError
try:
    import queue
except ImportError:
    import Queue as queue


# conflict types in python2. 
# Message and return type mast be bytearray, not str
def new__send_command(self, message):
    m = bytearray()
    m.extend(message)
    message = m

    response = None
    if not self.responses.empty():
        self.responses = queue.Queue()

    self.network.send_message(self.LSS_TX_COBID, message)

    if not bool(message[0] in ListMessageNeedResponse):
        return response

    # Wait for the slave to respond
    # TODO check if the response is LSS response message
    try:
        response = self.responses.get(
            block=True, timeout=self.RESPONSE_TIMEOUT)
    except queue.Empty:
        raise LssError("No LSS response received")
    
    r = bytearray()
    r.extend(response)
    return r


def fast_scan(lssMaster, put_config_state=True):
    old__send_command = lssMaster._LssMaster__send_command
    funcType = type(lssMaster._LssMaster__send_command)
    lssMaster._LssMaster__send_command = \
         funcType(new__send_command, lssMaster, canopen.lss.LssMaster)
    res = lssMaster.fast_scan()
    lssMaster._LssMaster__send_command = old__send_command
    if not put_config_state:
        lssMaster.send_switch_state_global(lssMaster.WAITING_STATE)
    return res


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-I', '--interface', type=str, default='can0', help='Can interface, default can0')
    args = parser.parse_args()
    
    nw = canopen.Network()
    nw.connect(channel=args.interface, bustype='socketcan')
    if int(sys.version[0]) == 2:
        res = fast_scan(nw.lss, False)
    else:
        res = nw.lss.fast_scan()
        nw.lss.send_switch_state_global(nw.lss.WAITING_STATE)
    if res[0]:
        LSS_id = res[1]
        print('Found unconfigured device:')
        print('''Vendor_ID = 0x{:X}
Product Code = 0x{:X}
Revision Number = {}
Serial Number = {}'''.format(*LSS_id))
    else:
        print('Fast scan failled.')
