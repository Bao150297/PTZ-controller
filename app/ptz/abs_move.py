# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-18 15:07:19
# @Last Modified by:   Bao
# @Last Modified time: 2021-08-26 10:39:33

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

        # print(self.moverequest)
        self.active = False
        self.token  = media_profile.token

    def do_move(self):
        # Start continuous move
        if self.active:
            self.ptz.Stop({'ProfileToken': self.moverequest.ProfileToken})
        self.active = True
        self.ptz.AbsoluteMove(self.moverequest)

    def custom_move(self, pan, tilt, zoom):
        print("custom absolute move")
        self.moverequest.Position.PanTilt.x = pan
        self.moverequest.Position.PanTilt.y = tilt
        self.moverequest.Position.Zoom.x = zoom
        # self.moverequest.Speed = {'PanTilt': {'x': 0.5, 'y': 0.5}, 'Zoom': 0}
        self.do_move()        

    def move_to_opposite(self):
        # Get current position
        ptz_status = self.ptz.GetStatus({'ProfileToken': self.token})
        self.moverequest.Position = ptz_status.Position
        # Then use abs to get opposite :3
        # self.moverequest.Position.PanTilt.x = 0 - self.moverequest.Position.PanTilt.x
        self.moverequest.Position.PanTilt.y = 0 - self.moverequest.Position.PanTilt.y
        self.moverequest.Speed = {'PanTilt': {'x': 0.1, 'y': 0.1}, 'Zoom': 0}
        self.do_move()