# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-23 15:08:57
# @Last Modified by:   Bao
# @Last Modified time: 2021-08-23 16:04:58

# How to zoom :3 ...
from onvif import ONVIFCamera
import sys
import time
# sys.path.append("../..")
# from app.ptz.utils import *

__all__ = ["ImagingSetup"]

class ImagingSetup():
    def __init__(self, imaging, media):
        self.imaging = imaging
        self.media   = media

        current_setting = self.media.GetVideoSources()

        self.imagingrequest = self.imaging.create_type('SetImagingSettings')
        # Get target profile
        video_sources = self.media.GetVideoSources()
        self.imagingrequest.VideoSourceToken = video_sources[0].token
        # if self.imagingrequest.ImagingSettings is None:
            # self.imagingrequest.ImagingSettings = current_setting[0].Imaging

        # print(self.imagingrequest)

    def adjust_focus(self):
        print("custom focus")
        self.imagingrequest.ImagingSettings = {'Focus': {
                                                    'AutoFocusMode': 'MANUAL',
                                                    'DefaultSpeed': 1.0,      
                                                    'NearLimit': 600.0,       
                                                    'FarLimit': 0.0,          
                                                    'Extension': None}}

        self.imaging.SetImagingSettings(self.imagingrequest)
        self.imagingrequest.ImagingSettings = None

    def adjust_brightness(self):
        print("adjust_brightness")
        self.imagingrequest.ImagingSettings = {'Brightness': 50.0}
        self.imaging.SetImagingSettings(self.imagingrequest)
        self.imagingrequest.ImagingSettings = None        

    def get_current_stt(self):
        request = self.media.GetVideoSources()
        print(request)
