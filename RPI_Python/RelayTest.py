#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  RelayTest.py
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
	import time

	GPIO.setmode(GPIO.BCM)

	# init list with pin numbers

	pinList = [21, 20, 16, 12]

	# loop through pins and set mode and state to 'high'

	for i in pinList: 
		GPIO.setup(i, GPIO.OUT) 
		GPIO.output(i, GPIO.HIGH)

	# time to sleep between operations in the main loop

	SleepTimeL = 2

	# main loop

	try:
		GPIO.output(pinList[0], GPIO.LOW)
		print "ONE"
		time.sleep(SleepTimeL); 
		GPIO.output(pinList[1], GPIO.LOW)
		print "TWO"
		time.sleep(SleepTimeL);  
		GPIO.output(pinList[2], GPIO.LOW)
		print "THREE"
		time.sleep(SleepTimeL);
		GPIO.output(pinList[3], GPIO.LOW)
		print "FOUR"
		time.sleep(SleepTimeL);
		GPIO.cleanup()
		print "Good bye!"

	# End program cleanly with keyboard
	except KeyboardInterrupt:
		print "  Quit"

		# Reset GPIO settings
		GPIO.cleanup()
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
