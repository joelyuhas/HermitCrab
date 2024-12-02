"""
Joel Yuhas
Raspberry-Pi/Hermit Crab project
July 13th, 2022

-------------------------------------------------------------------------------------
temp_humid_capture.py
-------------------------------------------------------------------------------------

Initialize all of the needed values, print them to the log, then start the loop.

This loop will do the following:
    - call initialize() to ensure provided USB drive is available
    - Ensure all required folders are present or created in directory
    - Get the temp and humidity for the 2 sensors every WAIT_INTERVAL_SECONDS_TEMP_HUMID seconds
    - If the humid is above HUMIDITY_UPPER_LIMIT turn on the fan
    - If the humid is below HUMIDITY_LOWER_LIMIT turn off the fan
    - If the directory becomes too full, delete LOG_DAYS_TO_CLEAR worth of folders

Directory layout/methodology:
- In the USB drive, all pictures are stored in the /temp-humid-captures/ directory, and all information is stored in
  .txt files. Each txt file has all the information for that day, and then it increments to the next day after.

Also initialize all values so that they have something if needed

"""
import time
import adafruit_dht
import board
import crab_library
import RPi.GPIO as GPIO

from Sensor import Sensor
from datetime import datetime
from time import sleep


def fan_control(humid, servo_input, input_fan_status):
    """
    Controls the fan, which is used to blow outside air into the cage when there is too much humidity

    NOTE: Might be able to switch later, currently using servo so it can be controlled the fan %, but may want to switch
    to just full on/off in the future.

    :param humid: averaged humidity value
    :param servo_input: the servo GPIO pin that toggles the fan on/off
    :param input_fan_status: The current fan status
    :return: Returns the new, desired fan status
    """
    try:
        # Fan is off, check if needs to be turned on
        if input_fan_status == "off":
            if humid > crab_library.HUMIDITY_UPPER_LIMIT:
                crab_library.print_log("Setting fan HIGH", 1)
                servo_input.ChangeDutyCycle(100)
                sleep(10)
                return "on"

        # Fan is on, check if needs to be turned off
        else:
            if humid < crab_library.HUMIDITY_LOWER_LIMIT:
                crab_library.print_log("Setting fan LOW", 1)
                servo_input.ChangeDutyCycle(0)
                sleep(10)
                return "off"

    except Exception as e:
        crab_library.print_log("FAN-ERROR: Issue setting fan control", 0)
        print(e)

    return input_fan_status


def heat_lamp_control(temp, servo_input, input_heat_lamp_status):
    """
    Controls the heat lamps, which are used to generate heat if the cage is too cold

    NOTE: Might be able to switch later, currently using servo so it can be controlled the fan %, but may want to switch
    to just full on/off in the future.

    :param temp: averaged humidity value
    :param servo_input: the servo GPIO pin that toggles the fan on/off
    :param input_heat_lamp_status: The current fan status
    :return: Returns the new, desired fan status
    """
    try:
        # Heat Lamp is off, check if needs to be turned on
        if input_heat_lamp_status == "off":
            if temp < crab_library.TEMPERATURE_LOWER_LIMIT:
                crab_library.print_log("Setting Heat Lamp ON", 1)
                servo_input.ChangeDutyCycle(2)
                sleep(1)
                servo_input.ChangeDutyCycle(0)

                print("heat lamp ON setting cycle to 2")
                sleep(10)
                return "on"

        # Heat Lamp is on, check if needs to be turned off
        else:
            if temp > crab_library.TEMPERATURE_UPPER_LIMIT:
                crab_library.print_log("Setting Heat Lamp OFF", 1)
                servo_input.ChangeDutyCycle(12)
                sleep(1)
                servo_input.ChangeDutyCycle(0)

                print("heat lamp OFF setting cycle to 10")
                sleep(10)
                return "off"

    except Exception as e:
        crab_library.print_log("FAN-ERROR: Issue setting fan control", 0)
        print(e)

    return input_heat_lamp_status


def led_status_for_temp_and_humid_values(temp_average, humid_average):
    """
    Checks the temperature and humidity values. If the average of them is in the desired range for hermit crabs, then
    light LED on. If either value is too high, flash the LED fast. If either value is too low, LED off

    NOTE will probably want to input these as list later, but have them manually put out for easier calculations and
    packaging

    ALSO NOTE, potentially will want to have it so that instead of taking in the average, it takes in each point of
    data, and if one is super far off it can outlier it, or if one is very high it can produce a warning or something
    :param temp_average: takes in the average value for temperature
    :param humid_average: takes in the average value for humidity
    :return:
    """

    # Note, will want to potentially genericise this a bit more, have it be able to take in list and have dynamic number
    # But as of now with only 2 sensors not super big deal.

    # Also of note, potentially in the future will want to do a rolling average, but will hold off on that for now
    try:
        # NOTE, can probably make this section into different functions
        temp_flag = 0  # False
        if temp_average >= crab_library.IDEAL_TEMP_LOWER_LIMIT:
            if temp_average <= crab_library.IDEAL_TEMP_UPPER_LIMIT:
                # Temperature is in the good range
                temp_flag = 1  # True
            else:
                crab_library.print_log(f"NOTICE: Average temperature too HIGH! {temp_average}", 1)
                # flashing mechanism
                GPIO.output(27, 1)  # set GPIO27 to 1/GPIO.HIGH/True
                sleep(1)
        else:
            crab_library.print_log(f"NOTICE: Average temperature too LOW! {temp_average}", 1)

        humid_flag = 0  # False
        if humid_average >= crab_library.IDEAL_HUMID_LOWER_LIMIT:
            if humid_average <= crab_library.IDEAL_HUMID_UPPER_LIMIT:
                humid_flag = 1  # True
            else:
                crab_library.print_log(f"NOTICE: Average humidity too HIGH! {humid_average}", 1)
                # flashing mechanism
                GPIO.output(22, 1)  # set GPIO22 to 1/GPIO.HIGH/True
                sleep(1)
        else:
            crab_library.print_log(f"NOTICE: Average humidity too LOW! {humid_average}", 1)

        # if both in flags true, then set light green
        # other
        GPIO.output(27, temp_flag)   # set GPIO27 to 1/GPIO.HIGH/True
        GPIO.output(22, humid_flag)  # set GPIO22 to 1/GPIO.HIGH/True

    except Exception as e:
        crab_library.print_log("LED-SET-ERROR: Issue setting LEDs control", 0)
        print(e)


# Initialize GPIO
GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
GPIO.setup(17, GPIO.OUT)  # Humidity control fan
GPIO.setup(11, GPIO.OUT)  # Heat Lamp control
GPIO.setup(27, GPIO.OUT)  # Temp LED output
GPIO.setup(22, GPIO.OUT)  # Humid LED output
servo_fan = GPIO.PWM(17, 50)  # humidity control PWM
servo_fan.start(0)
servo_heat_lamp = GPIO.PWM(11, 50)  # Servo Heat Lamp PWM
servo_heat_lamp.start(0)


# Initialize the sensors and camera
dhtSensor1 = adafruit_dht.DHT22(board.D4)
dhtSensor2 = adafruit_dht.DHT22(board.D15)
sensor_1 = Sensor(dhtSensor1, 1)
sensor_2 = Sensor(dhtSensor2, 2)

sensor_list = [sensor_1,sensor_2]


check_counter = 10
check_counter_toggle = False
fan_status = "off"
heat_lamp_status = "off"

# Print out of initialization
crab_library.print_log(f"Log Severity meter set to: {crab_library.DEBUG_LOG_TOGGLE_THRESHOLD}", 0)
crab_library.print_log("Initialized temp and humidity Variables!", 1)
crab_library.print_log(f"USB_DIRECTORY: {crab_library.USB_DIRECTORY}", 1)
crab_library.print_log(f"LOG_FILE_PARENT_LOCATION: {crab_library.TEMP_HUMID_PARENT_LOCATION}", 1)
crab_library.print_log(f"WAIT_INTERVAL_SECONDS_TEMP_HUMID: {crab_library.TEMP_HUMID_WAIT_INTERVAL_SECONDS}", 1)
crab_library.print_log(f"LOG_DAYS_TO_CLEAR: {crab_library.TEMP_HUMID_LOG_DAYS_TO_CLEAR}", 1)
crab_library.print_log("----------------------------", 1)


# First initialization
log_file = crab_library.initialize(check_counter_toggle, crab_library.TEMP_HUMID_TYPE_FLAG)

# Main loop
while True:
    # Wait the required interval, then continue
    time.sleep(crab_library.TEMP_HUMID_WAIT_INTERVAL_SECONDS)

    # Only check the directory structure and free space every 10 iterations to save computations
    check_counter = check_counter + 1
    if check_counter > 10:
        check_counter = 0
        try:
            log_file = crab_library.initialize(check_counter_toggle, crab_library.TEMP_HUMID_TYPE_FLAG)
            check_counter_toggle = False
        except Exception as e:
            crab_library.print_log("INITIALIZATION-ERROR: Issue while attempting to initialize for temp-humid", 0)
            continue

    avg_humid = 0
    avg_temp = 0
    avg_counter = 0

    # Temp and Humidity Capture, if signal is valid, add to final average
    for sensor in sensor_list:
        sensor.get_temp_and_humid()
        if sensor.status == "ONLINE":
            avg_humid = avg_humid + sensor.humidity
            avg_temp = avg_temp + sensor.tempeture_f
            avg_counter = avg_counter + 1

    # Calculate averages
    if avg_counter != 0:
        avg_humid = avg_humid/avg_counter
        avg_temp = avg_temp/avg_counter

        # Fan Control
        fan_status = fan_control(avg_humid, servo_fan, fan_status)

        # Temperature and heat_lamp control NOTE: Currently in prototype/offline
        # print("before heat lamp statues: [%s]", heat_lamp_status)
        # Commenting out for the time being until more debugging methods occur
        # heat_lamp_status = heat_lamp_control(avg_temp, servo_heat_lamp, heat_lamp_status)

        # Check temp ranges
        # print("before led status")
        led_status_for_temp_and_humid_values(avg_temp, avg_humid)

        # Printing and Log objects
        try:
            # Just doing manual print-outs for now, can make this dynamic in the future
            crab_library.print_log(
                f"writing the following: {sensor_1.humidity} {sensor_1.tempeture_f} {sensor_2.humidity} {sensor_2.tempeture_f} {fan_status}",
                2)
            log_file.write(str(datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))
                           + ", " + str(sensor_1.humidity)
                           + ", " + str(sensor_1.tempeture_f)
                           + ", " + str(sensor_2.humidity)
                           + ", " + str(sensor_2.tempeture_f)
                           + ", " + fan_status
                           + ", " + heat_lamp_status
                           + '\n')
        except Exception as e:
            crab_library.print_log("DATA-ERROR: Issue writing to log file", 0)
            print(e)

