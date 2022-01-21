# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-12-14 09:46:40
# @Last Modified time: 2022-01-20 11:13:39

import json
import time
import cv2

from onvif_controller import CameraControl

def check_preset_exists(ptz_ctl):
    all_presets = ptz_ctl.get_preset()
    all_ps_names = [p[1] for p in all_presets]
    efd_ps_names = ["EFD_preset_%d" %i for i in range(1, 24)]
    # Check if a list contains all other elements of another list
    return set(efd_ps_names).issubset(all_ps_names)

if __name__ == '__main__':

    with open("config.json", "r") as f:
        data = json.load(f)

    ptz_ctl = CameraControl(data["ip_camera"], data["onvif_id"], data["onvif_pwd"])
    ptz_ctl.camera_start()

    # ptz_ctl.remove_preset("EFD_preset_1")
    # a = check_preset_exists(ptz_ctl)
    # print(a)

    # all_presets = ptz_ctl.get_preset()

    # y_pos = [-0.73, -0.15, 0.43]
    # step_id = 1
    ptz_ctl.relative_move(-0.0001, -0.0001, 0.25000)
    # time.sleep(4)

    # for step_id in range(1, 24):
    #     ptz_ctl.set_preset("EFD_preset_%d" %step_id)
    #     if step_id % 8 == 0:
    #         circle_id = step_id // 8
    #         ptz_ctl.absolute_move(0, y_pos[circle_id], 0)
    #     else:
    #         ptz_ctl.relative_move(0.25, 0, 0)
    #     time.sleep(4)

    # ptz_ctl.absolute_move(0, -0.73, 0)
    # ptz_ctl.absolute_move(0, -0.15, 0)
    # ptz_ctl.absolute_move(0, 0.43, 0)
    # ptz_ctl.relative_move(-0.054, 0.093, 0)
    # ptz_ctl.relative_move(0.155, -0.075, 0)
    # ptz_ctl.relative_move(0.09, 0.093, 0)
    # ptz_ctl.relative_move(-0.11, -0.06, 0)
    # ptz_ctl.relative_move(-0.058, -0.076, 0)
    # ptz_ctl.relative_move(-0.085, 0.08, 0)
    # ptz_ctl.relative_move(0.03, -0.09, 0)
