#!/usr/bin/python3
import pyrealsense2 as rs
import numpy as np
import cv2
import copy
import math


import jetson.inference
import jetson.utils
from depthnet_utils import depthBuffers
import argparse
import sys

class ARC:
    def __init__(self):
       
        # parse the command line
        parser = argparse.ArgumentParser(description="Mono depth estimation on a video/image stream using depthNet DNN.", 
                                         formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.depthNet.Usage() +
                                         jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage())

        parser.add_argument("input_URI", type=str, default="", nargs='?', help="URI of the input stream")
        parser.add_argument("output_URI", type=str, default="", nargs='?', help="URI of the output stream")
        parser.add_argument("--network", type=str, default="fcn-mobilenet", help="pre-trained model to load, see below for options")
        parser.add_argument("--visualize", type=str, default="input,depth", help="visualization options (can be 'input' 'depth' 'input,depth'")
        parser.add_argument("--depth-size", type=float, default=1.0, help="scales the size of the depth map visualization, as a percentage of the input size (default is 1.0)")
        parser.add_argument("--filter-mode", type=str, default="linear", choices=["point", "linear"], help="filtering mode used during visualization, options are:\n  'point' or 'linear' (default: 'linear')")
        parser.add_argument("--colormap", type=str, default="viridis-inverted", help="colormap to use for visualization (default is 'viridis-inverted')",
                                          choices=["inferno", "inferno-inverted", "magma", "magma-inverted", "parula", "parula-inverted", 
                                                   "plasma", "plasma-inverted", "turbo", "turbo-inverted", "viridis", "viridis-inverted"])

        try:
            opt = parser.parse_known_args()[0]
        except:
            print("")
            parser.print_help()
            sys.exit(0)        
            
        # load the segmentation network
        net = jetson.inference.depthNet(opt.network, sys.argv)

        # create buffer manager
        self.buffers = depthBuffers(opt)
        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))

        found_rgb = False
        for s in device.sensors:
            if s.get_info(rs.camera_info.name) == 'RGB Camera':
                found_rgb = True
                break
        if not found_rgb:
            print("The demo requires Depth camera with Color sensor")
            exit(0)

        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        if device_product_line == 'L500':
            config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
        else:
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        # Start streaming
        self.pipeline.start(config)

    def video(self):
        align_to = rs.stream.color
        align = rs.align(align_to)
        for i in range(10):
            self.pipeline.wait_for_frames()
            
        while True:
            frames = self.pipeline.wait_for_frames()
          
            aligned_frames = align.process(frames)
            

            #################
            img_input = aligned_frames.get_color_frame()
            # allocate buffers for this size image
            self.buffers.Alloc(img_input.shape, img_input.format)

            # process the mono depth and visualize
            net.Process(img_input, self.buffers.depth, opt.colormap, opt.filter_mode)
            #################            
            
            
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()

            self.depth_frame = depth_frame

            color_image = np.asanyarray(color_frame.get_data())
            self.color_intrin = color_frame.profile.as_video_stream_profile().intrinsics

            depth_color_frame = rs.colorizer().colorize(depth_frame)

            # Convert depth_frame to numpy array to render image in opencv
            depth_color_image = np.asanyarray(depth_color_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            self.show(color_cvt)

            break
            # Render image in opencv window
            # Create opencv window to render image in


    def show(self, img):
        self.img_origin = img
        self.img_copy = copy.copy(self.img_origin)
        cv2.namedWindow("Color Stream", cv2.WINDOW_AUTOSIZE)

        cv2.setMouseCallback("Color Stream", self.draw)
        while True:
            cv2.imshow("Color Stream", self.img_copy)
            key = cv2.waitKey(10)
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break

    def draw(self, event,x,y,flags,params):
        img = copy.copy(self.img_copy)
        
        #print event,x,y,flags,params
        if(event==1):
            self.ix = x
            self.iy = y
        elif event == 4:
            img = self.img_copy
            self.img_work(img, x,y)
        elif event == 2:
            self.img_copy = copy.copy(self.img_origin)
        elif(flags==1):
            self.img_work(img,x,y)
            cv2.imshow("Color Stream", img)

    def img_work(self, img,x,y):
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        fontColor = (0, 0, 0)
        lineType = 2

        length = self.calculate_length(x, y)
        depth = self.get_depth_meter(x, y)
        
        if length > 0:
            cv2.line(img, pt1=(self.ix, self.iy), pt2=(x, y), color=(255, 255, 255), thickness=1)
            cv2.rectangle(img, (self.ix, self.iy), (self.ix + 80, self.iy - 20), (255, 255, 255), -1)            
            cv2.putText(img, '{0:.5}'.format(length), (self.ix, self.iy), font, fontScale, fontColor, lineType)
        else :    
            cv2.line(img, pt1=(self.ix, self.iy), pt2=(x, y), color=(255, 255, 255), thickness=1)
            cv2.rectangle(img, (self.ix, self.iy), (self.ix + 80, self.iy - 20), (255, 255, 255), -1)     
            cv2.putText(img, '{:0.2f}'.format(depth), (self.ix, self.iy), font, fontScale, fontColor, lineType)       

    def get_depth_meter(self,x,y):
        ix,iy = self.ix, self.iy
        depth = self.depth_frame.get_distance(ix,iy)
        print(f"Coordinates from top-left: x: {ix}, y: {iy}")
        print("Depth {:0.2f} meter".format(depth))
        return depth       

    def calculate_length(self,x,y):
        color_intrin = self.color_intrin
        ix,iy = self.ix, self.iy
        udist = self.depth_frame.get_distance(ix,iy)
        vdist = self.depth_frame.get_distance(x, y)
        point1 = rs.rs2_deproject_pixel_to_point(color_intrin, [ix, iy], udist)
        point2 = rs.rs2_deproject_pixel_to_point(color_intrin, [x, y], vdist)
        length = math.sqrt(
            math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1],2) + math.pow(
                point1[2] - point2[2], 2))
        return length


if __name__ == '__main__':
    ARC().video()
