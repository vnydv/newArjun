from typing import List
from utils import api, options, mergeCollate

import cv2
import numpy as np
from datetime import datetime
import json
import logging as log
import csv
import subprocess
#pip install rectangle-packer
import rpack


class AllFrameCapture(api.MotionsRecorder):

    def __init__(self):
        super().__init__()

        self.img_mean_persec_list = []    
        self.img_count_sum = 0
        self.img_count = 0
        # for storing frames as collection of 1 sec
        self.last_minute = None
        self.last_second = None

    def read_conf_options(self):
        super().read_conf_options()
    
    def startRecording(self):
        return super().startRecording()

    def stopRecording(self):
        return super().stopRecording()

    def process_image(self, frame):
        return super().process_image(frame)
    
    def saveImages(self, img):
        hasMovement, img2, bbox, sizes = self.process_image(img.copy())

        if options.Options.FRAME_DEBUG:
            img = img2
            hasMovement = True
        
        elif options.Options.CROP_IMAGES:     

            if options.Options.MERGE_NEARBY:
                                
                # merge nearby boxes        
                merged_bboxes, _ = mergeCollate.MergeCollator.merge_boxes(bbox,options.Options.BOX_MERGE_MAX_DIST)
                # twice to merge new overlapping ones
                merged_bboxes, sizes = mergeCollate.MergeCollator.merge_boxes( merged_bboxes, 0 )

            img = mergeCollate.MergeCollator.Collate(img, bbox, sizes)

        # get current time
        now = datetime.now()

        # if change in minutes
        if self.last_minute == None:
            self.last_minute = now.minute
        elif self.last_minute != now.minute:
            # if sec changes, save last second count data            
            if options.Options.SAVE_CSV: self.save_csv(now)
            #reset all
            self.last_minute = now.minute
            self.img_mean_persec_list = []
            self.img_count_sum = 0
            self.img_count = 0

        
        if hasMovement:

            # save image file
            self.temp_image_name = f'{now.strftime("%d-%m-%Y_%H-%M-%S-%f")}_{options.Options.DEVICE_SERIAL_ID}.jpg'
            #self.save_recording(img)
            if options.Options.FRAME_DEBUG:
                debug_temp_image_name = f'{now.strftime("%d-%m-%Y_%H-%M-%S-%f")}_{options.Options.DEVICE_SERIAL_ID}_debug.jpg'
                cv2.imwrite(options.Options.BUFFER_IMAGES_PATH + debug_temp_image_name, img2)

            cv2.imwrite(options.Options.BUFFER_IMAGES_PATH + self.temp_image_name, img)
            if options.Options.LOG_DEBUG: print('Saved Image: ', self.temp_image_name, len(bbox))

            # assign count data                        
            self.img_count_sum += len(bbox)
            self.img_count += 1


        # if a change in second then append mean
        # save mean every second
        if self.last_second == None:
            self.last_second = now.second
        elif self.last_second != now.second:
            # if sec changes, save last second count data            
            
            if self.img_count != 0:
                mean_count_persec = self.img_count_sum // self.img_count
            else:
                mean_count_persec = 0

            self.img_mean_persec_list.append((options.Options.DEVICE_SERIAL_ID, now.strftime("%d-%m-%Y_%H-%M-%S"), mean_count_persec))
            
            #reset all
            self.last_second = now.second                
            self.img_count_sum = 0
            self.img_count = 0

    def saveCSV(self, timeNow):
        # save as count_timeFrame_deviceID_countMeanInt.csv
        # save as count_DD-MM-YYYY_hh-mm_DOxxx_XXXX.csv

        csvName = f'count_{timeNow.strftime("%d-%m-%Y_%H")}-{self.last_minute}_{options.Options.DEVICE_SERIAL_ID}.csv'
        with open(options.Options.BUFFER_COUNT_PATH + csvName, 'w',  newline='') as csvFile:
            csvwriter = csv.writer(csvFile)
            # header
            csvwriter.writerow(["device_id","time_frame","insect_count"])        
            # data 
            csvwriter.writerows(self.img_mean_persec_list)
    
        log.info("Video bbox count CSV crealog.info("")ted and saved -> "+csvName)
        if options.Options.LOG_DEBUG: print('CSV saved', csvName)

    def saveRecording(self, image):
        return super().saveRecording(image)

MR = AllFrameCapture()

# do the process
MR.read_conf_options()
MR.startRecording()
MR.startRecording()