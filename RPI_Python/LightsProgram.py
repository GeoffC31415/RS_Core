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
	from datetime import datetime, timedelta
	import time
	import RS_Database as db
	from picamera import PiCamera
	import os
	from influxdb import InfluxDBClient
 
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	db.connect_to_db()
	
	# init list with pin numbers
	lightList = [21]
	heaterList = [16]
	pumpList = [12]
	# Timings
	STARTHOUR_LIGHTS = 20
	STOPHOUR_LIGHTS = 22
	STARTHOUR_PUMP = 0
	STOPHOUR_PUMP = 24
	STARTHOUR_HEATER = 0
	STOPHOUR_HEATER = 24
	# Parameters
	PICTUREINTERVALHRS = 1
	HEATERQRY = 'select mean(DHT2_Temp) from dev where time > now() - 15m'
	TARGETTEMP = 21
	curtemp = []
	
	# InfluxDB variables and initialisation
	host = "localhost"
	port = 8086
	user = "root"
	password = "root"
	dbname = "RS_Logs"
	# Create the InfluxDB object
	client = InfluxDBClient(host, port, user, password, dbname)
	
	# loop through pins and set mode and state to 'high'
	# HIGH is off, LOW is ON
	print 'Initialising all outputs to off...'
	for i in lightList:
		GPIO.setup(i, GPIO.OUT)
		GPIO.output(i, GPIO.HIGH)
	for i in heaterList: 
		GPIO.setup(i, GPIO.OUT) 
		GPIO.output(i, GPIO.HIGH)
	for i in pumpList: 
		GPIO.setup(i, GPIO.OUT) 
		GPIO.output(i, GPIO.HIGH)
			
	camera = PiCamera()
			
	# Lightstatus holds the current light values to prevent constant spam of the messages
	# 0 is off, 1 is on
	# preset to 0 as the previous loop turns lights off
	lightstatus = 0
	heaterstatus = 0
	pumpstatus = 0
	db_dirty = 0
	
	nextphototime = datetime.now() - timedelta(hours=1+PICTUREINTERVALHRS)
	
	# main loop
	#
	# Check time every minute and trigger lights on and off
	
	while 1:
		curtime = datetime.now().time()
		curdt = datetime.now()

		# Lights Loop (if spanning midnight then the AND should be an OR - check if clause carefully)
		if ((curtime.hour >= STARTHOUR_LIGHTS) and (curtime.hour < STOPHOUR_LIGHTS)):
			if lightstatus == 0:
				print str(time.ctime()) + '    Setting lights to on...'
				for i in lightList:
					GPIO.output(i, GPIO.LOW)
				print str(time.ctime()) + '    Lights on'
				lightstatus = 1
				db.log_relay(curdt,'Lights',1)
				db_dirty = 1
				#Give lights time to power up a bit
				time.sleep(5)
		else:
			if lightstatus == 1:
				print str(time.ctime()) + '    Setting lights to off...'
				for i in lightList: 
					GPIO.output(i, GPIO.HIGH)
				print str(time.ctime()) + '    Lights off'
				lightstatus = 0
				db.log_relay(curdt,'Lights',0)
				db_dirty = 1
				
		# Heater Loop
		result = client.query(HEATERQRY)
		curtemp = list(result.get_points())

		if TARGETTEMP > curtemp[0]['mean']:
			if heaterstatus == 0:
				print str(time.ctime()) + '    Setting heater to on...'
				for i in heaterList:
					GPIO.output(i, GPIO.LOW)
				print str(time.ctime()) + '    Heater on, current temp is ' + str(curtemp[0]['mean'])
				heaterstatus = 1
				db.log_relay(curdt,'Heater',1)
				db_dirty = 1
		else:
			if heaterstatus == 1:
				print str(time.ctime()) + '    Setting heater to off...'
				for i in heaterList:
					GPIO.output(i, GPIO.HIGH)
				print str(time.ctime()) + '    Heater off, current temp is ' + str(curtemp[0]['mean'])
				heaterstatus = 0
				db.log_relay(curdt,'Heater',0)
				db_dirty = 1

		# Pump Loop
		if 	((curtime.hour >= STARTHOUR_HEATER) and (curtime.hour < STOPHOUR_HEATER)):
			if pumpstatus == 0:
				print str(time.ctime()) + '    Setting pump to on...'
				for i in pumpList:
					GPIO.output(i, GPIO.LOW)
				print str(time.ctime()) + '    Pump on'
				pumpstatus = 1
				db.log_relay(curdt,'Pump',1)
				db_dirty = 1
		else:
			if pumpstatus == 1:
				print str(time.ctime()) + '    Setting pump to off...'
				for i in pumpList:
					GPIO.output(i, GPIO.HIGH)
				print str(time.ctime()) + '    Pump off'
				pumpstatus = 0
				db.log_relay(curdt,'Pump',0)
				db_dirty = 1
						
		if db_dirty == 1:
			db.commit_DB()
			db_dirty = 0
			
		if curdt > nextphototime:
			if lightstatus == 1:
				# Archive the most recent image
				curfile = '/var/www/html/RS_Website/images/image_recent.jpg'
				arcfile = '/var/www/html/RS_Website/images/image_' + time.strftime("%Y%m%d%H%M%S") + '.jpg'
				try:
					os.rename(curfile, arcfile)
				except:
					print str(time.ctime()) + '    File rename failed'
				# Record an image of the setup
				camera.capture(curfile)
				print str(time.ctime()) + '    Image captured'
			nextphototime = curdt + timedelta(hours=PICTUREINTERVALHRS)
			
		time.sleep(30)
		
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
