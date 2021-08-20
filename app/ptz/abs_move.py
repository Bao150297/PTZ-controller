# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-18 15:07:19
# @Last Modified by:   Bao
# @Last Modified time: 2021-08-19 17:24:00

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
    ptz.AbsoluteMove(request)

def max_down(ptz, request):
    request.Position.PanTilt.x = 1
    request.Position.PanTilt.y = 1.0
    request.Position.Zoom.x = 0
    do_move(ptz, request)

# def move_up(ptz, request):
#     print ('move up...')
#     request.Position.PanTilt.x = 0.2
#     request.Position.PanTilt.y = -1.0
#     request.Position.Zoom.x = 0.2
#     # request.Speed.PanTilt.x = 0
#     # request.Speed.PanTilt.y = YMAX
#     # request.Speed.Zoom.x = 0
#     do_move(ptz, request)

def move_down(ptz, request):
    print ('move down...')
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = YMIN
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

    global moverequest
    moverequest = ptz.create_type('AbsoluteMove')
    moverequest.ProfileToken = media_profile.token
    if moverequest.Speed is None:
        # a = ptz.GetStatus({'ProfileToken': media_profile.token})
        # print(a)
        moverequest.Position = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
    print(moverequest.Position)

    # Get range of pan and tilt
    # NOTE: X and Y are velocity vector
    global XMAX, XMIN, YMAX, YMIN
    XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
    XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
    YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
    YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min


def readin():
    """Reading from stdin and displaying menu"""
    global moverequest, ptz
    
    selection = sys.stdin.readline().strip("\n")
    lov=[ x for x in selection.split(" ") if x != ""]
    if lov:
        
        if lov[0].lower() in ["md","max down"]:
            max_down(ptz, moverequest)
        elif lov[0].lower() in ["d","do","dow","down"]:
            move_down(ptz,moverequest)
        # elif lov[0].lower() in ["l","le","lef","left"]:
        #     move_left(ptz,moverequest)
        # elif lov[0].lower() in ["l","le","lef","left"]:
        #     move_left(ptz,moverequest)
        # elif lov[0].lower() in ["r","ri","rig","righ","right"]:
        #     move_right(ptz,moverequest)
        # elif lov[0].lower() in ["ul"]:
        #     move_upleft(ptz,moverequest)
        # elif lov[0].lower() in ["ur"]:
        #     move_upright(ptz,moverequest)
        # elif lov[0].lower() in ["dl"]:
        #     move_downleft(ptz,moverequest)
        # elif lov[0].lower() in ["dr"]:
        #     move_downright(ptz,moverequest)
        elif lov[0].lower() in ["s","st","sto","stop"]:
            ptz.Stop({'ProfileToken': moverequest.ProfileToken})
            active = False
        else:
            print("What are you asking?\tI only know, 'up','down','left','right', 'ul' (up left), \n\t\t\t'ur' (up right), 'dl' (down left), 'dr' (down right) and 'stop'")
         
    print("")
    print("Your command: ", end='',flush=True)
       
            
if __name__ == '__main__':
    setup_move()
    # loop = asyncio.get_event_loop()
    # try:
    #     # loop.add_reader(sys.stdin, readin)
    #     print("Use Ctrl-C to quit")
    #     print("Your command: ", end='',flush=True)
    #     # loop.run_forever()
    # except Exception as e:
    #     e_verbose(e)
    #     pass
    # finally:
    #     # loop.remove_reader(sys.stdin)
    #     # loop.close()
    #     print("end")
    while True:
        readin()

# numpy, appdirs, dataclasses, pytools, pyopencl