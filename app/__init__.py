# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-20 08:48:59
# @Last Modified by:   Bao
# @Last Modified time: 2021-08-21 09:16:43
import os
import sys
from flask import (Flask,
                   request,
                   jsonify,
                   render_template,
                   send_from_directory)
from app.ptz import *
from onvif import ONVIFCamera

mycam = ONVIFCamera('172.16.0.108', 80, 'onvif', 'vnnet123456')
# Create media service object
media = mycam.create_media_service()
# Create ptz service object
ptz = mycam.create_ptz_service()

# Get target profile
media_profile = media.GetProfiles()[0]

# Movement handler instance
con_move = ContinousMove(ptz, media_profile)
abs_move = AbsoluteMove(ptz, media_profile)
rel_move = RelativeMove(ptz, media_profile)

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
        if lov.lower() in ["u","up"]:
            con_move.move_up()
        elif lov.lower() in ["d","do","dow","down"]:
            con_move.move_down()
        elif lov.lower() in ["l","le","lef","left"]:
            con_move.move_left()
        elif lov.lower() in ["l","le","lef","left"]:
            con_move.move_left()
        elif lov.lower() in ["r","ri","rig","righ","right"]:
            con_move.move_right()
        elif lov.lower() in ["ul"]:
            con_move.move_upleft()
        elif lov.lower() in ["ur"]:
            con_move.move_upright()
        elif lov.lower() in ["dl"]:
            con_move.move_downleft()
        elif lov.lower() in ["dr"]:
            con_move.move_downright()
        elif lov.lower() in ["s","st","sto","stop"]:
            con_move.ptz.Stop({'ProfileToken': con_move.moverequest.ProfileToken})
            con_move.active = False
        else:
            print("What are you asking?\tI only know, 'up','down','left','right', 'ul' (up left), \n\t\t\t'ur' (up right), 'dl' (down left), 'dr' (down right) and 'stop'")
            return jsonify({"message": False}), 400    
        return jsonify({"message": True}), 200 # Result True or False
    elif mtype == "abs":
        # Absolute move
        if not request.is_json:
            return jsonify({"message": False}), 400    
        data = request.get_json()
        pan  = data["pan"]
        tilt = data["tilt"]
        # Zoom position
        zoom = data["zoom"]
        abs_move.custom_move(pan, tilt, zoom)
        return jsonify({"message": True}), 200 # Result True or False
    elif mtype == "rel":
        # Relative move
        if not request.is_json:
            return jsonify({"message": False}), 400    
        data = request.get_json()
        pan  = data["pan"]
        tilt = data["tilt"]
        zoom = data["zoom"]
        rel_move.custom_move(pan, tilt, zoom)
        return jsonify({"message": True}), 200 # Result True or False
    elif mtype == "rel_c":
        # Relative move with pre-defined point
        if not request.is_json:
            return jsonify({"message": False}), 400
        data = request.get_json()
        x, y = data["x"], data["y"]
        rel_move.point_move(x, y)
        return jsonify({"message": True}), 200 # Result True or False
    else:
        return jsonify({"message": False}), 400

@app.route('/get_loc')
def get_ptz_position():
    position = rel_move.get_cur_position()
    return jsonify(position), 200
