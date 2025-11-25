"""
Camera Interface for Project 2 - Air Drawing
Handles video capture from OAKD Lite camera or webcam fallback
"""
import cv2
import numpy as np

# Try to import depthai, but make it optional for laptop testing
try:
    import depthai as dai
    DEPTHAI_AVAILABLE = True
except ImportError:
    DEPTHAI_AVAILABLE = False


class Camera:
    def __init__(self, use_oakd=True, fallback_camera_id=0):
        """
        Initialize the camera
        
        Args:
            use_oakd: If True, try to use OAKD camera first
            fallback_camera_id: Camera ID to use if OAKD is not available
        """
        self.pipeline = None
        self.device = None
        self.rgb_queue = None
        self.use_oakd = use_oakd
        self.fallback_camera = None
        self.using_fallback = False
        self.setup_pipeline()
    
    def setup_pipeline(self):
        """Set up the camera pipeline"""
        if self.use_oakd and DEPTHAI_AVAILABLE:
            try:
                # Create pipeline
                self.pipeline = dai.Pipeline()
                
                # Define source and output
                cam_rgb = self.pipeline.create(dai.node.ColorCamera)
                xout_rgb = self.pipeline.create(dai.node.XLinkOut)
                
                xout_rgb.setStreamName("rgb")
                
                # Properties
                cam_rgb.setPreviewSize(640, 480)
                cam_rgb.setInterleaved(False)
                cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
                
                # Linking
                cam_rgb.preview.link(xout_rgb.input)
                
                # Connect to device and start pipeline
                self.device = dai.Device(self.pipeline)
                self.rgb_queue = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
                print("OAKD Lite camera initialized successfully")
                return
            except Exception as e:
                print(f"Warning: Could not initialize OAKD camera: {e}")
                print("Falling back to regular webcam...")
        
        # Fallback to regular webcam
        self.fallback_camera = cv2.VideoCapture(0)
        if not self.fallback_camera.isOpened():
            raise RuntimeError("Could not open any camera (OAKD or webcam)")
        self.fallback_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.fallback_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.using_fallback = True
        print("Using fallback webcam")
    
    def get_frame(self):
        """
        Get a frame from the camera
        
        Returns:
            numpy.ndarray: BGR frame, or None if no frame available
        """
        if self.using_fallback:
            if self.fallback_camera is None:
                return None
            ret, frame = self.fallback_camera.read()
            return frame if ret else None
        
        if self.rgb_queue is None:
            return None
        
        in_rgb = self.rgb_queue.tryGet()
        if in_rgb is not None:
            frame = in_rgb.getCvFrame()
            # Convert RGB to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return frame
        return None
    
    def release(self):
        """Release camera resources"""
        if self.using_fallback:
            if self.fallback_camera:
                self.fallback_camera.release()
        else:
            if self.device:
                del self.device
            self.pipeline = None
            self.rgb_queue = None

