#!/usr/bin/env python
# -*- coding: utf-8 -*-


from common import *

network = create_network()
network.nmt.state = 'RESET'
network.disconnect()
