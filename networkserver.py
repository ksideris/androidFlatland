#!/usr/bin/env python

"""networkserver.py: Script to launch the network server."""

__author__      = "Konstantinos Sideris"
__copyright__   = "Copyright 2012, UCLA game lab"

from game.network.UDPServer import UDPServer
import libs.beacon as beacon
while True:
    server = beacon.find_server(12000, b"flatland_arg")
    if server<>None:
        break
print 'Server launched at: ',server,':56000'
UDPServer().start(server,56000)


