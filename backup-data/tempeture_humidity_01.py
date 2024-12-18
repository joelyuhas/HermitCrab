import adafruit_dht
#from ISStreamer.Streamer import Streamer
import time
import board

# --------- User Settings ---------
SENSOR_LOCATION_NAME = "Office"
BUCKET_NAME = ":partly_sunny: Room Temperatures"
BUCKET_KEY = "dht22sensor"
ACCESS_KEY = "ENTER ACCESS KEY HERE"
MINUTES_BETWEEN_READS = 10
METRIC_UNITS = False
# ---------------------------------
SENSOR_1_BIAS_TEMP = 0.0
SENSOR_2_BIAS_TEMP = 0.0


dhtSensor1 = adafruit_dht.DHT22(board.D4)
dhtSensor2 = adafruit_dht.DHT22(board.D15)
#streamer = Streamer(bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)

while True:
    try:
        humidity1 = dhtSensor1.humidity
        temp_c1 = dhtSensor1.temperature
        
        humidity2 = dhtSensor2.humidity
        temp_c2 = dhtSensor2.temperature
        
    except RuntimeError:
        print("RuntimeError, trying again...")
        continue

    #if METRIC_UNITS:
    #    streamer.log(SENSOR_LOCATION_NAME + " Temperature(C)", temp_c)
    #else:
    #    temp_f = format(temp_c * 9.0 / 5.0 + 32.0, ".2f")
    #    streamer.log(SENSOR_LOCATION_NAME + " Temperature(F)", temp_f)
    #humidity = format(humidity, ".2f")
    #streamer.log(SENSOR_LOCATION_NAME + " Humidity(%)", humidity)
    #streamer.flush()
    print("humidity1: " + str(humidity1))
    print("tempeture1: " + str((temp_c1 * 9.0 / 5.0 + 32.0)))
    
    print("humidity2: " + str(humidity2))
    print("tempeture2: " + str((temp_c2 * 9.0 / 5.0 + 32.0)))
    time.sleep(5)