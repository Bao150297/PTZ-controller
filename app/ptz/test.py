# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-12-14 09:46:40
# @Last Modified time: 2022-01-18 10:01:39

import json
import time
import cv2

from onvif_controller import CameraControl

if __name__ == '__main__':

    with open("config.json", "r") as f:
        data = json.load(f)

    ptz_ctl = CameraControl(data["ip_camera"], data["onvif_id"], data["onvif_pwd"])
    ptz_ctl.camera_start()

    all_presets = ptz_ctl.get_preset()
    # ptz_ctl.absolute_move(0, -0.73, 0)
    # ptz_ctl.absolute_move(0, -0.15, 0)
    # ptz_ctl.absolute_move(0, 0.43, 0)

    ptz_ctl.go_to_preset("Test")
    time.sleep(4)
    # ptz_ctl.relative_move(-0.054, 0.093, 0)
    # ptz_ctl.relative_move(0.155, -0.075, 0)
    # ptz_ctl.relative_move(0.09, 0.093, 0)
    # ptz_ctl.relative_move(-0.11, -0.06, 0)
    # ptz_ctl.relative_move(-0.058, -0.076, 0)
    # ptz_ctl.relative_move(-0.085, 0.08, 0)
    # ptz_ctl.relative_move(0.03, -0.09, 0)
    ptz_ctl.go_to_preset("Test 2")
    time.sleep(4)
    ptz_ctl.go_to_preset("Test 3")
    time.sleep(4)
    ptz_ctl.go_to_preset("Test 4")
    time.sleep(4)
    ptz_ctl.relative_move(0, 0, 0.3)
    time.sleep(4)
    ptz_ctl.relative_move(0, 0, -0.3)
    time.sleep(4)
