# accelreader.py - Read smoothed accelerometer values
#
# Original algorithm ported from liqaccel.c
#
# Copyright (c) 2011 by Jonathan Dieter <jdieter@lesbg.com>
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA

import dbus
import time

class AccelReader:
	def __init__(self):
		bus = dbus.SystemBus()
		self.accel = bus.get_object('com.nokia.mce', '/com/nokia/mce/request', 'com.nokia.mce.request')
		orientation, stand, face, x, y, z = self.accel.get_device_orientation()
		(self.x, self.y, self.z) = (x, y, z)
		self.time = time.time()

	def get_pos(self):	
		orientation, stand, face, x, y, z = self.accel.get_device_orientation()
		new_time = time.time()
		time_modifier = (new_time - self.time)
		self.time = new_time
		time_modifier = time_modifier * 2

		if time_modifier > 1:
			time_modifier = 1
		elif time_modifier < 0.1:
			time_modifier = 0.1

		self.x = self.x + (x - self.x) * time_modifier
		self.y = self.y + (y - self.y) * time_modifier
		self.z = self.z + (z - self.z) * time_modifier
	
		return (self.x, self.y, self.z)

if __name__ == "__main__":
	reader = AccelReader()
	while True:        
		print reader.get_pos()
