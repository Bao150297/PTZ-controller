# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-20 08:48:59
# @Last Modified time: 2022-01-07 14:14:30

import os
import sys
import json
from flask import (Flask,
                   request,
                   jsonify,
                   render_template,
                   send_from_directory)
from app.ptz import CameraControl

with open("config.json", "r") as f:
    data = json.load(f)

ptz_ctl = CameraControl(data["ip_camera"], data["onvif_id"], data["onvif_pwd"])
ptz_ctl.camera_start()
# Initialize the Flask application
app = Flask(__name__)

''' For video streaming via HLS '''
@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# FIXME: common path for m3u8 file and ts file
@app.route('/video/<string:file_name>')
def stream(file_name):
    root_dir = os.getcwd()
    return send_from_directory(os.path.join(root_dir, 'app', 'static', 'hls'), file_name, as_attachment=True)

@app.route('/video/app/static/hls/<string:file_name>')
def res_hls(file_name):
    root_dir = os.getcwd()
    return send_from_directory(os.path.join(root_dir, 'app', 'static', 'hls'), file_name, as_attachment=True)

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

# route http posts to this method
@app.route('/direct', methods=['POST'])
def direct():
    try:
        mtype = request.args.get("t")
        lov   = request.args.get("d")
    except Exception as e:
        return jsonify({"message": False}), 400

    if mtype == "con":
        # Continous move
        ptz_ctl.continuous_move(lov)
        return jsonify({"message": True}), 200 # Result True or False
    elif mtype == "abs":
        # Absolute move
        if not request.is_json:
            return jsonify({"message": False}), 400
        data = request.get_json()
        pan  = float(data["pan"])
        tilt = float(data["tilt"])
        # Zoom position
        zoom = float(data["zoom"])
        ptz_ctl.absolute_move(pan, tilt, zoom)
        return jsonify({"message": True}), 200 # Result True or False
    elif mtype == "rel":
        # Relative move
        if not request.is_json:
            return jsonify({"message": False}), 400
        data = request.get_json()
        pan  = float(data["pan"])
        tilt = float(data["tilt"])
        zoom = float(data["zoom"])
        ptz_ctl.relative_move(pan, tilt, zoom)
        return jsonify({"message": True}), 200 # Result True or False
    elif mtype == "rel_c":
        # Relative move with pre-defined point
        if not request.is_json:
            return jsonify({"message": False}), 400
        data = request.get_json()
        x, y = float(data["x"]), float(data["y"])
        ptz_ctl.point_move(x, y)
        return jsonify({"message": True}), 200 # Result True or False
    else:
        return jsonify({"message": False}), 400

@app.route('/get_loc')
def get_ptz_position():
    position = ptz_ctl.get_cur_position()
    return jsonify(position), 200

@app.route('/save_preset', methods=['POST'])
def save_preset():
    if not request.is_json:
        return jsonify({"message": "Bad request!"}), 400

    data = request.get_json()
    preset_name = data["name"]
    resp = ptz_ctl.set_preset(preset_name)
    if resp is not None:
        return jsonify({"message": "OK"}), 200

    return jsonify({"message": "Failed"}), 500

@app.route('/get_preset', methods=['GET'])
def get_preset():
    preset_list = ptz_ctl.get_preset()
    if not isinstance(preset_list, list):
        return jsonify({"message": "Failed!"}), 500

    resp_list = [i[1] for i in preset_list]
    return jsonify({"preset_list": resp_list}), 200

@app.route('/go_to_preset', methods=['POST'])
def go_to_preset():
    preset_name = request.args.get('name')
    ptz_ctl.go_to_preset(preset_name)
    return jsonify({"message": "OK"}), 200
