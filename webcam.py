#! /usr/bin/env python

import os
import argparse
import json
import cv2
from utils.utils import get_yolo_boxes, makedirs
from utils.bbox import draw_boxes
from keras.models import load_model
from tqdm import tqdm
import numpy as np
import time 
import math

def main():
    config_path  = "config_voc.json"

    with open(config_path) as config_buffer:    
        config = json.load(config_buffer)
    net_h, net_w = 64, 64 
    obj_thresh, nms_thresh = 0.5, 0.45

    #os.environ['CUDA_VISIBLE_DEVICES'] = config['train']['gpus']
    #print(os.environ
    infer_model = load_model(config['train']['saved_weights_name'])
    cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture('test.mp4')
    images = []
    cam_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    cam_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    first_slice = math.ceil(cam_width / 3) #720p --> first_slice = 427
    second_slice = math.ceil(first_slice * 2) #720p --> second_slice = 854
    line_1_1 = (first_slice, 0)
    line_1_2 = (first_slice, int(cam_height))
    line_2_1 = (second_slice, 0)
    line_2_2 = (second_slice, int(cam_height))

    print(first_slice)
    print(second_slice)

    print("WIDTH : ", cam_width)
    print("HEIGHT :", cam_height)
    
    """
    pc kamerasi için: 
    width : 640
    heigt : 480

    webcam için:
    width : 1280
    height : 720
    """
    
    while True:
        ret, image = cap.read()
        stime = time.time()
        if ret: 
            images += [image]
            batch_boxes = get_yolo_boxes(infer_model, images, net_h, net_w, config['model']['anchors'], obj_thresh, nms_thresh)

            for i in range(len(images)):
                images[i], bbox = draw_boxes(images[i], batch_boxes[i], config['model']['labels'], obj_thresh) 
                #bbox = ...
                # bu kısımda pixel kordinatlarının orta noktaları hesaplanacak 
                cv2.line(images[i], line_1_1, line_1_2, (255, 0, 0))
                cv2.line(images[i], line_2_1, line_2_2, (255, 0, 0))
                cv2.imshow('video with bboxes', images[i])

                if bbox.any() != None:
                    #detection varsa
                    print("Detection is True")
                    #do something
                elif bbox == None:
                    #detection yok
                    print("Detection is False")
                    #do something
                print('FPS {:.1f}'.format(1 / (time.time() - stime))) 
            images = []
            print("ikinci resim")
        if cv2.waitKey(1) == 27: 
            break  # esc to quit
    cv2.destroyAllWindows()        
        
if __name__ == '__main__':
    main()
