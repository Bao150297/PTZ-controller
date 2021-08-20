# Do a continous move, only stop when reaching destination
import sys
from onvif import ONVIFCamera
from app.ptz.utils import *
# from utils import *

# XMAX = 1
# XMIN = -1
# YMAX = 1
# YMIN = -1

class ContinouseMove():
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

    def move_up(self):
        print('move up...')
        self.moverequest.Velocity.PanTilt.x = 0
        self.moverequest.Velocity.PanTilt.y = self.YMAX
        self.do_move()

    def move_down(self):
        print('move down...')
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = self.YMIN
        self.do_move(request)

    def move_right(self):
        print ('move right...')
        self.moverequest.Velocity.PanTilt.x = self.XMAX
        self.moverequest.Velocity.PanTilt.y = 0
        self.do_move()

    def move_left(self):
        print ('move left...')
        self.moverequest.Velocity.PanTilt.x = self.XMIN
        self.moverequest.Velocity.PanTilt.y = 0
        self.do_move()
        
    def move_upleft(self):
        print('move up left...')
        self.moverequest.Velocity.PanTilt.x = self.XMIN
        self.moverequest.Velocity.PanTilt.y = self.YMAX
        self.do_move()
        
    def move_upright(self):
        print('move up left...')
        self.moverequest.Velocity.PanTilt.x = self.XMAX
        self.moverequest.Velocity.PanTilt.y = self.YMAX
        self.do_move()
        
    def move_downleft(self):
        print ('move down left...')
        self.moverequest.Velocity.PanTilt.x = self.XMIN
        self.moverequest.Velocity.PanTilt.y = self.YMIN
        self.do_move()
        
    def move_downright(self):
        print ('move down left...')
        self.moverequest.Velocity.PanTilt.x = self.XMAX
        self.moverequest.Velocity.PanTilt.y = self.YMIN
        self.do_move()


moverequest = None
ptz = None
active = False

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
    moverequest = ptz.create_type('ContinuousMove')
    moverequest.ProfileToken = media_profile.token
    if moverequest.Velocity is None:
        moverequest.Velocity = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
        moverequest.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
        moverequest.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI
        print(moverequest)

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
        
        if lov[0].lower() in ["u","up"]:
            move_up(ptz,moverequest)
        elif lov[0].lower() in ["d","do","dow","down"]:
            move_down(ptz,moverequest)
        elif lov[0].lower() in ["l","le","lef","left"]:
            move_left(ptz,moverequest)
        elif lov[0].lower() in ["l","le","lef","left"]:
            move_left(ptz,moverequest)
        elif lov[0].lower() in ["r","ri","rig","righ","right"]:
            move_right(ptz,moverequest)
        elif lov[0].lower() in ["ul"]:
            move_upleft(ptz,moverequest)
        elif lov[0].lower() in ["ur"]:
            move_upright(ptz,moverequest)
        elif lov[0].lower() in ["dl"]:
            move_downleft(ptz,moverequest)
        elif lov[0].lower() in ["dr"]:
            move_downright(ptz,moverequest)
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