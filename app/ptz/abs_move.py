# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-18 15:07:19
# @Last Modified by:   Bao
# @Last Modified time: 2021-08-20 13:41:41

# Now we need to perform a absolute move
import sys
from onvif import ONVIFCamera
from app.ptz.utils import *

__all__ = ["AbsoluteMove"]

class AbsoluteMove():
    def __init__(self, ptz, media_profile):
        self.ptz = ptz
        request  = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = media_profile.PTZConfiguration.token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)

        self.moverequest = self.ptz.create_type('AbsoluteMove')
        self.moverequest.ProfileToken = media_profile.token
        if self.moverequest.Speed is None:
            self.moverequest.Position = ptz.GetStatus({'ProfileToken': media_profile.token}).Position

        self.active = False

    def do_move(self):
        # Start continuous move
        if self.active:
            self.ptz.Stop({'ProfileToken': self.moverequest.ProfileToken})
        self.active = True
        self.ptz.AbsoluteMove(self.moverequest)

    def move_down(self):
        print("move down...")
        self.moverequest.Position.PanTilt.x = 1.0
        self.moverequest.Position.PanTilt.y = -1.0
        self.moverequest.Position.Zoom.x = 0
        self.do_move()

    def move_up(self):
        print("move up...")
        self.moverequest.Position.PanTilt.x = 1.0
        self.moverequest.Position.PanTilt.y = 1.0
        self.moverequest.Position.Zoom.x = 0
        self.do_move()

    def move_left(self):
        print("move left")
        self.moverequest.Position.PanTilt.x = -1
        self.moverequest.Position.PanTilt.y = 1.0
        self.moverequest.Position.Zoom.x = 0
        self.do_move()

    def move_right(self):
        print("move left")
        self.moverequest.Position.PanTilt.x = 1
        self.moverequest.Position.PanTilt.y = 1.0
        self.moverequest.Position.Zoom.x = 0
        self.do_move()

    def custom_move(self, pan, tilt, zoom):
        print("custom absolute move")
        self.moverequest.Position.PanTilt.x = pan
        self.moverequest.Position.PanTilt.y = tilt
        self.moverequest.Position.Zoom.x = zoom
        self.do_move()        
