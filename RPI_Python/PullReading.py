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

# DHT setup
sensor_DHT11 = Adafruit_DHT.DHT11
pin_DHT11 = 4

# pH probe setup on SPI
SPI_PORT   = 0
SPI_DEVICE = 0
PH_CHANNEL = 0
PH_OFFSET = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

def adc_to_ph(input):
	
	volts = input * (5 / 1024) # Assumes the probe is running off five volts
	ph = 3.5 * volts + PH_OFFSET
	
	return ph

def GetReading(sensorID):
	
	if sensorID == 1:
		humidity, temperature = Adafruit_DHT.read_retry(sensor_DHT11, pin_DHT11)
		if humidity is not None:
			new_reading = humidity
	elif sensorID == 2:
		humidity, temperature = Adafruit_DHT.read_retry(sensor_DHT11, pin_DHT11)
		if temperature is not None:
			new_reading = temperature
	elif sensorID == 3:
		new_reading = adc_to_ph(mcp.read_adc(PH_CHANNEL))
	
	if new_reading is not None:
		return new_reading
	else:
		return -1
