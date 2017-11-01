#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  PullReading.py
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

import random
import Adafruit_DHT
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import time

# DHT setup
sensor_DHT11 = Adafruit_DHT.DHT11
pin_DHT11 = 4

# pH probe setup on SPI
SPI_PORT   = 0
SPI_DEVICE = 0
PH_CHANNEL = 0
PH_OFFSET = -0.85
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

def adc_to_ph(input):
	
	volts = input
	volts *= 3.3
	volts /= 1024.0 # ADC range 0-1023
	ph = 3.5 * volts + PH_OFFSET
	
	# print "Volts is " + str(volts) + " and pH is " + str(ph)
	
	return ph

def GetReading(sensorID):
	
	new_reading = -1
	loopcount = 0
	
	if sensorID == 1:
		humidity = 101
		# Occasionally we get a crazy reading like 160%
		# give it up to twenty goes to get one in range
		while ((humidity > 100) or (humidity < 0) or (loopcount > 20)):
			if loopcount > 0:
				time.sleep(0.05)
			humidity, temperature = Adafruit_DHT.read_retry(sensor_DHT11, pin_DHT11)
			if humidity is not None:
				new_reading = humidity
			loopcount += 1
		
	elif sensorID == 2:
		# Occasionally we get a reading about half of the true reading
		# Happens about 5% of the time
		# To mitigate, take three readings and pick the middle one
		
		temparray = []
		
		for x in range(0,3):
			humidity, temperature = Adafruit_DHT.read_retry(sensor_DHT11, pin_DHT11)
			if temperature is not None:
				new_reading = temperature
			temparray.append(new_reading)
		
		temparray.sort()
		new_reading = temparray[1]
		
	elif sensorID == 3:
		# Do ten readings in 2 seconds to average noise
		readings = []
		for x in range(0, 10):
			readings.append(mcp.read_adc(PH_CHANNEL))
			time.sleep(0.2)
		# Average readings		
		avg_val = sum(readings)/len(readings)
		new_reading = adc_to_ph(avg_val)
		
	else:
		new_reading = -1
		
	return new_reading
