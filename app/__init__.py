# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-20 08:48:59
# @Last Modified by:   Bao
# @Last Modified time: 2021-08-20 10:01:10
from flask import Flask, request, jsonify, render_template
from app.ptz.con_move import *
from onvif import ONVIFCamera

mycam = ONVIFCamera('172.16.0.108', 80, 'onvif', 'vnnet123456')
# Create media service object
media = mycam.create_media_service()
# Create ptz service object
ptz = mycam.create_ptz_service()

# Get target profile
media_profile = media.GetProfiles()[0]

con_move = ContinouseMove(ptz, media_profile)

# Initialize the Flask application
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

# route http posts to this method
@app.route('/direct', methods=['POST'])
def verify():
    lov = request.args.get("d")
    print(lov)
    if lov:
        if lov[0].lower() in ["u","up"]:
            con_move.move_up()
        elif lov[0].lower() in ["s","st","sto","stop"]:
            ptz.Stop({'ProfileToken': moverequest.ProfileToken})
            active = False
        else:
            print("What are you asking?\tI only know, 'up','down','left','right', 'ul' (up left), \n\t\t\t'ur' (up right), 'dl' (down left), 'dr' (down right) and 'stop'")
            return jsonify({"message": False}), 400    
        return jsonify({"message": True}), 200 # Result True or False
    else:
        return jsonify({"message": False}), 400