from picamera import PiCamera
from datetime import datetime
from pathlib import Path
from time import sleep

import os
import time
import adafruit_dht
import board


SENSOR_1_BIAS_TEMP = 0.0
SENSOR_2_BIAS_TEMP = 0.0

# To directory on USB (will def change on another system, need to find better way
USB_DIRECTORY = Path("/media/pi/HERMITCRAB")
LOG_FILE_PARENT_LOCATION = USB_DIRECTORY / 'temp-humid-logs'
PICTURE_PARENT_LOCATION = USB_DIRECTORY / 'captures'


def initialize():
    # Temp and Humidity initialization
    LOG_FILE_PARENT_LOCATION.mkdir(exist_ok=True)

    # Creates or opens file if it exists
    log_file_name = LOG_FILE_PARENT_LOCATION / (str(datetime.today().strftime('%Y%m%d') + '.txt'))
    log_file = open(log_file_name, "a")

    # Picture Initalization
    PICTURE_PARENT_LOCATION.mkdir(exist_ok=True)

    # Ensure the sub directory with a folder as the date exists
    picture_directory = PICTURE_PARENT_LOCATION / str(datetime.today().strftime('%Y%m%d%H'))
    picture_directory.mkdir(exist_ok=True)

    return log_file, picture_directory


def check_space():
    space_available = int(os.system("df -k %s | tail -1 | awk '{print $4}'" % USB_DIRECTORY))
    print(space_available)
    if space_available < 1000:
        print ("IN TH EFILES")
        # Get list of folders and files for picture and logs repectivly
        # NEED TO MAKE MORE ROBUST AND ADD TRYS AND WHAT NOT TO NOT FAIL
        folder_list = []
        for folder in PICTURE_PARENT_LOCATION.iterdir():
            folder_list.append(int(str(folder)[-8:]))

        file_list = []
        for file in LOG_FILE_PARENT_LOCATION.iterdir():
            # Remove last 4 digits so just the name
            file_list.append(int(str(file)[-8:-4]))

        # Remove 2 days of info to clear up files
        for i in range(2):
            oldest_folder = min(folder_list)
            os.system(f"rm -rf {PICTURE_PARENT_LOCATION / (str(oldest_folder))}")

            oldest_file = min(file_list)
            os.system(f"rm -rf {LOG_FILE_PARENT_LOCATION / (str(oldest_file) + '.txt')}")


# Initialize the sensors and camera
dhtSensor1 = adafruit_dht.DHT22(board.D4)
dhtSensor2 = adafruit_dht.DHT22(board.D15)
camera = PiCamera()
camera.resolution = (1280, 720)
humidity1 = 0
humidity2 = 0
temp_c1 = 0
temp_c2 = 0
check_counter = 10


while True:
    # initialize and get locations needed
    log_file, picture_directory = initialize()
    # only check every 10 iterations to save computations
    # NOTE MAY CAUSE ERROR IF FULL DURING 10 ITERS, WILL NEED TO PLAY WITH TO GET VALUES RIGHT
    check_counter = check_counter + 1
    if check_counter > 10:
        #check_space()
        check_counter = 0

    # Temp and Humidity Capture
    # -------------------------
    try:
        humidity1 = dhtSensor1.humidity
        temp_c1 = dhtSensor1.temperature

        humidity2 = dhtSensor2.humidity
        temp_c2 = dhtSensor2.temperature

    except RuntimeError:
        print("RuntimeError, trying again...")
        continue

    log_file.write(str(datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))
                   + ", " + str(humidity1)
                   + ", " + str((temp_c1 * 9.0 / 5.0 + 32.0))
                   + ", " + str(humidity2)
                   + ", " + str((temp_c2 * 9.0 / 5.0 + 32.0))
               + '\n')

    # Picture capture
    # ---------------
    picture_number = 'image_' + str(datetime.today().strftime('%M%S') + '.jpg')
    camera.capture(str(picture_directory / picture_number))


    time.sleep(2)












#def main():
#    #counter = 0
#    camera = PiCamera()
#    if not PICTURE_LOCATION.is_dir():
#        PICTURE_LOCATION.mkdir()
#
#    while True:
#        #camera.start_preview()
#        # Save Picture
#
#
#
#main()

# if METRIC_UNITS:
#    streamer.log(SENSOR_LOCATION_NAME + " Temperature(C)", temp_c)
# else:
#    temp_f = format(temp_c * 9.0 / 5.0 + 32.0, ".2f")
#    streamer.log(SENSOR_LOCATION_NAME + " Temperature(F)", temp_f)
# humidity = format(humidity, ".2f")
# streamer.log(SENSOR_LOCATION_NAME + " Humidity(%)", humidity)
# streamer.flush()
# print("humidity1: " + str(humidity1))
# print("tempeture1: " + str((temp_c1 * 9.0 / 5.0 + 32.0)))

# print("humidity2: " + str(humidity2))
# print("tempeture2: " + str((temp_c2 * 9.0 / 5.0 + 32.0)))


