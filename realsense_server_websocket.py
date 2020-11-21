import asyncio
import json
from threading import Lock, Thread
from time import time

import pyrealsense2 as rs
import numpy as np
import websockets

last_depth = None
lock = Lock()

ctx = rs.context()
connected_devices = []

for i in range(len(ctx.devices)):
  print(ctx.devices[i])
  camera = ctx.devices[i].get_info(rs.camera_info.serial_number)
  connected_devices.append(camera)

def get_frame_in_background(device_sn):
  print(device_sn)
  pipeline = rs.pipeline()
  config = rs.config()
  config.enable_device(device_sn)
  config.enable_stream(rs.stream.depth, 480, 270, rs.format.z16, 6)
  pipeline.start(config)
  frames = pipeline.wait_for_frames()
  frames.keep()
  depth = frames.get_depth_frame()
  depth.keep()
  depthData = depth.as_frame().get_data()
  depthMat = np.asanyarray(depthData)
  print(depthMat)

print(connected_devices)
Thread(target=get_frame_in_background, args=(connected_devices[0],)).start()

async def websocket_reply(websocket, path):
  received = await websocket.recv()
  print(received)

start_server = websockets.serve(websocket_reply, "localhost", 8787)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()



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


