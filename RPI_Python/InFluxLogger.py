import time
import sys
import datetime
import PullReading
from influxdb import InfluxDBClient
import RPi.GPIO as GPIO
 
# Set this variables, influxDB should be localhost on Pi
host = "localhost"
port = 8086
user = "root"
password = "root"
 
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
        print "Gathering readings... " + str(time.ctime())
        DHT1	= PullReading.GetDHTReading(1)
        DHT2 	= PullReading.GetDHTReading(2)
        DHT4 	= PullReading.GetDHTReading(4)
        pH		= PullReading.GetReading(9)
        iso 	= time.ctime()
        print "Readings retrieved    " + str(time.ctime())

		# Form JSON
        json_body = [
        {
          "measurement": session,
              "tags": {
                  "run": runNo,
                  },
              "time": iso,
              "fields": {
                  "DHT1_Hum" : DHT1[0], 
                  "DHT1_Temp" : DHT1[1], 
                  "DHT2_Hum" : DHT2[0], 
                  "DHT2_Temp" : DHT2[1], 
                  "DHT4_Hum" : DHT4[0], 
                  "DHT4_Temp" : DHT4[1], 
                  "Reservoir pH" : pH
              }
          }
        ]
 
        # Write JSON to InfluxDB
        client.write_points(json_body)
        print "Data Written: " + str(iso)
        # Wait for next sample
        time.sleep(interval)
 
except KeyboardInterrupt:
    pass
