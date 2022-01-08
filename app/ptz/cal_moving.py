# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-12-11 08:47:12
# @Last Modified by:   dorihp
# @Last Modified time: 2022-01-07 14:19:15

import json
import time
import cv2
import numpy as np
from onvif import ONVIFCamera

class Detector():
    def __init__(self, cfg, weights, classes, input_size):
        super(Detector, self).__init__()

        assert input_size % 32 == 0, "Input size must be a multiple of 32!"

        # Init detector and it's parameters
        self.net = cv2.dnn_DetectionModel(cfg, weights)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        self.input_size = input_size

        self.net.setInputSize(input_size, input_size)
        self.net.setInputScale(1.0 / 255)
        self.net.setInputSwapRB(True)
        with open(classes, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')

    def detect(self, frame, cl_filter):
        classes, _, boxes = self.net.detect(frame, confThreshold=0.1, nmsThreshold=0.4)
        cen_x = cen_y = False
        # print(classes, boxes)

        if len(classes):
            for _class, box in zip(classes.flatten(), boxes):
                # if _class != cl_filter:
                    # continue

                left, top, width, height = box
                cen_x = int(left + width / 2)
                cen_y = int(top + height / 2)

                right = left + width
                bottom = top + height

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.circle(frame, (cen_x, cen_y), radius=0, color=(0, 0, 255), thickness=5)

                # break

        return frame, classes, boxes
        # return frame, cen_x, cen_y

class Undistort():
    def __init__(self, params):
        super(Undistort, self).__init__()

        parameters = np.load(params)
        self.mtx   = parameters["mtx"]
        self.dist  = parameters["dist"]

        self.newcameramtx, _ = cv2.getOptimalNewCameraMatrix(self.mtx, self.dist, (640, 480), 1, (640, 480))

    def do_undistort(self, frame):
        return cv2.undistort(frame, self.mtx, self.dist, None, self.newcameramtx)

def get_cur_position(ptz, token):
    ''' Get current location in PanTilt
        http://www.onvif.org/onvif/ver20/ptz/wsdl/ptz.wsdl#op.RelativeMove
    Args:
        - pan, tilt, zoom: movement postition value
    '''
    position   = dict({'x': 0, 'y': 0})
    ptz_status = ptz.GetStatus({'ProfileToken': token}).Position
    position['x'] = ptz_status.PanTilt.x
    position['y'] = ptz_status.PanTilt.y
    return position

def do_rel_move(ptz, token, pan, tilt, zoom=0):
    ''' Perfrom relative move
        http://www.onvif.org/onvif/ver20/ptz/wsdl/ptz.wsdl#op.RelativeMove
    Args:
        - pan, tilt, zoom: movement postition value
    '''
    moverequest = ptz.create_type('RelativeMove')
    moverequest.ProfileToken = token

    if moverequest.Speed is None:
        moverequest.Translation = {'PanTilt': {'x': 0.0, 'y': 0.0}}
        moverequest.Speed       = ptz.GetStatus({'ProfileToken': token}).Position

    moverequest.Translation  = {'PanTilt': {'x': pan, 'y': tilt}, 'Zoom': {'x': zoom}}
    moverequest.Speed.Zoom.x = {'PanTilt': {'x': 1, 'y': 1}, 'Zoom': 1}
    ptz.RelativeMove(moverequest)

def undistort_point(x, y):
    parameters = np.load("parameters.npz")
    mtx   = parameters["mtx"]
    dist  = parameters["dist"]
    rvecs = parameters["rvecs"]
    tvecs = parameters["tvecs"]

    h, w = 640, 480
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    in_point = (x, y)
    in_point = np.expand_dims(np.asarray(in_point, dtype=np.float32), axis=0)
    out_point = cv2.undistortPoints(in_point, mtx, dist, P=newcameramtx)

    return out_point

def get_point(image):
    ''' Use color filter to get coordinate of an object with specified color '''

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

    return return_cnt, diff

def main(detector, undistort):
    ''' In this function:
    - Do undistort on the first frame
    - Detect an object and get it's location
    - Perform a relative moving
    - Do undistort on the second frame
    - Detect and get location of the previous object again
    The object must be the only one in context
    '''
    with open("../../config.json", "r") as f:
        data = json.load(f)

    mycam = ONVIFCamera(data["ip_camera"], 80, data["onvif_id"], data["onvif_pwd"])
    # Create media service object
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()

    # Get target profile
    media_profile = media.GetProfiles()[0]
    token = media_profile.token

    cap = cv2.VideoCapture(data["rtsp_link"])
    frame_idx = 0

    while 1:
        # Capture the first frame
        ret, frame = cap.read()
        if not ret:
            print("Cannot connect to camera!")
            return

        if frame_idx == 0:

            frame = np.flip(frame, axis=0)
            frame = undistort.do_undistort(frame)
            # Get current camera position in Onvif coordinate system
            location = get_cur_position(ptz, token)
            print("Location before moving: Pan-%.5f \t Tilt-%.5f" %(location['x'], location['y']))

            # Detect object in this frame
            # frame_1, obj_x, obj_y = detector.detect(frame, 41)
            # print("Object's center coordinate before moving: ", obj_x, ":", obj_y)

            # Get object with color
            cnt, frame_1 = get_point(frame)
            print("Object's center coordinate before moving: ", cnt)

            # Do relative move
            move_p = 0.1
            move_t = 0.2
            do_rel_move(ptz, token, move_p, move_t)

        if frame_idx == 100:

            frame = np.flip(frame, axis=0)
            frame = undistort.do_undistort(frame)
            # Get new position of object
            # frame_2, _obj_x, _obj_y = detector.detect(frame, 1)
            # print("Object's center coordinate after moving: ", _obj_x, ":", _obj_x)

            _cnt, frame_2 = get_point(frame)
            print("Object's center coordinate after moving: ", _cnt)

            break

        frame_idx += 1

    cv2.imshow("Before", frame_1)
    cv2.imshow("After", frame_2)
    cv2.waitKey(0)

    cap.release()

if __name__ == '__main__':
    detector  = Detector("./yolov4/yolov4-tiny.cfg", "./yolov4/yolov4-tiny.weights", "./yolov4/coco.names", 416)
    undistort = Undistort("./calibrate-undistort-camera/parameters.npz")
    main(detector, undistort)
