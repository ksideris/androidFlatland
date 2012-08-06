#!/usr/bin/env python

"""networkserver.py: Script to launch the network server."""

__author__      = "Konstantinos Sideris"
__copyright__   = "Copyright 2012, UCLA game lab"

from game.network.UDPServer import UDPServer

print 'Server launched at: ','127.0.0.1:80'
UDPServer().start('127.0.0.1',80)


