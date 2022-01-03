# -*- coding: utf-8 -*-
# @Author: Bao
# @Date:   2021-08-20 09:21:34
# @Last Modified by:   Bao
# @Last Modified time: 2021-08-20 09:58:58
import json
import subprocess as sp
from app import app

# start flask app
if __name__ == '__main__':

		with open("config.json", "r") as f:
				config = json.load(f)

		rtsp_str = config["rtsp_link"]
		# Init FFMPEG player to convert RTSP stream to HLS
		# https://girishjoshi.io/post/ffmpeg-rtsp-to-hls/
		hls_dir = "app/static/hls/"
		command = ['ffmpeg', '-fflags', 'nobuffer',
				   '-rtsp_transport', 'udp',
				   '-i', rtsp_str,
				   '-vsync', '0',
				   '-copyts',
				   '-vcodec', "copy",
				   '-movflags', 'frag_keyframe+empty_moov',
				   '-an',
				   '-hls_flags', 'delete_segments+append_list',
				   '-f', 'segment',
				   '-reset_timestamps', '1',
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
		proc = sp.Popen(command, stdout=sp.DEVNULL, stderr=sp.STDOUT)
		app.run(host="0.0.0.0", port=5000, debug=False)
