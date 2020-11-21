import pyrealsense2 as rs

ctx = rs.context()
devices = ctx.query_devices()
print(devices)