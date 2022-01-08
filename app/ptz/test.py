# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-12-14 09:46:40
# @Last Modified time: 2022-01-07 14:15:43

import json
import time

from onvif_controller import CameraControl

if __name__ == '__main__':

    with open("config.json", "r") as f:
        data = json.load(f)

    ptz_ctl = CameraControl(data["ip_camera"], data["onvif_id"], data["onvif_pwd"])
    ptz_ctl.camera_start()

    all_presets = ptz_ctl.get_preset()
    a = [i[1] for i in all_presets]
    print("Test" in a)

    # print(isinstance(all_presets, list))

    # resp = ptz_ctl.set_preset("pre1")
    # print(resp)

    # resp = ptz_ctl.go_to_preset("pre1")
    # print(resp)
    # ptz_ctl.relative_move(1, 0, 0)
