import cv2


class Options:

    #use image crop
    CROP_IMAGES = True

    # merge nearby boxes
    MERGE_NEARBY = False

    # save CSV
    SAVE_CSV = False

    # use this to display bounding boxes
    FRAME_DEBUG = False

    # use this to show on console when files are created
    LOG_DEBUG = True

    #us RGB plane normalization ?
    USE_RGB_NORM = False

    # for Fixedfocus
    VID_RESO, FPS = (1920,1080), 60
    #VID_RESO, FPS = (1920,1200), 55
    #VID_RESO, FPS = (1280,720), 120
    #VID_RESO, FPS = (1280,720), 60

    # for AutoFocus
    #VID_RESO, FPS = (640, 480), 60    
    #VID_RESO, FPS = (4208,3120), 9
    #VID_RESO, FPS = (4208,3120), 4.5
    #VID_RESO, FPS = (3840,2160), 15
    #VID_RESO, FPS = (3840,2160), 7.5
    #VID_RESO, FPS = (4096,2160), 7.5
    #VID_RESO, FPS = (1920,1080), 60
    #VID_RESO, FPS = (1920,1080), 30
    #VID_RESO, FPS = (1280,720), 60
    #VID_RESO, FPS = (1280,720), 30
    #VID_RESO, FPS = (640, 480), 120


    # conf file
    conf_file_path = "/etc/entomologist/ento.conf"

    DEVICE_SERIAL_ID = ""
    BUFFER_IMAGES_PATH = ""
    BUFFER_COUNT_PATH = ""

    # video capture : from device
    #cap = None
    #cap = cv2.VideoCapture(f"v4l2src device/dev/video2 ! video/x-raw, width={VID_RESO[0]}, height={VID_RESO[1]}, framerate={FPS}/1, format=(string)UYVY ! decodebin ! videoconvert ! appsink", cv2.CAP_GSTREAMER)
    #cap = cv2.VideoCapture("videotestsrc ! video/x-raw, format=I420, width=640, height=480 ! vpuenc_h264 ! appsink",cv2.CAP_GSTREAMER)

    # the background Subractors
    subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
    #subtractor = cv2.createBackgroundSubtractorKNN()

    # FourCC is a 4-byte code used to specify the video codec. The list of available codes can be found in fourcc.org.
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')     # for windows
    
    CONTOUR_AREA_LIMIT = 10
    SKIP_FRAMES = 5

    BOX_MERGE_MAX_DIST = 30
    
    