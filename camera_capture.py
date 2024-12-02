"""
Joel Yuhas
Raspberry-Pi/Hermit Crab project
July 13th, 2022

-------------------------------------------------------------------------------------
camera_capture.py
-------------------------------------------------------------------------------------

Initialize all of the needed values, print them to the log, then start the loop.

This loop will do the following:
    - Ensure provided USB drive is available
    - Ensure all required folders are present or created in directory
    - Take a picture every WAIT_INTERVAL_SECONDS_PICTURE seconds
    - Save that picture in the required directory
    - If the directory becomes too full, delete CAPTURE_HOURS_TO_CLEAR worth of folders

Directory layout/methodology:
- In the USB drive, all pictures are stored in the /captures/ directory, in a sub directory that is the date to the hour
- This sub-directory will have all photos taken within that hour, and then will increment to the next hour subdirectory
  after the hour has expired


"""
import time
import crab_library

from picamera import PiCamera
from datetime import datetime


def picture_capture(input_camera, save_directory, interval_time):
    """
    Method used to capture images using the PiCamera and the raspberry pi camera. These pictures are then stitched
    together into a video using the "images_to_video" program. Each folder contains an hours worth of pictures

    :param input_camera: PiCamera object that's been initialized pi camera
    :param save_directory: The directory to save the images
    :param interval_time: how much time to wait between camera captures
    :return: the name of the picture that was generated (for recording purposes)
    """
    # Picture capture
    picture_number = 'image_' + str(datetime.today().strftime('%M%S') + '.jpg')
    input_camera.capture(str(save_directory / picture_number))
    time.sleep(interval_time)
    return picture_number


def video_capture(input_camera, save_directory, record_time):
    """
    Method used to do video captures instead of picture captures

    NOTE: When experimenting with this method, there were jumps and spikes of missed recording times, may have been due
            to how it was set up, but primarily using the camera capture method, so may also be random instability.

    :param input_camera: PiCamera object that's been initialized for the pi camera
    :param save_directory: The directory to save the images
    :param record_time: Amount of time to record each clip
    """
    input_camera.start_recording(str(save_directory / ('video_' + str(datetime.today().strftime('%M%S') + '.h264'))))
    input_camera.wait_recording(record_time)
    input_camera.stop_recording()


# NOTE: check_counter is temporary so that different shutter speeds can be tested
def set_camera_mode(input_camera, camera_state: str):
    """
    Experimental method for setting the camera into either "day" or "night" mode.

    :param input_camera: Camera to change shudder speed for
    :param camera_state: Night or Day depending on which mode is desired.

    """
    # Get time in Hours and Minutes
    t = datetime.now().strftime("%H%M")
    if (int(t) > crab_library.TIME_NIGHT_THRESHOLD) or (int(t) < crab_library.TIME_DAY_THRESHOLD):
        # Only update is state is not in night state
        if camera_state != "night":
            input_camera.exposure_mode = 'night'
    else:
        # Set back to normal
        if camera_state != "day":
            input_camera.exposure_mode = 'auto'

    return input_camera


# Initialize PiCamera and bring it online
camera = PiCamera()
camera.resolution = (1280, 720)
check_counter_toggle = True
check_counter = 10
state = 0

# Basic print statement and debug messages.
crab_library.print_log(f"Log Severity meter set to: {crab_library.DEBUG_LOG_TOGGLE_THRESHOLD}", 0)
crab_library.print_log("Initialized PiCamera Variables!", 1)
crab_library.print_log(f"USB_DIRECTORY: {crab_library.USB_DIRECTORY}", 1)
crab_library.print_log(f"PICTURE_PARENT_LOCATION: {crab_library.CAMERA_PARENT_LOCATION}", 1)
crab_library.print_log(f"WAIT_INTERVAL_SECONDS_PICTURE: {crab_library.CAMERA_WAIT_INTERVAL_SECONDS}", 1)
crab_library.print_log(f"CAPTURE_HOURS_TO_CLEAR: {crab_library.CAMERA_HOURS_TO_CLEAR}", 1)
crab_library.print_log("----------------------------", 1)

# Perform the first initialization
picture_directory = crab_library.initialize(True, crab_library.CAMERA_TYPE_FLAG)

# Main loop for the camera capture methods
while True:
    # Every 10 iterations, check the file structure is still good and check the amount of space left. Only check every
    # 10 iterations to save computation time.
    check_counter = check_counter + 1
    if check_counter > 10:
        check_counter = 0
        try:
            picture_directory = crab_library.initialize(True, crab_library.CAMERA_TYPE_FLAG)
            check_counter_toggle = False
        except Exception as e:
            crab_library.print_log("INITIALIZE-ERROR: Issue while attempting to initialize the picture directories", 0)
            print(e)

            # Wait the required interval, then continue, need these in here as the main wait is in the picture capture dir
            time.sleep(crab_library.CAMERA_WAIT_INTERVAL_SECONDS)
            continue

    # Picture capture
    try:
        picture_number = picture_capture(camera, picture_directory, crab_library.CAMERA_WAIT_INTERVAL_SECONDS)
        crab_library.print_log(f"Picture Capture executed: {picture_number}", 2)
    except Exception as e:
        crab_library.print_log("CAPTURE-ERROR: Issue while attempting to capture picture", 0)

        # Wait the required interval, then continue, need these in here as the main wait is in the picture capture dir
        time.sleep(crab_library.CAMERA_WAIT_INTERVAL_SECONDS)
        print(e)
