#! /usr/bin/env python

"""
Print functions used for testing and debugging.

These functions will be removed after testing.
"""
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
import socket

UDP_IP = "xxxx" #RASPI IP ADRESİ
UDP_PORT = 8888


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
    PC Cam Resolution: 
    width : 640
    heigt : 480
    """
    
    """
    External Cam Resolution
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
                images[i], bbox, xmax, ymax = draw_boxes(images[i], batch_boxes[i], config['model']['labels'], obj_thresh)  
                if xmax != None:
                    print("Detection True First Kontrol")
                    print("XMAX :", xmax[0])
                    print("YMAX :", ymax[0])
                    print("XMIN : ", bbox[0][0])
                    print("Mid Point : ", (xmax[0]+(bbox[0][0] + 3)) / 2)
                    mid_point = math.ceil((xmax[0]+(bbox[0][0] + 3)) / 2)
                    mid_point_line_1 = (mid_point, ymax + 10)
                    mid_point_line_2 = (mid_point, ymax - 30) 
                    cv2.line(images[i], mid_point_line_1, mid_point_line_2, (0, 255, 0))

                cv2.line(images[i], line_1_1, line_1_2, (255, 0, 0))
                cv2.line(images[i], line_2_1, line_2_2, (255, 0, 0))
                cv2.namedWindow("Video Stream", cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty("Video Stream", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow('Video Stream', images[i])

                try:
                    #DETECTION IS TRUE BLOCK 
                    if bbox.any() != None:
                        print("Detection is True")
                        #0-640 arası degerler degisecek
                        if (mid_point > 0) and (mid_point < first_slice):
                            MESSAGE = "first_pwm"
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
                            print("PWM_1")
                        elif (mid_point >= first_slice) and (mid_point < second_slice):
                            MESSAGE = "second_pwm"
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
                            print("PWM_2")                        
                        elif (mid_point >= second_slice):
                            MESSAGE = "third_pwm"
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
                            print("PWM_3")
                            
                    #DETECTION IS FALSE BLOCK
                except:
                    print("detection yok")
                    print(bbox)

                print('FPS {:.1f}'.format(1 / (time.time() - stime))) 
            images = []
            print("ikinci resim")
        if cv2.waitKey(1) == 27: 
            break  # esc to quit
    cv2.destroyAllWindows()        
        
if __name__ == '__main__':
    main()
