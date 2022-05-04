import pyrealsense2.pyrealsense2 as rs
import numpy as np

from threading import Thread
import cv2
import time

#class to pipe camera frames from a seperate thread
class cameraStream:
    #Initializes camera pipeline/configuration and begins to collect frames on a seperate thread
    def __init__(self, x, y):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        # Get device product line for setting a supporting resolution
        self.pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        self.pipeline_profile = self.config.resolve(self.pipeline_wrapper)
        self.cam_device = self.pipeline_profile.get_device()
        self.device_product_line = str(self.cam_device.get_info(rs.camera_info.product_line))
        

        self.config.enable_stream(rs.stream.depth, x, y, rs.format.z16, 30)

        if self.device_product_line == 'L500':
            self.config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
        else:
            self.config.enable_stream(rs.stream.color, x, y, rs.format.bgr8, 30)

        # Start streaming
        self.pipeline.start(self.config)

        self.frame = self.pipeline.wait_for_frames()
        align = rs.align(rs.stream.color)
        self.frame = align.process(self.frame)
        self.depth_frame = self.frame.get_depth_frame()
        self.color_frame = self.frame.get_color_frame()
        self.depth_intrin = self.depth_frame.profile.as_video_stream_profile().intrinsics
        self.color_intrin = self.color_frame.profile.as_video_stream_profile().intrinsics

        self.thread = Thread(target=self.update)
        self.thread.start()

    def getFOV(self):
        return (self.depth_intrin.fx, self.depth_intrin.fy)

    #Update frame function to run on sepereate thread
    def update(self):
        #frame = self.frame

        while True:
            frame = self.pipeline.wait_for_frames()
            align = rs.align(rs.stream.color)
            frame = align.process(frame)
            self.depth_frame = frame.get_depth_frame()
            self.color_frame = frame.get_color_frame()
            if not self.depth_frame or not self.color_frame:
                continue
            


    def __iter__(self):
        self.count = -1;
        return self

    #Class iterator
    #Returns: color_image (RGB) image with channels corrected for yolo
    #         color_image_copy (BGR) image to display and label bounding boxes onto
    #         depth_frame that has been aligned with color_image to get depth information from any specific pixel
    def __next__(self):
        self.count += 1

        # Convert images to numpy arrays
        depth_image = np.asanyarray(self.depth_frame.get_data())
        color_image = np.asanyarray(self.color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape

        # If depth and color resolutions are different, resize color image to match depth image for display
        if depth_colormap_dim != color_colormap_dim:
            print(f'Resizing color image')
            color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)

        color_image_copy = color_image.copy()
        color_image = np.einsum('ijk->kij',color_image)  # BGR to RGB, BHWC to BCHW
        

        return color_image, color_image_copy, self.depth_frame

    def kill(self):
        self.pipeline.stop()
        self.thread.join()
        raise KeyboardInterrupt
