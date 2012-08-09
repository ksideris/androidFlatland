#!/usr/bin/python

import time

import libs.beacon as beacon

b = beacon.Beacon(12000, "flatland_arg")
print 'Beacon Active!'
b.daemon = True
b.start()

time.sleep(10000)
