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
	import RS_Database as db
	
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	db.connect_to_db()
	
	# init list with pin numbers
	lightList = [21]
	heaterList = [16]
	pumpList = [12]
	
	# Pull times from settings database
	# Need to basically do an index-match on ons and offs
	#lightsOn = RS_Database.getLightsTimes(1)
	#lightsOff = RS_Database.getLightsTimes(0)
	
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
	db_dirty = 0
	
	# Timings
	STARTHOUR_LIGHTS = 20
	STOPHOUR_LIGHTS = 8
	STARTHOUR_PUMP = 0
	STOPHOUR_PUMP = 24
	STARTHOUR_HEATER = 0
	STOPHOUR_HEATER = 24
	
	# main loop
	#
	# Check time every minute and trigger lights on and off
	
	while 1:
		curtime = datetime.now().time()
		curdt = datetime.now()

		# Lights Loop (spanning midnight)
		if ((curtime.hour >= STARTHOUR_LIGHTS) or (curtime.hour < STOPHOUR_LIGHTS)):
			if lightstatus == 0:
				print 'Setting lights to on...'
				for i in lightList:
					GPIO.output(i, GPIO.LOW)
				print 'Lights on, currrent time is ' + str(curtime)
				lightstatus = 1
				db.log_relay(curdt,'Lights',1)
				db_dirty = 1
		else:
			if lightstatus == 1:
				print 'Setting lights to off...'
				for i in lightList: 
					GPIO.output(i, GPIO.HIGH)
				print 'Lights off, currrent time is ' + str(curtime)
				lightstatus = 0
				db.log_relay(curdt,'Lights',0)
				db_dirty = 1
				
		# Heater Loop
		if 	((curtime.hour >= STARTHOUR_PUMP) and (curtime.hour < STOPHOUR_PUMP)):
			if heaterstatus == 0:
				print 'Setting heater to on...'
				for i in heaterList:
					GPIO.output(i, GPIO.LOW)
				print 'Heater setting on, current time is ' + str(curtime)
				heaterstatus = 1
				db.log_relay(curdt,'Heater',1)
				db_dirty = 1
		else:
			if heaterstatus == 1:
				print 'Setting heater to off...'
				for i in heaterList:
					GPIO.output(i, GPIO.HIGH)
				print 'Heater setting off, current time is ' + str(curtime)
				heaterstatus = 0
				db.log_relay(curdt,'Heater',0)
				db_dirty = 1

		# Pump Loop
		if 	((curtime.hour >= STARTHOUR_HEATER) and (curtime.hour < STOPHOUR_HEATER)):
			if pumpstatus == 0:
				print 'Setting pump to on...'
				for i in pumpList:
					GPIO.output(i, GPIO.LOW)
				print 'Pump setting on, current time is ' + str(curtime)
				pumpstatus = 1
				db.log_relay(curdt,'Pump',1)
				db_dirty = 1
		else:
			if pumpstatus == 1:
				print 'Setting pump to off...'
				for i in pumpList:
					GPIO.output(i, GPIO.HIGH)
				print 'Pump setting off, current time is ' + str(curtime)
				pumpstatus = 0
				db.log_relay(curdt,'Pump',0)
				db_dirty = 1
						
		if db_dirty == 1:
			db.commit_DB()
			db_dirty = 0
			
		time.sleep(30)
		
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
