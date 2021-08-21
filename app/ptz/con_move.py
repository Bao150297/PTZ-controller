# Do a continous move, only stop when reaching destination
import sys
from onvif import ONVIFCamera
from app.ptz.utils import *

__all__ = ["ContinousMove"]

class ContinousMove():
    def __init__(self, ptz, media_profile):

        self.ptz = ptz
        request  = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = media_profile.PTZConfiguration.token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)

        self.moverequest = self.ptz.create_type('ContinuousMove')
        self.moverequest.ProfileToken = media_profile.token
        if self.moverequest.Velocity is None:
            self.moverequest.Velocity = self.ptz.GetStatus({'ProfileToken': media_profile.token}).Position
            self.moverequest.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
            self.moverequest.Velocity.Zoom.space    = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI

        self.XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
        self.XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
        self.YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
        self.YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min
        self.active = False

    def do_move(self):
        # Start continuous move
        if self.active:
            self.ptz.Stop({'ProfileToken': self.moverequest.ProfileToken})
        self.active = True
        self.ptz.ContinuousMove(self.moverequest)

    def move_up(self, timeout=5):
        print('move up...')
        self.moverequest.Velocity.PanTilt.x = 0
        self.moverequest.Velocity.PanTilt.y = self.YMAX
        self.moverequest.Timeout = timeout
        self.do_move()

    def move_down(self, timeout=5):
        print('move down...')
        self.moverequest.Velocity.PanTilt.x = 0
        self.moverequest.Velocity.PanTilt.y = self.YMIN
        self.moverequest.Timeout = timeout
        self.do_move()

    def move_right(self, timeout=5):
        print ('move right...')
        self.moverequest.Velocity.PanTilt.x = self.XMAX
        self.moverequest.Velocity.PanTilt.y = 0
        self.moverequest.Timeout = timeout
        self.do_move()

    def move_left(self, timeout=5):
        print ('move left...')
        self.moverequest.Velocity.PanTilt.x = self.XMIN
        self.moverequest.Velocity.PanTilt.y = 0
        self.moverequest.Timeout = timeout
        self.do_move()
        
    def move_upleft(self, timeout=5):
        print('move up left...')
        self.moverequest.Velocity.PanTilt.x = self.XMIN
        self.moverequest.Velocity.PanTilt.y = self.YMAX
        self.moverequest.Timeout = timeout
        self.do_move()
        
    def move_upright(self, timeout=5):
        print('move up left...')
        self.moverequest.Velocity.PanTilt.x = self.XMAX
        self.moverequest.Velocity.PanTilt.y = self.YMAX
        self.moverequest.Timeout = timeout
        self.do_move()
        
    def move_downleft(self, timeout=5):
        print ('move down left...')
        self.moverequest.Velocity.PanTilt.x = self.XMIN
        self.moverequest.Velocity.PanTilt.y = self.YMIN
        self.moverequest.Timeout = timeout
        self.do_move()
        
    def move_downright(self, timeout=5):
        print ('move down left...')
        self.moverequest.Velocity.PanTilt.x = self.XMAX
        self.moverequest.Velocity.PanTilt.y = self.YMIN
        self.moverequest.Timeout = timeout
        self.do_move()
