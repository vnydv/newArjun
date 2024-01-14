import json
#import numpy as np
#import cv2
import datetime
from base64 import b64decode, b64encode
# import os


# todo
# get frames, counter, time, totalChunks etc. in oneline / message
# convert to images

# # clean tmp folder before use
# os.system('rm -r tmp')
# os.system('mkdir tmp')

#jsonFileName = "subscription_mqtt_data.json"
jsonFileName = "/home/omen/Downloads/subscription_mqtt_data.json"

temp_pkts = {}
aws_timestamps = []

Actualdata = {}
MissingTimestamp_dummyData = {}

ImageIDs = {}

def read_image_info(aws_timestamps, data):        
    # Opening JSON file
    f = open(jsonFileName)
 
    # returns JSON object as 
    # a dictionary
    data = json.load(f)
 
    # Iterating through the json
    # list
    count = len(data['messages'])

    lastImgID = -1

    for msg in data['messages']:
        payload = msg["payload"]["counter"]
        aws_timestamp = msg["timestamp"]

        decoded_bytes = b64decode(payload)
        base16_str = decoded_bytes.hex()
    
        info_part = base16_str[0:32]
        data_part = base16_str[256:]
        size_of_string = len(data_part)
        end_img = int(info_part[0:2], 16)
        deviceId = info_part[2:4]
        deviceId = int(deviceId, 16)
        chunkId = int(info_part[4:6], 16)
        totalChunks = int(info_part[6:8], 16)
        timestamp = info_part[8:28]

        image_id = int(info_part[28:30], 16)
    
        if lastImgID == -1:
            lastImgID = image_id

        #k = DecodeTimeStampsFromDevice(timestamp)

        if not image_id in ImageIDs:
            ImageIDs[image_id] = {"TotalChunks": totalChunks, "Rxd": [chunkId], "LateRxd": []}

        else:
            #ImageIDs[image_id] += [chunkID]
            if lastImgID != image_id:
                ImageIDs[image_id]["LateRxd"] += [chunkId]

            ImageIDs[image_id]["Rxd"] += [chunkId]

        lastImgID = image_id

        print(image_id, deviceId, chunkId, totalChunks, timestamp, aws_timestamp, end_img)
 
        temp_pkts[aws_timestamp] = (chunkId, totalChunks)
        aws_timestamps.append(aws_timestamp)

        Actualdata[aws_timestamp] = (data_part, end_img, chunkId)

        #temp_pkts.append([chunkId, totalChunks])

    #print("Scan Count:", count)
    # Closing file
    f.close()
    #temp_pkts = temp_pkts[::-1]

def generate_missed_data():
    
    for imgID in sorted(ImageIDs.keys()):
        _data = ImageIDs[imgID]
        total = _data["TotalChunks"]
        
        fall = [i+1 for i in range(total)]

        dups = []
        # check if any duplicates
        for fid in _data["Rxd"]:
            if not fid in fall:
                dups.append(fid)
            else:
                fall.remove(fid)
                
        # print if missing:
        if len(fall) != 0:
            print("MISSED: imgID:", imgID, "lost:", fall)            
        
        # print if duplicates
        if len(dups) != 0:
            print("Duplicates: imgID:", imgID, "dups:", dups)
        
        # print if late
        _late = _data["LateRxd"]
        if len(_late) != 0:
            print("Late Received: imgID:", imgID, "frags:", _late)
            

        


def save_to_image():
    pass


    #flag = True

    # try:
    #     if image_id not in image_data:
    #         image_data[image_id] = {}
    
    #     if 'image_text' not in image_data[image_id]:
    #         image_data[image_id][image_text] = [None] * totalChunks
            
    #     if 'frag_id' not in image_data[image_id]:
    #         image_data[image_id][frag_id] = 0

            
    #     if chunkId > image_data[image_id][frag_id]:
    #         image_data[image_id][frag_id] = chunkId
    #         image_data[image_id][image_text][chunkId-1] = {
    #             "data_part": data_part,
    #             "deviceId": deviceId,
    #             "timestamp": timestamp,
    #             "end_img": end_img
    #         }
    #         if chunkId == len(image_data[image_id][image_text]):
    #             full_image_data = ""
    #             name = ""
    #             deviceId = ""
    #             for index, data in enumerate(image_data[image_id][image_text]): 
    #                 if data is not None:
    #                     name = data["timestamp"]
    #                     deviceId = data["deviceId"]
    #                     if index == len(image_data[image_id][image_text])-1:
    #                         full_image_data+=(data['data_part'][0: end_img*256])
    #                     else:
    #                         full_image_data+=data['data_part']   
    #                 else: 
    #                     if index == 0:
    #                         full_image_data+= "ffd8ff"
    #                         full_image_data+= "0"*(size_of_string-6)
    #                     elif index == len(image_data[image_id][image_text])-1:
    #                         full_image_data+= "0"*(end_img-4)
    #                         full_image_data+="ffd9"
    #                     else:
    #                         full_image_data+="0"*size_of_string
    #             decoded_bytes = bytes.fromhex(full_image_data)
    #             base64_str = b64encode(decoded_bytes).decode() 
    #             JPEG_r = b64decode(base64_str)
    #             na_r = cv2.imdecode(np.frombuffer(JPEG_r, dtype=np.uint8), cv2.IMREAD_COLOR)
    #             filename = '/tmp/' + "test.jpg"
    #             cv2.imwrite(filename, na_r)  
    #             name = deviceId + "_" + time_conversion(name) + ".jpg"                
    #             #del image_data[image_id] #---Required ??
    #     else:
    #         flag = False
    #         full_image_data = ""
    #         name = ""
    #         deviceId = ""
    #         last_index = size_of_string
    #         for index, data in enumerate(image_data[image_id][image_text]): 
    #             if data is not None:
    #                 name = data["timestamp"]
    #                 deviceId = data["deviceId"]
    #                 last_index = data["end_img"]
    #                 if index == len(image_data[image_id][image_text])-1:
    #                     full_image_data+=(data['data_part'][0: last_index*256])
    #                 else:
    #                     full_image_data+=data['data_part']   
    #             else: 
    #                 if index == 0:
    #                     full_image_data+= "ffd8ff"
    #                     full_image_data+= "0"*(size_of_string-6)
    #                 elif index == len(image_data[image_id][image_text])-1:
    #                     full_image_data+= "0"*(last_index-4)
    #                     full_image_data+="ffd9"
    #                 else:
    #                     full_image_data+="0"*size_of_string
    #         del image_data[image_id]
    #         if image_id not in image_data:
    #             image_data[image_id] = {}
        
    #         if 'image_text' not in image_data[image_id]:
    #             image_data[image_id][image_text] = [None] * totalChunks
                
    #         if 'frag_id' not in image_data[image_id]:
    #             image_data[image_id][frag_id] = 0
            
    #         image_data[image_id][frag_id] = chunkId
    #         image_data[image_id][image_text][chunkId-1] = {
    #             "data_part": data_part,
    #             "deviceId": deviceId,
    #             "timestamp": timestamp,
    #             "end_img": end_img
    #         }
            
    #         decoded_bytes = bytes.fromhex(full_image_data)
    #         base64_str = b64encode(decoded_bytes).decode() 
    #         JPEG_r = b64decode(base64_str)
    #         na_r = cv2.imdecode(np.frombuffer(JPEG_r, dtype=np.uint8), cv2.IMREAD_COLOR)
    #         filename = '/tmp/' + "test.jpg"
    #         cv2.imwrite(filename, na_r)  
    #         name = deviceId + "_" + time_conversion(name) + ".jpg"
    #         # -- ?? shouldn't the filename be name rather than ./test.jpg
    #         #s3_resource.Object(bucket_name, name).upload_file(Filename=filename)
    
                
    # except Exception as exc:
    #     # if image_id not in image_data:
    #     #     image_data[image_id] = {}
    
    #     # if 'image_text' not in image_data[image_id]:
    #     #     image_data[image_id]['image_text'] = [None] * totalChunks
            
    #     # if 'frag_id' not in image_data[image_id]:
    #     #     image_data[image_id]['frag_id'] = 0
            
    #     # image_data[image_id][image_text] = [None] * totalChunks
    #     # image_data[image_id][frag_id] = chunkId
    #     # image_data[image_id][image_text][chunkId-1] = {
    #     #     "data_part": data_part,
    #     #     "deviceId": deviceId,
    #     #     "timestamp": timestamp
    #     # }
    #     if flag == True:
    #         del image_data[image_id]
    #     return {
    #         'statusCode': 400,
    #         'body': json.dumps(str(exc)) 
    #     }

ok_timestamps = {}

def make_images(msdd):
    
    found_frames = {}

    last_tot_frames = 0
    cur_frame_id = 0
    cur_tot_frames = 0
    last_timstamp = 0

    #pkts_timestamps = sorted(temp_pkts.keys())

    for tmp in aws_timestamps[::-1]:
        cur_frame_id, cur_tot_frames = temp_pkts[tmp]        

        if len(found_frames) == 0:
            print()
            print(tmp, temp_pkts[tmp])
            last_timstamp = tmp
            ok_timestamps[last_timstamp] = True
            found_frames = {i+1:0 for i in range(cur_tot_frames)}
            print(list(found_frames.keys()))
            last_tot_frames = cur_tot_frames
            del found_frames[cur_frame_id]            
            print("-",cur_frame_id, end=' ',sep='')
            print(list(found_frames.keys()))
            continue

        if last_tot_frames != cur_tot_frames:
            
            # missed frames
            #print("Missed frames ", *found_frames)
            found_frames = {i+1:0 for i in range(cur_tot_frames)}
            last_tot_frames = cur_tot_frames
            del found_frames[cur_frame_id]            
            #print("+", found_frames, "\\t\t-", cur_frame_id)
            print('*')
            print(cur_frame_id, end=' ',sep='')
            print(list(found_frames.keys()))
            continue
        
        flag = True
        # if last_tot_frames in found_frames:
        #     if cur_frame_id in found_frames:
        #         if cur_frame_id < last_tot_frames:
        #             flag = False

        
        if cur_frame_id in found_frames and (Actualdata[tmp][1] == Actualdata[last_timstamp][1]):
        #if flag and cur_frame_id in found_frames:
            del found_frames[cur_frame_id]            
            print("-",cur_frame_id, end = ' ',sep='')        
            print(list(found_frames.keys()))
        else:
            # not found
            # print all the missed packets
            print("Missed:", list(found_frames.keys()), last_timstamp, '\n')

            msdd[last_timstamp] = {}

            last_index = len(Actualdata[last_timstamp][0])

            # create dummy data for the missed segments:
            # all found segments are deleted from found_frames
            for i in found_frames:                
                msdd[last_timstamp][i] = ""
                if i == 1:
                    # append the inital jpeg bytes
                    msdd[last_timstamp][i] += "ffd8ff"
                    msdd[last_timstamp][i]+= "0"*(last_index-6)
                
                elif i == cur_tot_frames:
                    # append the last jpeg bytes
                    msdd[last_timstamp][i]+= "0"*(last_index-4)
                    msdd[last_timstamp][i]+="ffd9"

                else:
                    msdd[last_timstamp][i] = "0"*last_index


            ok_timestamps[last_timstamp] = False
            print(tmp, temp_pkts[tmp])
            last_timstamp = tmp
            found_frames = {i+1:0 for i in range(cur_tot_frames)}
            last_tot_frames = cur_tot_frames
            ok_timestamps[last_timstamp] = True
            del found_frames[cur_frame_id]
            print("-",cur_frame_id, end = ' ',sep='')
            print(list(found_frames.keys()))
            #print(f"x<{tmp},{cur_frame_id}>") 
    else:        
        if found_frames != {}:
            print("Missed:", list(found_frames.keys()), last_timstamp, '\n')
            msdd[last_timstamp] = {}
            last_index = len(Actualdata[last_timstamp][0])

            # create dummy data for the missed segments:
            # all found segments are deleted from found_frames
            for i in found_frames:                
                msdd[last_timstamp][i] = ""
                if i == 1:
                    # append the inital jpeg bytes
                    msdd[last_timstamp][i] += "ffd8ff"
                    msdd[last_timstamp][i]+= "0"*(last_index-6)
                
                elif i == cur_tot_frames:
                    # append the last jpeg bytes
                    msdd[last_timstamp][i]+= "0"*(last_index-4)
                    msdd[last_timstamp][i]+="ffd9"

                else:
                    msdd[last_timstamp][i] = "0"*last_index

            ok_timestamps[last_timstamp] = False
            print(tmp, temp_pkts[tmp])


    print("\nCount Missing Segments",len(msdd),"\n\n")

def print_timestamp_info():
    print("Valid Timestamps")
    for tmp in sorted(ok_timestamps.keys()):
        if ok_timestamps[tmp] == True:
            print(tmp)
    

def construct_images():

    for tmp in ok_timestamps:
        if ok_timestamps[tmp] == True:
            print("\nProcessing:",tmp)
            _, totalChunks = temp_pkts[tmp]
            
            full_image_data = ""
            last_index = len(Actualdata[tmp][0])

            image_data = [None] * totalChunks

            tmpst_id = aws_timestamps.index(tmp)            

            # sort chunks based on chunkID
            _tempIDs = {}
            for i in range(totalChunks):
                tmpst = aws_timestamps[tmpst_id-i]                
                _tempIDs[Actualdata[tmpst][2]] = tmpst
            print("Sorted", _tempIDs)
            
            for i in range(totalChunks):
                #tmpst = aws_timestamps[tmpst_id-i]                
                try:
                    tmpst = _tempIDs[i+1]
                except:
                    print("ERROR",i, _tempIDs)
                print(tmpst)                
                if i == (totalChunks - 1):                    
                    full_image_data+=((Actualdata[tmpst][0])[0: Actualdata[tmpst][1]*256])                    
                else:                    
                    full_image_data+=(Actualdata[tmpst][0])                    

            #print(full_image_data)

            decoded_bytes = bytes.fromhex(full_image_data)
            base64_str = b64encode(decoded_bytes).decode() 
            JPEG_r = b64decode(base64_str)            
            na_r = cv2.imdecode(np.frombuffer(JPEG_r, dtype=np.uint8), cv2.IMREAD_COLOR)
            #print(na_r)
            name = "09" + "_" + str(tmp) + ".jpg"
            filename = 'tmp/' + name
            try:
                cv2.imwrite(filename, na_r)
                print('saved to disk.')
            except Exception as exe:
                print("ERROR:",tmp)
                print(exe)

        else:
            pass
            # if missing timestamps
            print("\nProcessing Distorted Image:",tmp)
            print("Missing", list(MissingTimestamp_dummyData[tmp].keys()))
            _, totalChunks = temp_pkts[tmp]
            
            full_image_data = ""
            last_index = len(Actualdata[tmp][0])

            image_data = [None] * totalChunks

            tmpst_id = aws_timestamps.index(tmp)

            # sort chunks based on chunkID

            _tempIDs = {}

            for i in range(totalChunks):                
                tmpst = aws_timestamps[tmpst_id-i]
                _tempIDs[Actualdata[tmpst][2]] = tmpst

            for i in MissingTimestamp_dummyData[tmp]:
                _tempIDs[i] = -1

            print("Sorted", _tempIDs)
            
            for i in range(totalChunks):
                tmpst = _tempIDs[i+1]                
                #tmpst = aws_timestamps[tmpst_id-i]
                print(tmpst)

                if i==0 and tmpst == -1:
                    full_image_data+= MissingTimestamp_dummyData[tmp][i+1]
                elif i == (totalChunks - 1):
                    if tmpst != -1:
                        full_image_data+=((Actualdata[tmpst][0])[0: Actualdata[tmpst][1]*256])
                    else:
                        full_image_data+= MissingTimestamp_dummyData[tmp][i+1]
                else:
                    if tmpst != -1:
                        full_image_data+=(Actualdata[tmpst][0])                    
                    else:
                        full_image_data+= MissingTimestamp_dummyData[tmp][i+1]

            #print(full_image_data)

            decoded_bytes = bytes.fromhex(full_image_data)
            base64_str = b64encode(decoded_bytes).decode() 
            JPEG_r = b64decode(base64_str)            
            na_r = cv2.imdecode(np.frombuffer(JPEG_r, dtype=np.uint8), cv2.IMREAD_COLOR)
            #print(na_r)
            name = "missed_09" + "_" + str(tmp) + ".jpg"
            filename = 'tmp/' + name
            try:
                cv2.imwrite(filename, na_r)
                print('saved to disk.')
            except Exception as exe:
                print("ERROR:",tmp)
                print(exe)


def test_random_tmpst(tmp):
    #1704948153100
    
    print("\n\nRandom Processing:",tmp)
    _, totalChunks = temp_pkts[tmp]
    
    full_image_data = ""
    last_index = len(Actualdata[tmp][0])
    
    image_data = [None] * totalChunks

    tmpst_id = aws_timestamps.index(tmp)            

    # sort chunks based on chunkID

    _tempIDs = {}

    if True or ok_timestamps.get(tmp, 0) == True:
        for i in range(totalChunks):
            tmpst = aws_timestamps[tmpst_id-i]
            print(Actualdata[tmpst][2])
            _tempIDs[Actualdata[tmpst][2]] = tmpst
        print("Sorted", _tempIDs)
    else:
        print("SKIPED: -> can't be sorted missing segments")

    for i in range(totalChunks):
        if _tempIDs == {}:
            tmpst = aws_timestamps[tmpst_id-i]
        else:
            tmpst = _tempIDs[i+1]
        print(tmpst)
        # if i==0:
        #     full_image_data+= "ffd8ff"
        #     full_image_data+= "0"*(last_index-6)
        
        if i == (totalChunks - 1):
            #full_image_data+= "0"*(last_index-4)
            full_image_data+=((Actualdata[tmpst][0])[0: Actualdata[tmpst][1]*256])
            #full_image_data+="ffd9"
        else:                    
            full_image_data+=(Actualdata[tmpst][0])
            #full_image_data+= "0"*(last_index)

    #print(full_image_data)

    decoded_bytes = bytes.fromhex(full_image_data)
    base64_str = b64encode(decoded_bytes).decode() 
    JPEG_r = b64decode(base64_str)
    na_r = cv2.imdecode(np.frombuffer(JPEG_r, dtype=np.uint8), cv2.IMREAD_COLOR)
    #print(na_r)
    name = "randTest_09" + "_" + str(tmp) + ".jpg"
    filename = 'tmp/' + name
    try:
        cv2.imwrite(filename, na_r)
        print('saved to disk.')
    except Exception as exe:
        print(tmp)
        print(exe)


read_image_info(aws_timestamps, Actualdata)

print("\n\nSummary:\n")

generate_missed_data()

#make_images(MissingTimestamp_dummyData)
#print_timestamp_info()
print('\n\n')

#construct_images()

# test_random_tmpst(1704948138752)
# test_random_tmpst(1704948206787)
# test_random_tmpst(1704947549975)
# test_random_tmpst(1704947533063)
