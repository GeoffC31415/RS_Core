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

import RPi.GPIO as GPIO
import time
import RS_Database as db
import os
from influxdb import InfluxDBClient
from picamera import PiCamera
from datetime import datetime, timedelta

# Parameters
PICTUREINTERVALHRS = 1
HEATERQRY = 'select mean(DHT2_Temp) from dev where time > now() - 15m'
TARGETTEMP = 21
STARTHOUR_LIGHTS = 20
STOPHOUR_LIGHTS = 8
STARTHOUR_PUMP = 0
STOPHOUR_PUMP = 24
# Static lists with pin numbers
LIGHTLIST = [21]
HEATERLIST = [16]
PUMPLIST = [12]
# InfluxDB settings
HOST = "localhost"
PORT = 8086
USER = "root"
PASSWORD = "root"
DBNAME = "RS_Logs"

# Global status variables
# Remember to make sure they are all globally declared in functions which change them
lightstatus = 0
heaterstatus = 0
pumpstatus = 0
db_dirty = 0

# Create the InfluxDB object
client = InfluxDBClient(HOST, PORT, USER, PASSWORD, DBNAME)


def archivePhoto():
	curfile = '/var/www/html/RS_Website/images/image_recent.jpg'
	arcfile = '/var/www/html/RS_Website/images/image_' + time.strftime("%Y%m%d%H%M%S") + '.jpg'
	try:
		os.rename(curfile, arcfile)
	except:
		print str(time.ctime()) + '    File rename failed'
	return 0

def getLightStatus(curtime):
	if STARTHOUR_LIGHTS < STOPHOUR_LIGHTS:
		result = ((curtime.hour >= STARTHOUR_LIGHTS) and (curtime.hour < STOPHOUR_LIGHTS))
	else:
		result = ((curtime.hour >= STARTHOUR_LIGHTS) or (curtime.hour < STOPHOUR_LIGHTS))
	return result
	
def getPumpStatus(curtime):
	if STARTHOUR_LIGHTS < STOPHOUR_LIGHTS:
		result = ((curtime.hour >= STARTHOUR_PUMP) and (curtime.hour < STOPHOUR_PUMP))
	else:
		result = ((curtime.hour >= STARTHOUR_PUMP) or (curtime.hour < STOPHOUR_PUMP))
	return result

def getHeaterStatus(target):
	result = client.query(HEATERQRY)
	curtemp = list(result.get_points())
	return (target > curtemp[0]['mean'])
	
def setLights(status, curdt):
	global lightstatus, db_dirty
	
	if status != lightstatus:
		lightstatus = status
		db.log_relay(curdt,'Lights',status)
		db_dirty = 1
		
		if status:
			setPins(LIGHTLIST, GPIO.LOW)
			print str(time.ctime()) + '    Lights on'
		else:
			setPins(LIGHTLIST, GPIO.HIGH)
			print str(time.ctime()) + '    Lights off'
		
		#Pause for photo light
		time.sleep(5)
	return 0
	
def setHeaters(status, curdt):
	global heaterstatus, db_dirty
	
	if status != heaterstatus:
		heaterstatus = status
		db.log_relay(curdt,'Heater',status)
		db_dirty = 1
		
		if status:
			setPins(HEATERLIST, GPIO.LOW)
			print str(time.ctime()) + '    Heater on'
		else:
			setPins(HEATERLIST, GPIO.HIGH)
			print str(time.ctime()) + '    Heater off'
	return 0
	
def setPumps(status, curdt):
	global pumpstatus, db_dirty
	
	if status != pumpstatus:
		pumpstatus = status
		db.log_relay(curdt,'Pump',status)
		db_dirty = 1
		
		if status:
			setPins(PUMPLIST, GPIO.LOW)
			print str(time.ctime()) + '    Pump on'
		else:
			setPins(PUMPLIST, GPIO.HIGH)
			print str(time.ctime()) + '    Pump off'
	return 0

def setPins(pinlist, gpstatus):
	for i in pinlist:
		GPIO.output(i, gpstatus)
	return 0

def main(args):
 
	global db_dirty
 
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	db.connect_to_db()
	
	# loop through pins and set mode and state to 'high'
	# HIGH is off, LOW is ON
	print str(time.ctime()) + '    Initialising all outputs to off...'
	for i in LIGHTLIST:
		GPIO.setup(i, GPIO.OUT)
		GPIO.output(i, GPIO.HIGH)
	for i in HEATERLIST: 
		GPIO.setup(i, GPIO.OUT) 
		GPIO.output(i, GPIO.HIGH)
	for i in PUMPLIST: 
		GPIO.setup(i, GPIO.OUT) 
		GPIO.output(i, GPIO.HIGH)
			
	camera = PiCamera()
	
	nextphototime = datetime.now() - timedelta(hours=1+PICTUREINTERVALHRS)
	
	while 1:
		curtime = datetime.now().time()
		curdt = datetime.now()

		setLights(getLightStatus(curtime), curdt)
		setHeaters(getHeaterStatus(TARGETTEMP), curdt)
		setPumps(getPumpStatus(curtime), curdt)
		
		if db_dirty:
			db.commit_DB()
			db_dirty = 0
			
		if curdt > nextphototime:
			if lightstatus:
				archivePhoto()
				camera.capture(curfile)
				print str(time.ctime()) + '    Image captured'
				nextphototime = curdt + timedelta(hours=PICTUREINTERVALHRS)
			
		time.sleep(30)

	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
