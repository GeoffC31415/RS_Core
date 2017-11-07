#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  WriteRecords.py
#  
#  Copyright 2017  <pi@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from datetime import datetime
import PullReading
import RS_Database
import time
import os
from picamera import PiCamera

def main():
	RS_Database.connect_to_db()
	camera = PiCamera()
	loopcounter = 0
	
	while True:
		
		curtime = datetime.now()
		
		# DHT sensors. Numbers result in logging of two readings for each sensor
		# Array lists sensornums according to the Sensors DB Table
		# These must all be listed ahead of analog sensors for the x-formula to work
		for x in [1,2,4]:
			DHT_Readings = PullReading.GetDHTReading(x)
			RS_Database.write_reading(
									curtime, 
									2*x - 1, 
									DHT_Readings[0]
									 )
			RS_Database.write_reading(
									curtime, 
									2*x, 
									DHT_Readings[1]
									 )
		# Analog sensors
		# Array lists sensornums according to the Sensors DB Table
		for x in [9]:
			RS_Database.write_reading(
									curtime, 
									x, 
									PullReading.GetReading(x)
									 )
		
		RS_Database.commit_DB()
		
		if loopcounter % 12 == 0:
			# Archive the most recent image
			curfile = '/var/www/html/RS_Website/images/image_recent.jpg'
			arcfile = '/var/www/html/RS_Website/images/image_' + time.strftime("%Y%m%d%H%M%S") + '.jpg'
			try:
				os.rename(curfile, arcfile)
			except:
				print "File rename failed"
			# Record an image of the setup
			camera.capture(curfile)
			print "Image captured, loop counter is " + str(loopcounter)
		
		loopcounter += 1
		time.sleep(60*5)
		
	return 0


if __name__ == '__main__':
	main()
	
