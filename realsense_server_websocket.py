import pyrealsense2 as rs

ctx = rs.context()
connected_devices = []

for i in range(len(ctx.devices)):
  camera = ctx.devices[i].get_info(rs.camera_info.serial_number)
  connected_devices.append(camera)

print(connected_devices)