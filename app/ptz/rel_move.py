# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-18 15:07:19
# @Last Modified by:   Bao
# @Last Modified time: 2021-08-21 09:43:40

# Now we need to perform a relative moving
import sys
from onvif import ONVIFCamera

import os
from app.ptz.utils import *

__all__ = ["RelativeMove"]

class RelativeMove():
    def __init__(self, ptz, media_profile):
        self.ptz = ptz
        request  = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = media_profile.PTZConfiguration.token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)

        self.moverequest = self.ptz.create_type('RelativeMove')
        self.moverequest.ProfileToken = media_profile.token

        if self.moverequest.Speed is None:
            self.moverequest.Translation = {'PanTilt': {'x': 0.0, 'y': 0.0}}
            self.moverequest.Speed       = self.ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        self.active = True
        self.token  = media_profile.token

    def do_move(self):
        # Start continuous move
        if self.active:
            self.ptz.Stop({'ProfileToken': self.moverequest.ProfileToken})
        self.active = True
        self.ptz.RelativeMove(self.moverequest)        

    def custom_move(self, rel_pan, rel_tilt, rel_zoom):
        print("relative custom move")
        self.moverequest.Translation  = {'PanTilt': {'x': rel_pan, 'y': rel_tilt}, 'Zoom': {'x': rel_zoom}}
        self.moverequest.Speed.Zoom.x = {'PanTilt': {'x': 1, 'y': 1}, 'Zoom': 1}
        self.do_move()

