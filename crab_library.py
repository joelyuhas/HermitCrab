"""
Joel Yuhas
Raspberry-Pi/Hermit Crab project
July 13th, 2022

Contains all constants and cross used definitions for running and managing the programs on the raspberry pi.

"""
import os
import subprocess

from datetime import datetime
from pathlib import Path


"""
Toggle the level of severity of debug logs that are desired inclusive:
    - 0 : all errors
    - 1 : initialization, alerts, and notices
    - 2 : conformation and success statements
    
    A value of 1 will print 0 and 1 severities, but not 2
"""
DEBUG_LOG_TOGGLE_THRESHOLD = 1

"""
Threshold for how much available space left on the USB_DIRECTORY before old files on the USB_DIRECTORY are removed.
Below this value, old files are triggered to get removed 
"""
SPACE_THRESHOLD_KB = 10000

"""
Constants used to determine the running interval/frame rate of each program in seconds
"""
TEMP_HUMID_WAIT_INTERVAL_SECONDS = 2
CAMERA_WAIT_INTERVAL_SECONDS = 2

"""
These values provide the upper and lower limit for the fan operation to follow. When the % humidity is above the 
UPPER_LIMIT, the fan will turn on, when the % humidity is below the LOWER_LIMIT, the fan will turn off
"""
HUMIDITY_UPPER_LIMIT = 85
HUMIDITY_LOWER_LIMIT = 75

"""
These values provide the upper and lower limit for the heat lamp to follow. When the % temperature is above the 
UPPER_LIMIT, the heat lamp turns off, when the temp is below the LOWER_LIMIT, the heat lamp will turn on
"""
TEMPERATURE_UPPER_LIMIT = 79
TEMPERATURE_LOWER_LIMIT = 72

"""
These are the desired values. These can be different from the upper and lower limits, as those are the values the fan 
will turn on/off at, while these are the independent "desired values" for ideal hermit crab conditions

Also this way these values can be tweaked independently
"""
IDEAL_TEMP_UPPER_LIMIT = 85
IDEAL_TEMP_LOWER_LIMIT = 69
IDEAL_HUMID_UPPER_LIMIT = 85
IDEAL_HUMID_LOWER_LIMIT = 75


"""
Time of day thresholds for camera capture in HHMM
"""

TIME_NIGHT_THRESHOLD = 2000     # 8pm
TIME_DAY_THRESHOLD = 700        # 7am

"""
The values which are used to determine how much data to delete when the USB is too full

CAPTURE_HOURS_TO_CLEAR: Pictures are stored in folders for each hour of recording. This value selects how many folders
                        to delete when directory too full
LOG_DAYS_TO_CLEAR: Temp and Humidty are stored in text files that increment each day. This value corresponds to how many
                   text files to delete.
"""
TEMP_HUMID_LOG_DAYS_TO_CLEAR = 1
CAMERA_HOURS_TO_CLEAR = 2

"""
These values are flags for the initialize and check space functions. These are provided to the methods, so if needed,
the camera or temp/humidity programs can run independently, and be initalized on their own.
"""
TEMP_HUMID_TYPE_FLAG = "temp-humid"
CAMERA_TYPE_FLAG = "camera"

"""
The directories to the USB, as well as the sub directories for each needed folder for data storage.

Currently using:
- temperature and humidity
- picture captures
"""""
USB_DIRECTORY = Path("/media/pi/HERMITCRAB")
TEMP_HUMID_PARENT_LOCATION = USB_DIRECTORY / 'temp-humid-logs'
CAMERA_PARENT_LOCATION = USB_DIRECTORY / 'captures'


def print_log(message, value):
    """
    Helper function to print out debug messages to the console

    :param message: The message that would like to be printed out
    value: the value is the severity of debug log:
        0 = error message
        1 = init messages
        2 = success/debug message
    :param value: The debug value/flag setting.

    """
    # If DEBUG_LOG_TOGGLE is on, print all debug messages, otherwise only print debug mesages with values 0 and 1
    if value <= DEBUG_LOG_TOGGLE_THRESHOLD:
        print(str(datetime.today().strftime('%Y%m%d%H%M%S') + ": " + str(message)))


def initialize(check_counter_toggle, type):
    """
    Initializes all required directory variables, ensures that the directories exists, and calls the check_space
    function

    This module was designed so that both the camera capture and temp and humid capture could be run independently if
    needed, which is why the type flag is used. This way, the initialize function can be called from both python
    scripts and initialized only as needed, rather than doing a blanket initialization

    :param check_counter_toggle: the flag used to determine whether to check the space left or not
    :param type: The type of initialization, either TYPE_TMP_HUMID_FLAG for temp and humidity or TYPE_CAMERA_FLAG for
                 camera
    :return: either the:
                - log_file PATH if temp/humid
                - picture_directory if picture capture
                - False if issue
    """
    # Ensure USB directory exists
    if not USB_DIRECTORY.is_dir():
        print_log(f"USB-ERROR: provided USB directory does not exists: {USB_DIRECTORY}", 0)
        raise AssertionError

    # Temp and Humidity initialization
    TEMP_HUMID_PARENT_LOCATION.mkdir(exist_ok=True)

    # Check space
    if check_counter_toggle:
        check_space(type)

    # Creates or opens file if it exists
    if type == TEMP_HUMID_TYPE_FLAG:
        log_file_name = TEMP_HUMID_PARENT_LOCATION / (str(datetime.today().strftime('%Y%m%d') + '.txt'))
        log_file = open(log_file_name, "a")
        print_log("Temp-Humid Directory initialization success", 2)
        return log_file

    elif type == CAMERA_TYPE_FLAG:
        # Ensure the sub-directory with a folder as the date exists
        picture_directory = CAMERA_PARENT_LOCATION / str(datetime.today().strftime('%Y%m%d%H'))
        picture_directory.mkdir(exist_ok=True)
        print_log("Picture Directory initialization success", 2)
        return picture_directory
    else:
        print_log("INITIALIZE-ERROR: Issue selecting initialization type between CAMERA and TMP-HUMID flag", 0)
        return False


def check_space(type):
    """
    Checks how much space is left on the USB_DIRECTORY. If below the space available is less than SPACE_THRESHOLD_KB
    then start removing the files. Depending on the type, only remove the files created by the process (i.e., if type
    is temp/humid, only delete log files. If type Picture, delete folder of pictures

    LOG_DAYS_TO_CLEAR/CAPTURE_HOURS_TO_CLEAR is used to determine how much to delete. Deleting folders of images or
    .txt files depending on the file type

    NOTE:
    - For PICTURES: Deletes FOLDERS, each folder with an hour worth of data. Oldest folders deleted. Value based on
                    CAPTURE_HOURS_TO_CLEAR
    - For TEMP/HUMID: Deletes TEXT FILES. Each text file holds a days worth of temp/humidity data. Value based on
                    LOG_DAYS_TO_CLEA

    :param type: Determines what data to delete, either temp/humid or pictures
    """
    space_available = int(subprocess.check_output("df -k %s | tail -1 | awk '{print $4}'" % USB_DIRECTORY, shell=True))
    print_log(f"Checking Space: available: {str(space_available)}", 2)

    # only clean if less than SPACE_THRESHOLD_KB left in the provided USB_DIRECTORY
    if space_available < SPACE_THRESHOLD_KB:
        # Clean the camera files
        if type == CAMERA_TYPE_FLAG:
            folder_list = []
            for folder in CAMERA_PARENT_LOCATION.iterdir():
                folder_list.append(int(str(folder)[-10:]))

            # Remove 2 hours of info to clear up files
            try:
                for i in range(CAMERA_HOURS_TO_CLEAR):
                    oldest_folder = min(folder_list)
                    print_log(f"CLEANING: Removing the following: {oldest_folder}", 1)
                    os.system(f"rm -rf {CAMERA_PARENT_LOCATION / (str(oldest_folder))}")

            except Exception:
                print_log("DELETION-ERROR: Issue while attempting to free up space ", 0)

        # Clean the temp and humidity files
        elif type == TEMP_HUMID_TYPE_FLAG:
            file_list = []
            for file in TEMP_HUMID_PARENT_LOCATION.iterdir():
                file_list.append(int(str(file)[-10:-4]))

            # Remove 1 day of info to clear up files
            try:
                for i in range(TEMP_HUMID_LOG_DAYS_TO_CLEAR):
                    oldest_file = min(file_list)
                    print_log(f"CLEANING: Removing the following: {oldest_file}", 1)
                    os.system(f"rm -rf {TEMP_HUMID_PARENT_LOCATION / (str(oldest_file) + '.txt')}")

            except Exception:
                print_log("DELETION-ERROR: Issue while attempting to free up space ", 0)