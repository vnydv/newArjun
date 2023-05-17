from typing import *
import subprocess
import logging as log
import cv2

from . import options

# replace print with logprint

class CamConnect():
    '''module to get connected camera device id'''

    LOG_DEBUG = True

    @staticmethod
    def get_cam_deviceID( videoResolution, videoFPS):
        '''checks for all connected camera devices and return the camera id
        vid0,vid1, etc. for the specified resolution
        
        -1 , if no deviceFound'''

        # fetch which ever camera is working
        for i in range(0,3):

            # first stop the device --if busy
            output = None
            pid = -1

            try:
                # get the pid of device if in use
                output = subprocess.check_output(["fuser",f"/dev/video{i}"])                
            except:
                # dvice not busy (free to use)
                if CamConnect.LOG_DEBUG:
                    print(f"No working cam at: /dev/video{i}, device free to use")
            
            # if busy stop device
            if output:
                output = output.decode('utf-8')
                try:
                    pid = int(output)
                    print(f"Found device PID {pid}, stopping...")
                    # kill the busy process
                    subprocess.call(["kill","-9",f"{pid}"])
                    print(f"Device PID {pid}, stopped.")
                except:
                    pass

            # start the device
            camera = cv2.VideoCapture(f"v4l2src device=/dev/video{i} ! video/x-raw, width={videoResolution[0]}, height={videoResolution[1]}, framerate={videoFPS}/1, format=(string)UYVY ! decodebin ! videoconvert ! appsink", cv2.CAP_GSTREAMER)
            while True:
                success, frame = camera.read()  # read the camera frame
                camera.release()
                if not success:                
                    break
                else:
                    if CamConnect.LOG_DEBUG:
                        print(f"Found working cam at: /dev/video{i}")
                    return i

        return -1

        
