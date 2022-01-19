# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2022-01-03 08:51:16
# @Last Modified by:   ADMIN
# @Last Modified time: 2022-01-19 09:02:13

'''
PTZ controller put here
Reference: https://github.com/smartsenselab/sensecam-control
'''

import cv2
import math
import numpy as np
from onvif import ONVIFCamera

class CameraControl:
    """
    Module for control cameras using Onvif
    """

    def __init__(self, ip, user, password, calibrate=True):
        self.__cam_ip = ip
        self.__cam_user = user
        self.__cam_password = password

        self.calibrate = calibrate
        # For undistord point
        if calibrate:
            parameters = np.load("app/ptz/parameters.npz")
            self.mtx   = parameters["mtx"]
            self.dist  = parameters["dist"]
            self.rvecs = parameters["rvecs"]
            self.tvecs = parameters["tvecs"]

            self.newcameramtx, _ = cv2.getOptimalNewCameraMatrix(self.mtx, self.dist, (640, 480), 1, (640, 480))

        self.h_pov = 55 / 640
        self.v_pov = 33 / 480 * (180 / 105)

    def camera_start(self):
        """
        Creates the connection to the camera using the onvif protocol

        Returns:
            Return the ptz service object and media service object
        """
        mycam = ONVIFCamera(self.__cam_ip, 80, self.__cam_user, self.__cam_password)
        print('Create media service object')
        media = mycam.create_media_service()
        print('Create ptz service object')
        ptz = mycam.create_ptz_service()
        print('Get target profile')
        media_profile = media.GetProfiles()[0]
        print('Camera working!')

        self.mycam = mycam
        self.camera_ptz = ptz
        self.camera_media_profile = media_profile
        self.camera_media = media

        return self.camera_ptz, self.camera_media_profile

    def absolute_move(self, pan: float, tilt: float, zoom: float):
        """
        Operation to move pan, tilt or zoom to a absolute destination.

        Args:
            pan: Pans the device relative to the (0,0) position.
            tilt: Tilts the device relative to the (0,0) position.
            zoom: Zooms the device n steps.

        Returns:
            Return onvif's response
        """
        request = self.camera_ptz.create_type('AbsoluteMove')
        request.ProfileToken = self.camera_media_profile.token
        request.Position = {'PanTilt': {'x': pan, 'y': tilt}, 'Zoom': zoom}
        resp = self.camera_ptz.AbsoluteMove(request)
        print('camera_command( aboslute_move(%f, %f, %f) )' %(pan, tilt, zoom))
        return resp

    def continuous_move(self, direction):
        """
        Operation for continuous Pan/Tilt and Zoom movements.

        Args:
            pan: speed of movement of Pan.
            tilt: speed of movement of Tilt.
            zoom: speed of movement of Zoom.

        Returns:
            Return onvif's response.
        """
        config_req = self.camera_ptz.create_type('GetConfigurationOptions')
        ptz_configuration_options = self.camera_ptz.GetConfigurationOptions(config_req)

        XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
        XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
        YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
        YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

        if direction.lower() in ["u","up"]:
            x, y = 0, YMAX
        elif direction.lower() in ["d","do","dow","down"]:
            x, y = 0, YMIN
        elif direction.lower() in ["l","le","lef","left"]:
            x, y = XMIN, 0
        elif direction.lower() in ["r","ri","rig","righ","right"]:
            x, y = XMAX, 0
        elif direction.lower() in ["ul"]:
            x, y = XMIN, YMAX
        elif direction.lower() in ["ur"]:
            x, y = XMAX, YMAX
        elif direction.lower() in ["dl"]:
            x, y = XMIN, YMIN
        elif direction.lower() in ["dr"]:
            x, y = XMAX, YMIN
        elif direction.lower() in ["s","st","sto","stop"]:
            self.stop_move()

        request = self.camera_ptz.create_type('ContinuousMove')
        request.ProfileToken = self.camera_media_profile.token
        request.Velocity = {'PanTilt': {'x': x, 'y': y}, 'Zoom': 0}
        resp = self.camera_ptz.ContinuousMove(request)
        print('camera_command( continuous_move(%f, %f, %f) )' %(x, y, 0))
        return resp

    def relative_move(self, pan: float, tilt: float, zoom: float):
        """
        Operation for Relative Pan/Tilt and Zoom Move.

        Args:
            pan: A positional Translation relative to the pan current position.
            tilt: A positional Translation relative to the tilt current position.
            zoom:

        Returns:
            Return onvif's response
        """
        request = self.camera_ptz.create_type('RelativeMove')
        request.ProfileToken = self.camera_media_profile.token
        request.Translation = {'PanTilt': {'x': pan, 'y': tilt}, 'Zoom': zoom}
        resp = self.camera_ptz.RelativeMove(request)
        print('camera_command( relative_move(%f, %f, %f) )' %(pan, tilt, zoom))
        return resp

    def point_move(self, x, y):
        x, y = round(x), round(y)
        """ Provide x, y coordinate on image, center image to this point """
        if self.calibrate:
            in_point = np.asarray((x, y), dtype=np.float).reshape(1, 2)
            out_point = cv2.undistortPoints(in_point, self.mtx, self.dist, P=self.newcameramtx)
            x, y = out_point[0][0]

        move_p = x  - 320 # No problem
        move_t = - (y  - 240)

        move_p *= self.h_pov
        move_t *= self.v_pov

        move_p = math.radians(move_p)
        move_t = math.radians(move_t)
        print("move_p, move_t: ", move_p, move_t)

        # move_p = round(move_p / math.pi, 5)
        # move_t = round(move_t / math.pi, 5)
        move_p = round(move_p * 0.34632, 5)
        move_t = round(move_t * 0.31831, 5)

        print("Move params: %d - %d - %.5f - %.5f" %(x, y, move_p, move_t))
        self.relative_move(move_p, move_t, 0)

    def get_cur_position(self):
        ptz_status = self.camera_ptz.GetStatus({'ProfileToken': self.camera_media_profile.token}).Position
        print('x: %.5f \ty: %.5f' %(ptz_status.PanTilt.x, ptz_status.PanTilt.y))
        current_location = dict({'p': 0, 't': 0, 'z': 0})
        current_location['p'] = ptz_status.PanTilt.x
        current_location['t'] = ptz_status.PanTilt.y
        current_location['z'] = ptz_status.Zoom.x
        return current_location

    def stop_move(self):
        """
        Operation to stop ongoing pan, tilt and zoom movements of absolute relative and continuous type.

        Returns:
            Return onvif's response
        """
        request = self.camera_ptz.create_type('Stop')
        request.ProfileToken = self.camera_media_profile.token
        resp = self.camera_ptz.Stop(request)
        print('camera_command( stop_move() )')
        return resp

    def set_home_position(self):
        """
        Operation to save current position as the home position.

        Returns:
            Return onvif's response
        """
        request = self.camera_ptz.create_type('SetHomePosition')
        request.ProfileToken = self.camera_media_profile.token
        resp = self.camera_ptz.SetHomePosition(request)
        self.camera_ptz.Stop({'ProfileToken': self.camera_media_profile.token})
        print('camera_command( set_home_position() )')
        return resp

    def go_home_position(self):
        """
        Operation to move the PTZ device to it's "home" position.

        Returns:
            Return onvif's response
        """
        request = self.camera_ptz.create_type('GotoHomePosition')
        request.ProfileToken = self.camera_media_profile.token
        resp = self.camera_ptz.GotoHomePosition(request)
        print('camera_command( go_home_position() )')
        return resp

    def get_ptz(self):
        """
        Operation to request PTZ status.

        Returns:
            Returns a list with the values ​​of Pan, Tilt and Zoom
        """
        request = self.camera_ptz.create_type('GetStatus')
        request.ProfileToken = self.camera_media_profile.token
        ptz_status = self.camera_ptz.GetStatus(request)
        pan = ptz_status.Position.PanTilt.x
        tilt = ptz_status.Position.PanTilt.y
        zoom = ptz_status.Position.Zoom.x
        ptz_list = (pan, tilt, zoom)
        print('camera_command( get_ptz() )')
        return ptz_list

    def set_preset(self, preset_name: str):
        """
        The command saves the current device position parameters.
        Args:
            preset_name: Name for preset.

        Returns:
            Return onvif's response.
        """
        presets = CameraControl.get_preset_complete(self)
        request = self.camera_ptz.create_type('SetPreset')
        request.ProfileToken = self.camera_media_profile.token
        request.PresetName = preset_name
        print('camera_command( set_preset%s) )' %preset_name)

        for i, _ in enumerate(presets):
            if str(presets[i].Name) == preset_name:
                print(
                    'Preset (\'%s\') not created. Preset already exists!' %preset_name)
                return None

        ptz_set_preset = self.camera_ptz.SetPreset(request)
        print('Preset (\'%s\') created!' %preset_name)
        return ptz_set_preset

    def get_preset(self):
        """
        Operation to request all PTZ presets.

        Returns:
            Returns a list of tuples with the presets.
        """
        ptz_get_presets = CameraControl.get_preset_complete(self)
        print('camera_command( get_preset() )')

        presets = []
        for i, _ in enumerate(ptz_get_presets):
            presets.append((i, ptz_get_presets[i].Name))
        return presets

    def get_preset_complete(self):
        """
        Operation to request all PTZ presets.

        Returns:
            Returns the complete presets Onvif.
        """
        request = self.camera_ptz.create_type('GetPresets')
        request.ProfileToken = self.camera_media_profile.token
        ptz_get_presets = self.camera_ptz.GetPresets(request)
        return ptz_get_presets

    def remove_preset(self, preset_name: str):
        """
        Operation to remove a PTZ preset.

        Args:
            preset_name: Preset name.

        Returns:
            Return onvif's response.
        """
        presets = CameraControl.get_preset_complete(self)
        request = self.camera_ptz.create_type('RemovePreset')
        request.ProfileToken = self.camera_media_profile.token
        print('camera_command( remove_preset(%s) )', preset_name)
        for i, _ in enumerate(presets):
            if str(presets[i].Name) == preset_name:
                request.PresetToken = presets[i].token
                ptz_remove_preset = self.camera_ptz.RemovePreset(request)
                print('Preset (\'%s\') removed!' %preset_name)
                return ptz_remove_preset
        print("Preset (\'%s\') not found!" %preset_name)
        return None

    def go_to_preset(self, preset_position: str):
        """
        Operation to go to a saved preset position.

        Args:
            preset_position: preset name.

        Returns:
            Return onvif's response.
        """
        presets = CameraControl.get_preset_complete(self)
        request = self.camera_ptz.create_type('GotoPreset')
        request.ProfileToken = self.camera_media_profile.token
        print('camera_command( go_to_preset(%s) )' %preset_position)
        for i, _ in enumerate(presets):
            str1 = str(presets[i].Name)
            if str1 == preset_position:
                request.PresetToken = presets[i].token
                resp = self.camera_ptz.GotoPreset(request)
                print("Goes to (\'%s\')" %preset_position)
                return resp
        print("Preset (\'%s\') not found!" %preset_position)
        return None
