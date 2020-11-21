import asyncio
import json
from threading import Lock, Thread
from time import time

import pyrealsense2 as rs

last_depth = None
lock = Lock()

ctx = rs.context()
connected_devices = []

for i in range(len(ctx.devices)):
  print(devices[i])
  camera = ctx.devices[i].get_info(rs.camera_info.serial_number)
  connected_devices.append(camera)

def get_frame_in_background(device_sn):
  pipeline = rs.pipeline()
  config = rs.config()
  config.enable_device(device_sn)
  config.enable_stream(rs.stream.depth, 424, 240, rs.format.z16, 6)
  pipeline.start(config)
  frames = pipeline.wait_for_frames()
  depth = frames.get_depth_frame()
  print(depth)

print(connected_devices)
Thread(target=thread_function, args=(connected_devices[0],)).start()

# def get_frame_in_background(device_sn):
#   pipeline = rs.pipeline()
#   config = rs.config()
#   config.enable_device(device_sn)
#   config.enable_stream(rs.stream.depth, 424, 240, rs.format.z16, 6)
#   pipeline.start(config)
#   while True:
#     global last_depth, lock
#     time_start = time()
#     # Get Frame and apply filters
#     frames = pipeline.wait_for_frames()
#     # frames = device_manager.poll_frames()
#     depth = frames.get_depth_frame()
#     # for filter in filters:
#       # depth = filter.process(depth)


