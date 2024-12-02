"""
Joel Yuhas
Raspberry-Pi/Hermit Crab project
July 13th, 2022

images_to_video.py

Custom program used to turn the individual pictures gathered from the raspberry pi camera and turn into one video.

Done by providing the directory number to the program, or changing it in this file.

Designed so it already has the USB specific directory (which may need to change should it be used on a different
computer)

Also designed to create a 1280 x 720 (which the camera is set to) at 15 frames a seconds.
Currently, the raspberry pi is set to take a photo every 2 seconds so this is a good way to see a sped up version of
events.

Things that may need to change depending on setup
    - USB directory depending on the computer
    - size, if the size ever changes
    - The Directory naming convention, should that ever change
    - The 180-degree rotation, since the camera is currently mounted upside down

"""
from pathlib import Path
import cv2
import glob
import argparse

# Constants for the video dimensions
DEFAULT_VIDEO_HEIGHT = 1280
DEFAULT_VIDEO_WIDTH = 720
USB_DRIVE_NUMBER = 'F'


def arg_parser():
    """
    Get the folder name of the folder full of individual images that would like to be turned into a video

    Format for input example: "2022103109"

    input on command line

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("capture_folder_number",
                        help="The name in integer format of the folder in the captures directory to turn into video")
    return parser.parse_args()


def main(args):
    # Format directory and ensure it exist (auto fill usb directory and captures based on expected format
    usb_directory = f"{USB_DRIVE_NUMBER}:/captures/{args.capture_folder_number}/*"
    if not Path(usb_directory[:-1]).is_dir():
        print("Provided directory [%s] does not exist!", usb_directory)
        raise AssertionError

    # Attempt the to turn the directory of images into a video
    size = (DEFAULT_VIDEO_HEIGHT, DEFAULT_VIDEO_WIDTH)
    img_array = []
    try:
        print("Processing...")
        for filename in glob.glob(usb_directory):
            img = cv2.imread(filename)
            height, width, layers = img.shape
            size = (width, height)
            # rotate 180 (camera mounted upside down atm
            img = cv2.rotate(img, cv2.ROTATE_180)
            img_array.append(img)

    except Exception as e:
        print(f"File most likely corrupted {filename}")

    # Output the video
    out = cv2.VideoWriter(f"project_{args.capture_folder_number}.avi", cv2.VideoWriter_fourcc(*'DIVX'), 15, size)

    print(f"Video project_{args.capture_folder_number}.avi completed")
    print("Releasing...")

    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()

    print("Done!")


args = arg_parser()
main(args)



