import pyrealsense2 as rs
import numpy as np
import cv2
import logging
import time

realsense_ctx = rs.context()  # The context encapsulates all of the devices and sensors, and provides some additional functionalities.
connected_devices = []

# get serial numbers of connected devices:
for i in range(len(realsense_ctx.devices)):
    detected_camera = realsense_ctx.devices[i].get_info(
        rs.camera_info.serial_number)
    connected_devices.append(detected_camera)
    print(detected_camera)
pipelines = []
configs = []
for i in range(len(realsense_ctx.devices)):
    pipelines.append(rs.pipeline())  # one pipeline for each device
    configs.append(rs.config())      # one config for each device
    configs[i].enable_device(connected_devices[i])
    configs[i].enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 30)
    pipelines[i].start(configs[i])

try:
    while True:
        images = []
        for i in range(len(pipelines)):
            print("waiting for frame at cam", i)
            frames = pipelines[i].wait_for_frames()
            color_frame = frames.get_color_frame()
            images.append(np.asanyarray(color_frame.get_data()))

        # Stack all images horizontally
        image_composite = images[0]
        for i in range(1, len(images)):
            images_composite = np.hstack((image_composite, images[i]))

        # Show images from both cameras
        cv2.namedWindow('RealSense', cv2.WINDOW_NORMAL)
        cv2.imshow('RealSense', images_composite)

        cv2.waitKey(20)

finally:
    for i in range(len(pipelines)):
        pipelines[i].stop()

