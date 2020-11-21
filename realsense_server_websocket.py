import asyncio
import pathlib
import json
from threading import Lock, Thread
from time import time

import pyrealsense2 as rs
import numpy as np
import websockets
import ssl

last_depth = None
lock = Lock()

filters = []
decimate = rs.decimation_filter()
decimate.set_option(rs.option.filter_magnitude, 2)
filters.append(decimate)
filters.append(rs.temporal_filter())
filters.append(rs.hole_filling_filter(2))

ctx = rs.context()
connected_devices = []

for i in range(len(ctx.devices)):
  print(ctx.devices[i])
  camera = ctx.devices[i].get_info(rs.camera_info.serial_number)
  connected_devices.append(camera)

def get_frame_in_background(device_sn):
  # print(device_sn)
  pipeline = rs.pipeline()
  config = rs.config()
  config.enable_device(device_sn)
  config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 6)
  pipeline.start(config)
  while True:
    global last_depth, lock
    time_start = time()
    frames = pipeline.wait_for_frames()
    frames.keep()
    depth = frames.get_depth_frame()
    for filter in filters:
      depth = filter.process(depth)
    depth.keep()
    depthData = depth.as_frame().get_data()
    # print(len(depthData))
    depthMat = np.asanyarray(depthData)[200:300].tolist()
    # print(len(depthMat))
    lock.acquire()
    last_depth = depthMat
    lock.release()
    # print ('Last frame processing took = %3i ms\r' %  (((time()-time_start) * 1000)) , end='' )

# print(connected_devices)
Thread(target=get_frame_in_background, args=(connected_devices[1],)).start()

# async def websocket_reply(websocket, path):
#   await websocket.recv()
#   time_start = time()
#   lock.acquire()
#   result = last_depth
#   lock.release()
#   await websocket.send(json.dumps(result))
#   print ('Retrieval Processing Time = %i ms' %  (((time()-time_start) * 1000)) )

async def ws_loop(websocket, path):
  print(path)
  while True:
    lock.acquire()
    result = last_depth
    lock.release()
    await websocket.send(json.dumps(result))
    await asyncio.sleep(1)

  # name = await websocket.recv()
  # print(f"< {name}")

  # lock.acquire()
  # result = last_depth
  # lock.release()
  # await websocket.send(json.dumps(result))

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
server_pem = pathlib.Path(__file__).with_name("server.pem")
ssl_context.load_cert_chain(server_pem)

start_server = websockets.serve(ws_loop, port=8080, ssl=ssl_context)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

