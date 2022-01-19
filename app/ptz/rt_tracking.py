# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-21 10:44:55
# @Last Modified time: 2022-01-07 14:15:30

# We will try to perform trakcing object with relative move
import sys
sys.path.append("../..")
from app.ptz import *
import math
from math import tan, cos, sin, atan2, asin, sqrt
from onvif import ONVIFCamera
import cv2
import numpy as np
import time

def undistord(image):
    parameters = np.load("parameters.npz")
    mtx   = parameters["mtx"]
    dist  = parameters["dist"]
    rvecs = parameters["rvecs"]
    tvecs = parameters["tvecs"]

    h, w = image.shape[:2] #get the size of images
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # undistort
    dst = cv2.undistort(image, mtx, dist, None, newcameramtx)

    # crop the image
    # x,y,w,h = roi
    # dst = dst[y:y+h, x:x+w]
    return dst

def get_point(image):
    ''' Use color filter to get coordinate of sprinker '''
    # image = cv2.imread("sample.jpg")

    image = undistord(image)
    # if index == 1:
    #     cv2.imwrite("undistorted.jpg", image)
    # else:
    #     cv2.imwrite("undistorted_2.jpg", image)

    result = image.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Red object
    # lower = np.array([155, 25, 0])
    # upper = np.array([179, 255, 255])
    
    # Green object
    lower = np.array([36, 25, 25])
    upper = np.array([70, 255, 255])

    mask = cv2.inRange(image, lower, upper)

    diff = cv2.bitwise_and(result, result, mask=mask)
    diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    cnts, _ = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return_cnt = None
    com_x1, com_y1, com_x2, com_y2 = None, None, None, None 

    largest = 0 
    # Get largest object
    if not cnts is None:
        for cnt in cnts:
            if cv2.contourArea(cnt) < 50:
              continue
            (x, y, w, h) = cv2.boundingRect(cnt)
            if w * h > largest:
                largest = w * h
                _x = x + w
                _y = y + h
                # if com_x1 is None or x < com_x1:
                com_x1 = x
                # if com_y1 is None or y < com_y1:
                com_y1 = y
                # if com_x2 is None or _x > com_x2:
                com_x2 = _x
                # if com_y2 is None or _y > com_y2:
                com_y2 = _y

    # cv2.rectangle(diff, (com_x1, com_y1), (com_x2, com_y2), (255, 255, 255), 2)
    return_cnt = (int((com_x1 + com_x2) / 2), int((com_y1 + com_y2) / 2)) 

    # if index == 1:
    #     cv2.imwrite("mask.png", diff)

    # cv2.imshow('mask', mask)
    # cv2.imshow('result', result)
    # cv2.waitKey(0)
    # cap.release()
    # cv2.destroyAllWindows()
    return return_cnt, image.shape

if __name__ == '__main__':

    with open("../../config.json", "r") as f:
        data = json.load(f)

    mycam = ONVIFCamera(data["ip_camera"], 80, data["onvif_id"], data["onvif_pwd"])
    # Create media service object
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()

    # Get target profile
    media_profile = media.GetProfiles()[0]
    # print(media_profile.PTZConfiguration)

    rel_move = RelativeMove(ptz, media_profile)

    rtsp = data["rtsp_link"]
    cap  = cv2.VideoCapture(rtsp)

    h_small, w_small = 480, 640

    # FOV
    h_field, v_field = 55, 33

    hd_perpx = h_field / w_small
    vd_perpx = v_field / h_small * 1.714285714285714

    center = (320, 240)

    print("Start tracking")
    while 1:
        ret, frame = cap.read()
        if not ret:
            print("Disconnected")
            break

        start, _ = get_point(frame)
        print("Start from: ", start)

        move_p = (start[0]  - center[0]) # No problem
        move_t = 0 - (start[1]  - center[1])
        zoom   = 0

        move_p *= hd_perpx
        move_t *= vd_perpx

        # We assume ptz speed is 80 degrees per sec
        delay_time = (abs(move_p) + abs(move_t)) / 80 + 0.2 # 0.2s is time for sending request, device delay in perfoming move

        print("In degrees: ", move_p, ":", move_t)

        move_p = math.radians(move_p) / math.pi # * 2 # That's OK 
        move_t = math.radians(move_t) / math.pi

        print("In radians: ", move_p, ":", move_t)

        rel_move.custom_move(move_p, move_t, zoom)

        # time.sleep(delay_time)
        time.sleep(2)

    cap.release()
