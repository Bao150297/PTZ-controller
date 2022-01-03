import json
import time

from onvif_controller import CameraControl

if __name__ == '__main__':

    with open("../../config.json", "r") as f:
        data = json.load(f)

    ptz_ctl = CameraControl(data["ip_camera"], data["onvif_id"], data["onvif_pwd"])
    ptz_ctl.camera_start()

    all_presets = ptz_ctl.get_preset()
    print(all_presets)

    # resp = ptz_ctl.set_preset("pre1")
    # print(resp)

    resp = ptz_ctl.go_to_preset("pre1")
    print(resp)
