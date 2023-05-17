from abc import ABC, abstractmethod
import json
import cv2
import numpy as np

import options
import camConnect

class MotionsRecorder(ABC):

    def __init__(self):
        self.cap = None

    @abstractmethod
    def read_conf_options(self):
        with open(options.Options.conf_file_path,'r') as file:
            data = json.load(file)

        options.Options.DEVICE_SERIAL_ID = data["device"]["SERIAL_ID"]
        options.Options.BUFFER_IMAGES_PATH = data["device"]["STORAGE_PATH"]
        options.Options.BUFFER_COUNT_PATH = data["device"]["COUNT_STORAGE_PATH"]
        print("OK")


    @abstractmethod
    def process_image(self, frame):
        '''
        frame : numpy ndarray

        --- return ---
        hasMovement, frame, detections, sizes'''

        store = frame
        
        #--------------------------
        # RGB plane normalization
        if options.Options.USE_RGB_NORM == True:
            rgb_planes = cv2.split(frame)

            result_norm_planes = []
            for plane in rgb_planes:
                dilated_img = cv2.dilate(plane, np.ones((11,11), np.uint8))
                bg_img = cv2.medianBlur(dilated_img, 5)
                diff_img = 255 - cv2.absdiff(plane, bg_img)
                norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
                result_norm_planes.append(norm_img)

            shadow_less_frame = cv2.merge(result_norm_planes) #result_norm

            # 120,255 works with some
            #  ---- use either - chnage THRES_MIN only
            THRES_MIN = 140
            #ret, thresh1 = cv2.threshold(shadow_less_frame,THRES_MIN,255,cv2.THRESH_BINARY)
            ret, thresh1 = cv2.threshold(shadow_less_frame,THRES_MIN, 255, cv2.THRESH_TOZERO_INV)

        
        #------------------         
        # bg sub & blurring - Noise removal       
        if options.Options.USE_RGB_NORM == True:
            imgOut = options.Options.subtractor.apply(thresh1)
        else:
            imgOut = options.Options.subtractor.apply(frame)

        imgOut = cv2.medianBlur(imgOut, 3)
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))

        imgOut1 = cv2.morphologyEx(imgOut, cv2.MORPH_OPEN, kernel,iterations = 2)
        imgOut1[imgOut1 == 127] = 0 # 0-> black
        
        imgOut2 = cv2.morphologyEx(imgOut1, cv2.MORPH_CLOSE, kernel,iterations = 2)
        # remove light variations(gray 127) - consider only Major Movement (white patches 255)    
        imgOut2[imgOut2 == 127] = 0 # 0-> black

        imgOut3 = cv2.morphologyEx(imgOut, cv2.MORPH_CLOSE, kernel,iterations = 2)
        # remove light variations(gray 127) - consider only Major Movement (white patches 255)    
        imgOut3[imgOut3 == 127] = 0 # 0-> black

        #------------------------w
        #draw contours
        contours, _ = cv2.findContours(imgOut2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detectionsRed = []
        # need for closepacking of cropped images
        sizesRed = []

        for cnt in contours:
            area = cv2.contourArea(cnt)            
            x, y, w, h = cv2.boundingRect(cnt)
            x,y = x-5,y-5
            w,h = w+10,h+10

            if self.CONTOUR_AREA_LIMIT < area:                
                x = 0 if x < 0 else options.Options.VID_RESO[0] if x > options.Options.VID_RESO[0] else x
                y = 0 if y < 0 else options.Options.VID_RESO[1] if y > options.Options.VID_RESO[1] else y
                w = options.Options.VID_RESO[0]-x if x+w > options.Options.VID_RESO[0] else w
                h = options.Options.VID_RESO[1]-y if y+h > options.Options.VID_RESO[1] else h
                detectionsRed.append([x, y, w, h])
                sizesRed.append([w,h])
        
        contours, _ = cv2.findContours(imgOut3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        numberofObjects = 0
        
        detections = []
        # need for closepacking of cropped images
        sizes = []

        for cnt in contours:            
            area = cv2.contourArea(cnt)            
            x, y, w, h = cv2.boundingRect(cnt)
            x,y = x-5,y-5
            w,h = w+10,h+10

            if self.CONTOUR_AREA_LIMIT < area:
                # remove red countous
                enclosedRed = []
                enclosedSizesRed = []
                thisEnclosedCount = 0

                for cntR, szR in zip(detectionsRed, sizesRed):
                    _x, _y, = cntR[:2]

                    if (x < _x < x+w) and (y <_y <y+h):
                        thisEnclosedCount+=1
                        enclosedRed.append(cntR)
                        enclosedSizesRed.append(szR)

                if thisEnclosedCount < 2:
                    x = 0 if x < 0 else options.Options.VID_RESO[0] if x > options.Options.VID_RESO[0] else x
                    y = 0 if y < 0 else options.Options.VID_RESO[1] if y > options.Options.VID_RESO[1] else y
                    w = options.Options.VID_RESO[0]-x if x+w > options.Options.VID_RESO[0] else w
                    h = options.Options.VID_RESO[1]-y if y+h > options.Options.VID_RESO[1] else h
                    detections.append([x, y, w, h])
                    sizes.append([w,h])
                else:
                    detections.extend(enclosedRed)
                    sizes.extend(enclosedSizesRed)

        #------------------
        # display cntrs
        if options.Options.FRAME_DEBUG:
            for cntr in detections:
                x,y,w,h = cntr
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0,255, 0), 1)
                #cv2.drawContours(store, [cnt], -1, (255,0,0),2)
                numberofObjects = numberofObjects + 1
                cv2.putText(store,str(numberofObjects), (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_8)

            cv2.putText(store,"Number of objects: " + str(len(detections)), (10,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_8)

        hasMovement = len(detections) > 0 and len(detections) < 50

        return [hasMovement, frame, detections, sizes]    
    
    @abstractmethod
    def saveImages(self, img):
        return None

    @abstractmethod
    def saveCSV(self, timeNow):
        return None

    @abstractmethod
    def saveRecording(self, image):
        return None
    
    @abstractmethod
    def startRecording(self):
        camID = -1
        while camID == -1:
            #camID = self.get_cam_deviceID(options.Options.VID_RESO, self.FPS)
            camID = camConnect.CamConnect.get_cam_deviceID(options.Options.VID_RESO, options.Options.FPS)

        self.cap = cv2.VideoCapture(f"v4l2src device=/dev/video{camID} ! video/x-raw, width={options.Options.options.Options.VID_RESO[0]}, height={options.Options.VID_RESO[1]}, framerate={self.FPS}/1, format=(string)UYVY ! decodebin ! videoconvert ! appsink", cv2.CAP_GSTREAMER)
        #log.info("Cam started functioning")

        skipCount = 0
        
        while True :
            available, frame = self.cap.read()

            if available and skipCount > options.Options.SKIP_FRAMES:
                self.start_storing_img(frame)
                # check exit
                if cv2.waitKey(1) & 0xFF == ord('x'):
                    break
            else:
                skipCount+=1
                if options.Options.FRAME_DEBUG:
                    print("...Device Unavailable")
    
    @abstractmethod
    def stopRecording(self):
        self.save_recording()
        self.cap.release()
        cv2.destroyAllWindows()
