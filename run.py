# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-20 09:21:34
# @Last Modified time: 2022-01-21 09:31:50
import sys
import json
import argparse
import subprocess as sp

from app import app

def get_parser():
	parser = argparse.ArgumentParser('PTZ-controller')
	parser.add_argument('--encode-app',
						 '-ea',
						 nargs='?',
						 choices=['gstreamer', 'ffmpeg'],
						 default='ffmpeg',
						 const='ffmpeg',
						 help='Application used to read, encode and generate hls stream'
						 )
	return parser

# start flask app
if __name__ == '__main__':

	with open("config.json", "r") as f:
			config = json.load(f)

	rtsp_str = config["rtsp_link"]

	parser = get_parser()
	args = parser.parse_args()

	hls_dir = "app/static/hls/"

	if args.encode_app == 'ffmpeg':
		print("FFMPEG is selected as encoding app")
		# Init FFMPEG player to convert RTSP stream to HLS
		# https://girishjoshi.io/post/ffmpeg-rtsp-to-hls/
		command = ['ffmpeg', '-threads', '4',
				   '-rtsp_transport', 'udp',
				   '-i', rtsp_str,
				   '-c:v', 'libx264',
				   '-x264opts', 'keyint=30:min-keyint=30:scenecut=-1',
				   '-tune', "zerolatency",
				   '-deadline', 'realtime',
				   '-b:v', '1400k',
				   '-bufsize', '1400k',
				   '-an',
				   '-hls_flags', 'delete_segments+append_list',
				   '-f', 'segment',
				   '-segment_wrap', '60',
				   '-segment_list_flags', 'live',
				   '-segment_time', '0.5',
				   '-segment_list_size', '1',
				   '-segment_format', 'mpegts',
				   '-segment_list', '%sindex.m3u8' %hls_dir,
				   '-segment_list_type', 'm3u8',
				   '-segment_list_entry_prefix', hls_dir,
				   '{}/%3d.ts'.format(hls_dir)
				]
	else:
		print("Gstreamer is selected as encoding app")
		command = ['gst-launch-1.0', '-v'
				   'rtspsrc=%s' %rtsp_str,
				   '!', 'rtph264depay',
				   '!', 'nvv4lh264enc', 'max-performace=1',
				   '!', 'nvvidconv',
				   '!', 'videoconvert',
				   '!', 'mpegtsmux',
				   '!', 'hlssink',
				   'location=%s' %hls_dir,
				   'max-files=60',
				   'target-duration=5']

	proc = sp.Popen(command, stdout=sp.DEVNULL, stderr=sp.PIPE)
	app.run(host="0.0.0.0", port=5000, debug=False)
