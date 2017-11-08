#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  RS_Database.py
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

import MySQLdb
from datetime import datetime

servername 	= "localhost"
username 	= "root"
password 	= "RoquetteScience"
dbname 		= "RS_Logs"

def connect_to_db():
	global db 
	global cur
	
	db = MySQLdb.connect(
						servername, 
						username, 
						password,
						dbname
						)
	
	cur = db.cursor()
	
	return 0


def write_reading(logtime, sensorID, reading):
	
	# -1 is our error reading, so skip if it's that.
	if reading != -1:

		qrystr = 	"""INSERT INTO SensorReadings
							(LogTime, SensorID, Reading)
						VALUES
							("{logtime}", {sensorID}, {reading}) 
					""".format(
								logtime=logtime, 
								sensorID=sensorID, 
								reading='{0:.3f}'.format(reading)
							   )

		printstr =	"Writing {reading} for sensor {sensorID}".format(
								sensorID=sensorID, 
								reading='{0:.3f}'.format(reading)
							   )

		print printstr

		try:
			cur.execute(qrystr)
			
		except:
			print "DB execute error"

	return 0
	
def log_relay(curtime, relay, state):
	
	qrystr = """
				INSERT INTO RelayLogs
					(LogTime, RelayName, State)
				VALUES
					("{curtime}", "{relay}", {state})
			""".format	(
						curtime=curtime,
						relay=relay,
						state=state
						)
	
	try:
		cur.execute(qrystr)
		
	except:
		print "DB execute error"
		print qrystr
	
	return 0
	
def commit_DB():
	
	try:
		db.commit()
		print "Data committed   " + format(datetime.now(),'%d-%m-%y %H:%M')
	
	except:
		print "DB commit error"
	
	return 0
