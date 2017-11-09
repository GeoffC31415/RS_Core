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
import glob
import subprocess
import os

# DHT setup
sensor_DHT11 = Adafruit_DHT.DHT11
DHT_Pins = [4,17,0,22]

# One-wire setup
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# pH probe setup on SPI
SPI_PORT   = 0
SPI_DEVICE = 0
PH_CHANNEL = 0
EC_CHANNEL = 1
PH_OFFSET = 0
PH_CAL = 1 / 1.583
EC_OFFSET = 0
EC_TEMP_COMP = 1.0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

def adc_to_ph(input):
	
	volts = input
	volts *= 3.3
	volts /= 1024.0 # ADC range 0-1023
	ph = 3.5 * PH_CAL * volts + PH_OFFSET
	
	# print "Volts is " + str(volts) + " and pH is " + str(ph)
	
	return ph

def adc_to_ec(input):
	
	millivolts = input
	millivolts *= 3300.0
	millivolts /= 1024.0 # ADC range 0-1023
	
	# Adjust for temp
	millivolts = millivolts / EC_TEMP_COMP
	
	if millivolts < 448:
		ec = 6.84*millivolts - 64.32
	elif millivolts <1457:
		ec = 6.98*millivolts - 127
	else:
		ec = 5.3 * millivolts + 2278
	
	# print "Volts is " + str(millivolts/1000.0) + " and EC is " + str(ec)
	
	return ec
	
def read_watertemp_raw():
	catdata = subprocess.Popen(['cat',device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out,err = catdata.communicate()
	out_decode = out.decode('utf-8')
	lines = out_decode.split('\n')
	return lines

def read_watertemp():
	lines = read_watertemp_raw()
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_watertemp_raw()
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string) / 1000.0
	EC_TEMP_COMP = 1.0 + 0.0185*(temp_c-25.0)
	return temp_c

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
	elif sensorID == 6:
		new_reading = read_watertemp()
	elif sensorID == 10:
		readings = []
		for x in range(0, 10):
			readings.append(mcp.read_adc(EC_CHANNEL))
			time.sleep(0.2)
		# Average readings		
		avg_val = sum(readings)/len(readings)
		new_reading = adc_to_ec(avg_val)
	else:
		new_reading = -1
		
	return new_reading

def GetDHTReading(sensorID):
	
	hum_reading = -1
	temp_reading = -1
	loopcount = 0
		
	if sensorID <= len(DHT_Pins):
		# Get median of four
		humarray = []
		temparray = []
		
		readpin = DHT_Pins[sensorID-1]
		
		for x in range(0,4):
			humidity, temperature = Adafruit_DHT.read_retry(sensor_DHT11, readpin)
			if humidity is not None:
				hum_reading = humidity
			if temperature is not None:
				temp_reading = temperature
			humarray.append(hum_reading)
			temparray.append(temp_reading)
		
		humarray.sort()
		temparray.sort()
		hum_reading = humarray[1] #we want to skip the top two high readings
		temp_reading = temparray[2] #we want to skip the bottom two low readings
		
	readings = [hum_reading, temp_reading]	
		
	return readings
