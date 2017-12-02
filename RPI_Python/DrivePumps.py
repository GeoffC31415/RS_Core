#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  DrivePumps.py
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
#
# Pump 4 is rainwater reservoir

import RPi.GPIO as GPIO
import time

FLOWRATE = 0.75 # millilitres per second
PUMPLIST = [6,13,19,26] # pin numbers for pumps 1 through 4

MAXML = 1000 # Maximum number of ml to add

def InjectPump(pumpnum, volume):
		
	if not 1 <= pumpnum <= len(PUMPLIST):
		print "The pumpnum is out of range: " + str(pumpnum)
		return -1
		
	if not 1 <= volume <= MAXML:
		print "The ml volume is out of range: " + str(volume)
		print "The maximum is " + str(MAXML)
		return -1
		
	# Set up GPIO
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PUMPLIST[pumpnum-1], GPIO.OUT) 
	GPIO.output(PUMPLIST[pumpnum-1], GPIO.HIGH)
	
	# Power pump for the right amount of time
	print "Adding from pump {:d}, volume {:d} ml. Should take {:.2f} minutes".format(pumpnum, volume, volume/FLOWRATE/60.0)
	print "Starting... " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
	GPIO.output(PUMPLIST[pumpnum-1], GPIO.LOW)
	time.sleep(volume / FLOWRATE)
	GPIO.output(PUMPLIST[pumpnum-1], GPIO.HIGH)
	
	GPIO.cleanup()
	
	print "Done!       " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
	return 0

def main(args):
	
	if len(args) < 3:
		print "Must include volume of fluid as an argument"
		print "e.g. 'Python DrivePumps.py 1 100' would add 100ml from pump 1"
		return -1

	InjectPump(int(args[1]),int(args[2]))

	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
