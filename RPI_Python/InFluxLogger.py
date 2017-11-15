import time
import sys
import datetime
import PullReading
from influxdb import InfluxDBClient
 
# Set this variables, influxDB should be localhost on Pi
host = "localhost"
port = 8086
user = "admin"
password = "admin"
 
# The database we created
dbname = "RS_Logs"
# Sample period (s)
interval = 60
 
# Allow user to set session and runno via args otherwise auto-generate
if len(sys.argv) > 1:
    if (len(sys.argv) < 3):
        print "Must define session and runNo!!"
        sys.exit()
    else:
        session = sys.argv[1]
        runNo = sys.argv[2]
else:
    session = "dev"
    now = datetime.datetime.now()
    runNo = now.strftime("%Y%m%d%H%M")
 
print "Session: ", session
print "runNo: ", runNo
 
# Create the InfluxDB object
client = InfluxDBClient(host, port, user, password, dbname)
 
# Run until keyboard out
try:
    while True:
		# Gather readings
		print str(time.ctime()) + "    Gathering readings..."
		DHT1		= PullReading.GetDHTReading(1)
		DHT2 		= PullReading.GetDHTReading(2)
		DHT4 		= PullReading.GetDHTReading(4)
		pH			= PullReading.GetReading(9)
		waterTemp	= PullReading.GetReading(6)
		ec			= PullReading.GetReading(10)
		iso 		= time.ctime()
		print str(time.ctime()) + "    Readings retrieved"

		# Form JSON
		json_body = [
		{
		  "measurement": session,
			  "tags": {
				  "run": runNo,
				  },
			  "time": iso,
			  "fields": {
				  "DHT1_Temp" : DHT1[1], 
				  "DHT2_Temp" : DHT2[1], 
				  "DHT4_Temp" : DHT4[1], 
				  "Reservoir pH" : float(pH),
				  "Water_Temp" : float(waterTemp),
				  "Reservoir EC" : float(ec)
			  }
		  }
		]
        # Do humidities seperately as they can be over 100
        # We want blanks in those cases where it's out of range
		if DHT1[0] < 100: 
			json_body[0]['fields']["DHT1_Hum"] = DHT1[0]
		if DHT2[0] < 100:
			json_body[0]['fields']["DHT2_Hum"] = DHT2[0]
		if DHT4[0] < 100:
			json_body[0]['fields']["DHT4_Hum"] = DHT4[0]

		# Write JSON to InfluxDB
		client.write_points(json_body)
		print str(iso) + "    Sensor Data Written to InfluxDB"
		# Wait for next sample
		time.sleep(interval)
 
except KeyboardInterrupt:
    pass
