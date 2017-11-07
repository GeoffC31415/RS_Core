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
DHT_Pins = [4,17,27,22]

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
	
	if sensorID == 9:
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

def GetDHTReading(sensorID):
	
	hum_reading = -1
	temp_reading = -1
	loopcount = 0
		
	if sensorID <= len(DHT_Pins):
		# Get median of five
		humarray = []
		temparray = []
		
		readpin = DHT_Pins[sensorID-1]
		
		for x in range(0,5):
			humidity, temperature = Adafruit_DHT.read_retry(sensor_DHT11, readpin)
			if humidity is not None:
				hum_reading = humidity
			if temperature is not None:
				temp_reading = temperature
			humarray.append(hum_reading)
			temparray.append(temp_reading)
			time.sleep(1)
		
		humarray.sort()
		temparray.sort()
		hum_reading = humarray[2]
		temp_reading = temparray[2]
		
	readings = [hum_reading, temp_reading]	
		
	return readings
