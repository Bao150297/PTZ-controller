# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-21 10:44:55
# @Last Modified by:   Bao
# @Last Modified time: 2021-08-26 10:57:22

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

def get_red_point(index=1):
    ''' Use color filter to get coordinate of sprinker '''
    # image = cv2.imread("sample.jpg")
    rtsp = "rtsp://admin:vnnet123456@172.16.0.108:554/Streaming/Channels/102"
    cap  = cv2.VideoCapture(rtsp)
    _, image = cap.read()

    image = undistord(image)
    if index == 1:
        cv2.imwrite("undistorted.jpg", image)
    else:
        cv2.imwrite("undistorted_2.jpg", image)

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

    cv2.rectangle(diff, (com_x1, com_y1), (com_x2, com_y2), (255, 255, 255), 2)
    return_cnt = (int((com_x1 + com_x2) / 2), int((com_y1 + com_y2) / 2)) 

    if index == 1:
        cv2.imwrite("mask.png", diff)

    # cv2.imshow('mask', mask)
    # cv2.imshow('result', result)
    # cv2.waitKey(0)
    cap.release()
    # cv2.destroyAllWindows()
    return return_cnt, image.shape

if __name__ == '__main__':

    mycam = ONVIFCamera('172.16.0.108', 80, 'onvif', 'vnnet123456')
    # Create media service object
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()

    # Get target profile
    media_profile = media.GetProfiles()[0]
    # print(media_profile.PTZConfiguration)

    # rel_move = RelativeMove(ptz, media_profile)

    # start, (h_small, w_small, _) = get_red_point()
    # print("Image size: ", w_small, "x", h_small)
    # print("Start from: ", start)

    # # Resolution of substream
    # w_small, h_small = 640, 480
    # # FOV
    # h_field, v_field = 55, 33

    # hd_perpx = h_field / w_small
    # vd_perpx = v_field / h_small * 1.714285714285714

    # center = (320, 240)

    # move_p = (start[0]  - center[0]) # No problem
    # move_t = 0 - (start[1]  - center[1])
    # zoom   = 0

    # move_p *= hd_perpx
    # move_t *= vd_perpx
    # print("In degrees: ", move_p, ":", move_t)

    # move_p = math.radians(move_p) / math.pi # * 2 # That's OK 
    # move_t = math.radians(move_t) / math.pi
    # # move_p = np.deg2rad(move_p)
    # # move_t = np.deg2rad(move_t)
    # print("In radians: ", move_p, ":", move_t)

    # rel_move.custom_move(move_p, move_t, zoom)
    ###################

    # w = w_small
    # h = h_small
    # x, y = destination

    # # Camera FOV.
    # fovx = 55
    # fovy = 33

    # # Camera current pan & tilt.
    # pan  = 0
    # tilt = 0

    # # 3D TO 2D
    # # Convert to 3D local coords.
    # lx = (2 * x / w - 1) * tan(fovx / 2)
    # ly = (-2 * y / h + 1) * tan(fovy / 2)
    # lz = 1

    # # Transform ray.
    # tx = cos(pan) * cos(tilt) * lx - cos(tilt) * sin(pan) * ly - sin(tilt) * lz
    # ty = sin(pan)             * lx + cos(pan)             * ly
    # tz = cos(pan) * sin(tilt) * lx - sin(pan) * sin(tilt) * ly + cos(tilt) * lz

    # # New pan & tilt to center object.
    # tilt = atan2(tz, tx)
    # pan  = asin(ty / sqrt((tx**2) + (ty**2) + (tz**2)))
    # print(tilt, pan)
    # rel_move.custom_move(pan, tilt, 0)
    ################### 

    #### Maybe we can change speed ####
    speed_changer = SpeedChanger(ptz, media_profile)
    speed_changer.change_speed(0.01, 0.01, 0.3)

    # time.sleep(0.5)
    abs_move = AbsoluteMove(ptz, media_profile)
    # abs_move.custom_move(1, 1, 0)
    abs_move.move_to_opposite()
    # time.sleep(10)
    # abs_move.ptz.Stop({'ProfileToken': con_move.moverequest.ProfileToken})
    # print("Stopped!")

    ###################################

    # time.sleep(2)
    # new_pts, _ = get_red_point(index=2)
    # print("After move: ", new_pts)
