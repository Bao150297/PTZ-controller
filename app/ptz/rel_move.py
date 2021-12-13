# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-18 15:07:19
# @Last Modified by:   Bao
# @Last Modified time: 2021-08-26 14:04:42

# Now we need to perform a relative moving
import os
import sys
import math
import cv2
import numpy as np
import logging

from onvif import ONVIFCamera

from app.ptz.utils import *

__all__ = ["RelativeMove", "SpeedChanger"]

class RelativeMove():
    def __init__(self, ptz, media_profile):
        self.ptz = ptz
        request  = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = media_profile.PTZConfiguration.token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)
        # print(ptz_configuration_options)

        self.moverequest = self.ptz.create_type('RelativeMove')
        self.moverequest.ProfileToken = media_profile.token

        if self.moverequest.Speed is None:
            self.moverequest.Translation = {'PanTilt': {'x': 0.0, 'y': 0.0}}
            self.moverequest.Speed       = self.ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        self.active = True

        parameters = np.load("app/ptz/parameters.npz")
        self.mtx   = parameters["mtx"]
        self.dist  = parameters["dist"]
        self.rvecs = parameters["rvecs"]
        self.tvecs = parameters["tvecs"]

        self.newcameramtx, _ = cv2.getOptimalNewCameraMatrix(self.mtx, self.dist, (640, 480), 1, (640, 480))

        self.h_pov = 55 / 640
        self.v_pov = 33 / 480 * 1.714285714285714

    def get_cur_position(self):
        ''' Get current location in PanTilt
            http://www.onvif.org/onvif/ver20/ptz/wsdl/ptz.wsdl#op.RelativeMove
        Args:
            - pan, tilt, zoom: movement postition value
        '''
        current_location = dict({'p': 0, 't': 0, 'z': 0})
        ptz_status = self.ptz.GetStatus({'ProfileToken': self.moverequest.ProfileToken}).Position
        current_location['p'] = ptz_status.PanTilt.x
        current_location['t'] = ptz_status.PanTilt.y
        current_location['z'] = ptz_status.Zoom.x
        return current_location

    def do_move(self):
        # Start continuous move
        if self.active:
            self.ptz.Stop({'ProfileToken': self.moverequest.ProfileToken})
        self.active = True
        res = self.ptz.RelativeMove(self.moverequest)
        return res

    def custom_move(self, rel_pan, rel_tilt, rel_zoom):
        print("relative custom move")
        self.moverequest.Translation  = {'PanTilt': {'x': rel_pan, 'y': rel_tilt}, 'Zoom': {'x': rel_zoom}}
        self.moverequest.Speed.Zoom.x = {'PanTilt': {'x': 1, 'y': 1}, 'Zoom': 1}
        return self.do_move()

    def point_move(self, x, y):

        in_point = (x, y)
        in_point = np.expand_dims(np.asarray(in_point, dtype=np.float32), axis=0)
        out_point = cv2.undistortPoints(in_point, self.mtx, self.dist, P=self.newcameramtx)

        x, y = out_point[0][0]

        move_p = x  - 320 # No problem
        move_t = - (y  - 240)

        move_p *= self.h_pov
        move_t *= self.v_pov

        move_p = math.radians(move_p) / 2.3
        move_t = math.radians(move_t) / math.pi

        logging.info("Move params: %s - %.2f - %.2f - %.2f - %.2f" %(str(in_point), x, y, move_p, move_t))

        self.moverequest.Translation  = {'PanTilt': {'x': move_p, 'y': move_t}, 'Zoom': {'x': 0}}
        self.moverequest.Speed.Zoom.x = {'PanTilt': {'x': 1, 'y': 1}, 'Zoom': 1}
        return self.do_move()

class SpeedChanger():
    def __init__(self, ptz, media_profile):
        self.ptz = ptz
        request  = self.ptz.create_type('GetConfiguration')
        request.PTZConfigurationToken = media_profile.PTZConfiguration.token
        ptz_configuration_options = self.ptz.GetConfiguration(request)

        self.moverequest = self.ptz.create_type('SetConfiguration')

        if self.moverequest.PTZConfiguration is None:
            self.moverequest.PTZConfiguration = ptz_configuration_options
            self.moverequest.PTZConfiguration.Name = ptz_configuration_options.Name
            self.moverequest.ForcePersistence = True

        self.active = True
        self.token  = media_profile.token

    def change_speed(self, value_p, value_t, value_z):
        self.moverequest.PTZConfiguration.DefaultPTZSpeed = {'PanTilt': {'x': value_p, 'y': value_t}, 'Zoom': {'x': value_z}}
        # print(self.moverequest)
        self.ptz.SetConfiguration(self.moverequest)
