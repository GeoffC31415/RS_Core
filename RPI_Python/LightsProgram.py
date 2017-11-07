#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  LightsOn.py
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


def main(args):
	
	import RPi.GPIO as GPIO
	from datetime import datetime
	import time
	
	GPIO.setmode(GPIO.BCM)

	# init list with pin numbers
	#pumpList = [21, 20, 16, 12]
	lightList = [21]
	heaterList = [16]
	pumpList = [12]
	
	# loop through pins and set mode and state to 'high'
	# HIGH is off, LOW is ON
	for i in lightList: 
		GPIO.setup(i, GPIO.OUT) 
		GPIO.output(i, GPIO.HIGH)
	for i in heaterList: 
		GPIO.setup(i, GPIO.OUT) 
		GPIO.output(i, GPIO.HIGH)
	for i in pumpList: 
		GPIO.setup(i, GPIO.OUT) 
		GPIO.output(i, GPIO.HIGH)
			
	# Lightstatus holds the current light values to prevent constant spam of the messages
	# 0 is off, 1 is on
	# preset to 0 as the previous loop turns lights off
	lightstatus = 0
	heaterstatus = 0
	pumpstatus = 0
	# Grab the lighting times from the settings database
	
	
	# main loop
	#
	# Check time every minute and trigger lights on and off
	
	while 1:
		curtime = datetime.now().time()
	
		# Lights Loop
		if ((curtime.hour >= 8) and (curtime.hour < 20)):
			if lightstatus == 0:
				print 'Setting lights to on...'
				for i in lightList:
					GPIO.output(i, GPIO.LOW)
				print 'Lights on, currrent time is ' + str(curtime)
				lightstatus = 1			
		else:
			if lightstatus == 1:
				print 'Setting lights to off...'
				for i in lightList: 
					GPIO.output(i, GPIO.HIGH)
				print 'Lights off, currrent time is ' + str(curtime)
				lightstatus = 0
				
				
		# Heater Loop
		if 	((curtime.hour >= 0) and (curtime.hour < 24)):
			if heaterstatus == 0:
				print 'Setting heater to on...'
				for i in heaterList:
					GPIO.output(i, GPIO.LOW)
				print 'Heater setting on, current time is ' + str(curtime)
				heaterstatus = 1
		else:
			if heaterstatus == 1:
				print 'Setting heater to off...'
				for i in heaterList:
					GPIO.output(i, GPIO.HIGH)
				print 'Heater setting off, current time is ' + str(curtime)
				heaterstatus = 0

		# Pump Loop
		if 	((curtime.hour >= 0) and (curtime.hour < 24)):
			if pumpstatus == 0:
				print 'Setting pump to on...'
				for i in pumpList:
					GPIO.output(i, GPIO.LOW)
				print 'Pump setting on, current time is ' + str(curtime)
				pumpstatus = 1
		else:
			if pumpstatus == 1:
				print 'Setting pump to off...'
				for i in pumpList:
					GPIO.output(i, GPIO.HIGH)
				print 'Pump setting off, current time is ' + str(curtime)
				pumpstatus = 0
						
		time.sleep(60)
		
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))