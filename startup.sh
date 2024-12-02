#!/bin/bash
# Sleep is used to ensure raspberry pi starts up in time
sleep 60
cd /home/pi/raspberrypi-items/hermit_crab
git pull

# kill the motion function
sudo killall motion

# Start the programs
python3 temp_humid_capture.py >> /home/pi/raspberrypi-items/hermit_crab/logs/output_temp_humid_capture.txt &
python camera_capture.py >> /home/pi/raspberrypi-items/hermit_crab/logs/output_camera_capture.txt &

# Wait for any log updates and then add them to git
sleep 30
git add /home/pi/raspberrypi-items/hermit_crab/logs/output_temp_humid_capture.txt
git add /home/pi/raspberrypi-items/hermit_crab/logs/output_camera_capture.txt
git commit -m "committing daily raspberry pi updates"
git push

