import rpack
import numpy as np

class MergeCollator():

    @staticmethod
    def merge_boxes(boxes, DIST):
        ''''''   
        merged_boxes = []

        for box in boxes:
            # Create a temp copy of box
            new_box = box

            # check if this overlap with merged boxes
            overlaps = []
            for mb in merged_boxes:
                if (box[0] + box[2] + DIST >= mb[0] and mb[0] + mb[2] + DIST >= box[0] and
                    box[1] + box[3] + DIST >= mb[1] and mb[1] + mb[3] + DIST >= box[1]):
                    overlaps.append(mb)

            if len(overlaps) > 0:
                # merge all overlapping boxes into a single new merged box
                overlaps.append(box)
                new_box = (min([b[0] for b in overlaps]), min([b[1] for b in overlaps]),
                        max([b[0]+b[2] for b in overlaps])-min([b[0] for b in overlaps]),
                        max([b[1]+b[3] for b in overlaps])-min([b[1] for b in overlaps]))

                # Remove all overlapping boxes from the list of merged boxes
                merged_boxes = [mb for mb in merged_boxes if mb not in overlaps]

            # Add the new or merged box to the list of merged boxes
            merged_boxes.append(new_box)

            # get there sizes
            sizes = [[b[2],b[3]] for b in merged_boxes]

        return merged_boxes, sizes


    @staticmethod
    def collate_boxes(img, bboxes, sizes):
        '''Crop detected regions and merge as single image'''
        
        if len(bboxes) == 0 or len(bboxes) > 40:
            print("Got 0 or A lot of boxes, try combining, returning.... This takes a lot of time....")
            return img

        #get new positions
        #area = sum([i[0]*i[1] for i in sizes])
        #print(area)
        #dimArea = int(area**0.5) + 1
        pos = rpack.pack(sizes)# dimArea*2, dimArea*2)
        #print(type(pos))

        sizes = np.array(sizes)
        positions = np.array(pos)

        #print(positions)

        # get maxY and maxX 
        reqH = max(sizes+positions, key=lambda x: x[0])[0]
        reqW = max(sizes+positions, key=lambda x: x[1])[1]
        
        reqH = reqW = max(reqW, reqH)
        # no indent
        if reqH >= MergeCollator.VID_RESO[0]:
            print("Exceeds original size, returning")
            return img

        #print('NewImageDims:',reqH, reqW)

        newImg = np.zeros((reqH,reqW,3), np.uint8)
        #newImg *= 255
        #print(newImg.shape)


        for i in range(len(bboxes)):
            # copy pixels from img to newImg
            #print('Cropping the bee...')
            #print(len(sizes), sizes)
            #print(len(positions) ,positions)
            #print(bboxes)
            #print('-'*50)
            y1, x1 = bboxes[i][0:2]
            h, l = sizes[i]

            y,x = positions[i]
            #print('PosOn_NewFrame:',x,x+l,y,y+h)
            #print('PosFrom_Frame :',x1,x1+l,y1,y1+h)
            #print(newImg.shape)
            #print(img.shape)
            newImg[x:x+l,y:y+h] = img[x1:x1+l,y1:y1+h]
        
        #cv2.imshow("ImgOut", newImg)
        
        return newImg@staticmethod
    def Collate(img, bboxes, sizes):
        '''Crop detected regions and merge as single image'''
        
        if len(bboxes) == 0 or len(bboxes) > 40:
            print("Got 0 or A lot of boxes, try combining, returning.... This takes a lot of time....")
            return img

        #get new positions
        #area = sum([i[0]*i[1] for i in sizes])
        #print(area)
        #dimArea = int(area**0.5) + 1
        pos = rpack.pack(sizes)# dimArea*2, dimArea*2)
        #print(type(pos))

        sizes = np.array(sizes)
        positions = np.array(pos)

        #print(positions)

        # get maxY and maxX 
        reqH = max(sizes+positions, key=lambda x: x[0])[0]
        reqW = max(sizes+positions, key=lambda x: x[1])[1]
        
        reqH = reqW = max(reqW, reqH)
        # no indent
        if reqH >= MergeCollator.VID_RESO[0]:
            print("Exceeds original size, returning")
            return img

        #print('NewImageDims:',reqH, reqW)

        newImg = np.zeros((reqH,reqW,3), np.uint8)
        #newImg *= 255
        #print(newImg.shape)


        for i in range(len(bboxes)):
            # copy pixels from img to newImg
            #print('Cropping the bee...')
            #print(len(sizes), sizes)
            #print(len(positions) ,positions)
            #print(bboxes)
            #print('-'*50)
            y1, x1 = bboxes[i][0:2]
            h, l = sizes[i]

            y,x = positions[i]
            #print('PosOn_NewFrame:',x,x+l,y,y+h)
            #print('PosFrom_Frame :',x1,x1+l,y1,y1+h)
            #print(newImg.shape)
            #print(img.shape)
            newImg[x:x+l,y:y+h] = img[x1:x1+l,y1:y1+h]
        
        #cv2.imshow("ImgOut", newImg)
        
        return newImg