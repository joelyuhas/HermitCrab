# HermitCrab
The automation of the temperate and humidity inside a hermit crab tank using a Raspberry Pi, a fan, heat lamp, and some sensors. Also attached the Pi camera and created time lapse videos. 

Originally created Aug 2022. Ran until November 2023.

## Objective
The objective of this project was to create an automated system that could help maintain a specific temperature and humidity range in my hermit crab tank, specifically between 70%-85% humidity and 72-85 degrees Fahrenheit. The device would be mounted to the top of the hermit crab cage and operate continuously.

A secondary objective was to setup the Pi Camera and get some time lapse shots of the hermit crabs moving.

## Setup
For this setup the following were used:
- Raspberry Pi
- Small computer fan
- DHT temp/humidity sensors
- Small breadboard
- Wires, resistors, transistors, and various breadboard equipment

## High Level Overview
This project is a good example of quick and clean code, without too much overhead and design being needed. It was designed to have a small footprint and be easy to adjust in the future.

A high level overview of how the project was broken up is shown in the following:
- temp_humid_capture.py
   - Read the temp and humidity ranges from the sensors, turn on/off the fan/heat lamp if the temp/humid was in a specific zone.
   - Save the recorded temp and humid values to an external storage device (USB).
- camera_capture.py
    - Take a photo of the inside of the hermit crab tank every X seconds.
    - Save the photos to the external storage.
- crab_library.py
    - Contains several helper functions used by the programs to help maintain the external storage.
    - Contains logic that can be used to delete old data on the storage device if it starts getting too full.
- images_to_video.py
    - Small program to stitch together and format time lapse photos into easy to watch video.
- startup.sh
    - Script used to start and launch all the proper programs on the Pi.
- Logs
    - Contains some of the debugging logs.
- backup-data
    - Backup logs and older code used with debugging.

More updates to come in future PDF!
