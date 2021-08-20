# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-18 15:07:19
# @Last Modified by:   Bao
# @Last Modified time: 2021-08-20 14:47:18

# from onvif import ONVIFCamera

# mycam = ONVIFCamera('172.16.0.108', 80, 'admin', 'vnnet123456', 'wsdl/')

# dt = mycam.devicemgmt.GetSystemDateAndTime()
# print(dt)

# ptz_service = mycam.create_ptz_service()
# a = mycam.ptz.GetConfiguration()
# print(a)

# Now we need to perform a absolute moving
import asyncio, sys
from onvif import ONVIFCamera

import os
import sys
from utils import *

XMAX = 1
XMIN = -1
YMAX = 0.5
YMIN = -0.5

moverequest = None
ptz = None
active = False

def do_move(ptz, request):
    # Start continuous move
    global active
    if active:
        ptz.Stop({'ProfileToken': request.ProfileToken})
    active = True
    ptz.RelativeMove(request)

def to_left(ptz, request):
    # request.Translation.PanTilt.x = -0.2
    # request.Translation.PanTilt.y = -0.2
    request.Speed.PanTilt.x = -0.5
    request.Speed.PanTilt.y = -0.5
    request.Speed.Zoom = 0.1
    do_move(ptz, request)

def setup_move():
    mycam = ONVIFCamera('172.16.0.108', 80, 'onvif', 'vnnet123456')
    # Create media service object
    media = mycam.create_media_service()
    # Create ptz service object
    global ptz
    ptz = mycam.create_ptz_service()

    # Get target profile
    media_profile = media.GetProfiles()[0]

    # Get PTZ configuration options for getting continuous move range
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration.token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)
    # print(ptz_configuration_options)

    global moverequest
    moverequest = ptz.create_type('RelativeMove')
    moverequest.ProfileToken = media_profile.token
    if moverequest.Speed is None:
        moverequest.Translation = {'PanTilt': {'x': -0.5, 'y': -0.5}}
        moverequest.Speed       = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
    print(moverequest)

def readin():
    """Reading from stdin and displaying menu"""
    global moverequest, ptz
    
    selection = sys.stdin.readline().strip("\n")
    lov=[ x for x in selection.split(" ") if x != ""]
    if lov:
        
        if lov[0].lower() in ["l","left"]:
            to_left(ptz, moverequest)
        elif lov[0].lower() in ["d","do","dow","down"]:
            move_down(ptz, moverequest)
        elif lov[0].lower() in ["s","st","sto","stop"]:
            ptz.Stop({'ProfileToken': moverequest.ProfileToken})
            active = False
        else:
            print("What are you asking?\tI only know, 'up','down','left','right', 'ul' (up left), \n\t\t\t'ur' (up right), 'dl' (down left), 'dr' (down right) and 'stop'")
         
    print("")
    print("Your command: ", end='',flush=True)
       
            
if __name__ == '__main__':
    setup_move()
    while True:
        readin()

