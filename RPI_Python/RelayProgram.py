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
import os
from influxdb import InfluxDBClient
from picamera import PiCamera
from datetime import datetime, timedelta

# Parameters
PICTUREINTERVALHRS = 1
TEMPQRY = 'select mean(DHT2_Temp) from dev where time > now() - 10m'
TARGETTEMP = 21
STARTHOUR_LIGHTS = 20
STOPHOUR_LIGHTS = 8
STARTHOUR_PUMP = 0
STOPHOUR_PUMP = 24
# Static lists with pin numbers
LIGHTLIST = [21]
HEATERLIST = [16]
FANLIST = [20]
PUMPLIST = [12]
# InfluxDB settings
HOST = "localhost"
PORT = 8086
USER = "admin"
PASSWORD = "admin"
DBNAME = "RS_Logs"

# Global status variables
# Remember to make sure they are all globally declared in functions which change them
lightstatus = 0
heaterstatus = 0
pumpstatus = 0
fanstatus = 0
# Create the InfluxDB object
client = InfluxDBClient(HOST, PORT, USER, PASSWORD, DBNAME)


def archivePhoto(curfile,arcfile):
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
	result = client.query(TEMPQRY)
	curtemp = list(result.get_points())
	return (target > curtemp[0]['mean'])

def getFanStatus(target):
	result = client.query(TEMPQRY)
	curtemp = list(result.get_points())
	return (target < curtemp[0]['mean'])
			
def setLights(status, curdt):
	global lightstatus, db_dirty
	
	if status != lightstatus:
		lightstatus = status
		if status:
			setPins(LIGHTLIST, GPIO.LOW)
			print str(time.ctime()) + '        LIGHTS ON'
		else:
			setPins(LIGHTLIST, GPIO.HIGH)
			print str(time.ctime()) + '        LIGHTS OFF'
		#Pause for photo light
		time.sleep(5)
		
	influxlog(curdt,'Relay_Lights',status)
	return 0
	
def setHeaters(status, curdt):
	global heaterstatus, db_dirty
	
	if status != heaterstatus:
		heaterstatus = status
		
		if status:
			setPins(HEATERLIST, GPIO.LOW)
			print str(time.ctime()) + '        HEATER ON'
		else:
			setPins(HEATERLIST, GPIO.HIGH)
			print str(time.ctime()) + '        HEATER OFF'
	influxlog(curdt,'Relay_Heater',status)
	return 0
	
def setPumps(status, curdt):
	global pumpstatus, db_dirty
	
	if status != pumpstatus:
		pumpstatus = status
		
		if status:
			setPins(PUMPLIST, GPIO.LOW)
			print str(time.ctime()) + '        PUMP ON'
		else:
			setPins(PUMPLIST, GPIO.HIGH)
			print str(time.ctime()) + '        PUMP OFF'
	influxlog(curdt,'Relay_Pump',status)
	return 0
	
def setFans(status, curdt):
	global fanstatus, db_dirty
	
	if status != fanstatus:
		fanstatus = status
		
		if status:
			setPins(FANLIST, GPIO.LOW)
			print str(time.ctime()) + '        FAN ON'
		else:
			setPins(FANLIST, GPIO.HIGH)
			print str(time.ctime()) + '        FAN OFF'
	influxlog(curdt,'Relay_Fan',status)
	return 0

def setPins(pinlist, gpstatus):
	for i in pinlist:
		GPIO.output(i, gpstatus)
	return 0

def influxlog(curdt, measurementstr, state):
	#Add it into InfluxDB
	json_body = [
		{
		  "measurement": "dev",
			  "time": curdt,
			  "fields": {
				  measurementstr : bool(state)
			  }
		  }
		]
	
	# Write JSON to InfluxDB
	client.write_points(json_body)
	print str(time.ctime()) + '    Relay Data Written to InfluxDB'
	return 0

def main(args):
 
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	curdt = datetime.now()
	
	# loop through pins and set mode and state to 'high'
	# HIGH is off, LOW is ON
	print str(time.ctime()) + '    Initialising all outputs to off...'
	for i in LIGHTLIST:
		GPIO.setup(i, GPIO.OUT)
		GPIO.output(i, GPIO.HIGH)
	influxlog(curdt,'Relay_Lights',False)
	for i in HEATERLIST: 
		GPIO.setup(i, GPIO.OUT) 
		GPIO.output(i, GPIO.HIGH)
	influxlog(curdt,'Relay_Heater',False)
	for i in PUMPLIST: 
		GPIO.setup(i, GPIO.OUT) 
		GPIO.output(i, GPIO.HIGH)
	influxlog(curdt,'Relay_Pump',False)	
	for i in FANLIST: 
		GPIO.setup(i, GPIO.OUT) 
		GPIO.output(i, GPIO.HIGH)
	influxlog(curdt,'Relay_Fan',False)
		
	camera = PiCamera()
	
	nextphototime = datetime.now() - timedelta(hours=1+PICTUREINTERVALHRS)
	
	while 1:
		curtime = datetime.now().time()
		curdt = datetime.now()

		fans_setting = getFanStatus(TARGETTEMP)
		
		setLights(getLightStatus(curtime), curdt)
		setHeaters(getHeaterStatus(TARGETTEMP), curdt)
		setPumps(getPumpStatus(curtime), curdt)
		setFans(fans_setting, curdt)
			
		if curdt > nextphototime:
			if lightstatus:
				curfile = '/var/www/html/RS_Website/images/image_recent.jpg'
				arcfile = '/var/www/html/RS_Website/images/image_' + time.strftime("%Y%m%d%H%M%S") + '.jpg'
				archivePhoto(curfile,arcfile)
				camera.capture(curfile)
				print str(time.ctime()) + '        IMAGE CAPTURED'
				nextphototime = curdt + timedelta(hours=PICTUREINTERVALHRS)
		
		time.sleep(30)
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
