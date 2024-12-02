"""
Joel Yuhas
Raspberry-Pi/Hermit Crab project
July 13th, 2022

The Sensor class allows a standard and easy to modify interface for interacting with the sensors, such as the dht temp
and humidity sensor.

"""
import crab_library


class Sensor:
    def __init__(self, dht_sensor, sensor_number):
        self.dht_sensor = dht_sensor
        self.tempeture_f = 0
        self.tempeture_c = 0
        self.humidity = 0
        self.sensor_number = sensor_number
        self.status = "ONLINE"
        self.error_flag = 0

    def get_temp_and_humid(self):
        """
        Gets the temperature and humidity values from the selected dhtSensor.

        :return: returns the humidity and temp readings from the sensor
                 returns "err, err" so that the values can still be recorded in the logs for easier debugging
        """
        try:
            self.humidity = self.dht_sensor.humidity
            self.tempeture_c = self.dht_sensor.temperature
            # Fahrenheit conversion
            self.tempeture_f = (self.tempeture_c * 9.0 / 5.0 + 32.0)
            self.status = "ONLINE"
            self.error_flag = 0
            return self.humidity, self.tempeture_f
        except RuntimeError:
            crab_library.print_log(f": SENSOR-ERROR-{self.sensor_number}: Issue getting values from temp/humid sensor {self.sensor_number}", 0)
            # Pass these strings so its easier to debug later on
            # NOTE, may just change to have last value instead
            self.error_flag = self.error_flag + 1
            self.status = "ONLINE-ERROR"
            # If cant get value 10 times in a row, then sensor most likely offline
            if self.error_flag >= 50:
                self.status = "OFFLINE"
            return "err", "err"
        except:
            self.error_flag = self.error_flag + 1
            self.status = "OTHER-ERROR"
            # If cant get value 10 times in a row, then sensor most likely offline
            if self.error_flag >= 50:
                self.status = "OFFLINE"
            return "err", "err"

