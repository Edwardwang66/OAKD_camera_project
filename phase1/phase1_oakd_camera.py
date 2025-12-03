"""
Enhanced OAK-D Camera with Depth Support
Provides RGB frames and depth maps for distance estimation
"""
import cv2
import numpy as np

# Try to import depthai
try:
    import depthai as dai
    DEPTHAI_AVAILABLE = True
except ImportError:
    DEPTHAI_AVAILABLE = False
    print("Note: DepthAI not available. Will use webcam fallback.")


class Phase1OAKDCamera:
    """
    Enhanced OAK-D camera with RGB and depth support
    """
    def __init__(self, use_oakd=True, fallback_camera_id=0):
        """
        Initialize the OAK-D camera with depth support
        
        Args:
            use_oakd: If True, try to use OAKD camera first
            fallback_camera_id: Camera ID to use if OAKD is not available
        """
        self.pipeline = None
        self.device = None
        self.rgb_queue = None
        self.depth_queue = None
        self.use_oakd = use_oakd
        self.fallback_camera_id = fallback_camera_id
        self.fallback_camera = None
        self.using_fallback = False
        self.has_depth = False
        
        self.setup_pipeline()
    
    def setup_pipeline(self):
        """Set up DepthAI pipeline for RGB and depth capture"""
        if self.use_oakd and DEPTHAI_AVAILABLE:
            try:
                # Create pipeline
                self.pipeline = dai.Pipeline()
                
                # Create RGB camera
                cam_rgb = self.pipeline.create(dai.node.ColorCamera)
                cam_rgb.setPreviewSize(640, 480)
                cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
                cam_rgb.setInterleaved(False)
                cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
                
                # Create mono cameras for depth
                mono_left = self.pipeline.create(dai.node.MonoCamera)
                mono_right = self.pipeline.create(dai.node.MonoCamera)
                
                mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
                mono_left.setBoardSocket(dai.CameraBoardSocket.LEFT)
                mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
                mono_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
                
                # Create stereo depth node
                stereo = self.pipeline.create(dai.node.StereoDepth)
                # Try different preset modes based on DepthAI version
                try:
                    # Try HIGH_DENSITY first (newer versions)
                    stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
                except AttributeError:
                    try:
                        # Fallback to HIGH_ACCURACY (older versions)
                        stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_ACCURACY)
                    except AttributeError:
                        # If neither works, use default settings
                        print("Warning: Could not set preset mode, using default settings")
                
                stereo.setLeftRightCheck(True)
                stereo.setSubpixel(False)
                stereo.setExtendedDisparity(False)
                
                # Create output nodes
                xout_rgb = self.pipeline.create(dai.node.XLinkOut)
                xout_rgb.setStreamName("rgb")
                
                xout_depth = self.pipeline.create(dai.node.XLinkOut)
                xout_depth.setStreamName("depth")
                
                # Linking
                cam_rgb.preview.link(xout_rgb.input)
                mono_left.out.link(stereo.left)
                mono_right.out.link(stereo.right)
                stereo.depth.link(xout_depth.input)
                
                # Connect to device and start pipeline
                self.device = dai.Device(self.pipeline)
                self.rgb_queue = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
                self.depth_queue = self.device.getOutputQueue(name="depth", maxSize=4, blocking=False)
                
                self.has_depth = True
                self.using_fallback = False
                print("OAK-D camera with depth initialized successfully")
                return
                
            except Exception as e:
                print(f"Warning: Could not initialize OAK-D camera: {e}")
                print("Falling back to regular webcam...")
        
        # Fallback to regular webcam (no depth)
        self.fallback_camera = cv2.VideoCapture(self.fallback_camera_id)
        if not self.fallback_camera.isOpened():
            raise RuntimeError("Could not open any camera (OAK-D or webcam)")
        self.fallback_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.fallback_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.using_fallback = True
        self.has_depth = False
        print("Using fallback webcam (no depth support)")
    
    def get_frame(self):
        """
        Get a RGB frame from the camera
        
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
    
    def get_depth_frame(self):
        """
        Get a depth frame from the camera
        
        Returns:
            numpy.ndarray: Depth frame (16-bit), or None if no depth available
        """
        if not self.has_depth or self.depth_queue is None:
            return None
        
        in_depth = self.depth_queue.tryGet()
        if in_depth is not None:
            depth_frame = in_depth.getFrame()
            return depth_frame
        return None
    
    def get_distance_at_point(self, x, y, depth_frame=None, patch_size=10):
        """
        Get distance at a specific point in the frame
        
        Args:
            x: X coordinate
            y: Y coordinate
            depth_frame: Optional depth frame (if None, will get from camera)
            patch_size: Size of patch to average over (default 10x10)
            
        Returns:
            float: Distance in meters, or None if unavailable
        """
        if depth_frame is None:
            depth_frame = self.get_depth_frame()
        
        if depth_frame is None:
            return None
        
        h, w = depth_frame.shape[:2]
        
        # Ensure coordinates are within bounds
        x = max(0, min(w - 1, int(x)))
        y = max(0, min(h - 1, int(y)))
        
        # Calculate patch bounds
        half_patch = patch_size // 2
        x_min = max(0, x - half_patch)
        x_max = min(w, x + half_patch)
        y_min = max(0, y - half_patch)
        y_max = min(h, y + half_patch)
        
        # Extract patch and calculate average depth
        patch = depth_frame[y_min:y_max, x_min:x_max]
        
        # Filter out invalid depth values (0 or very large)
        valid_depths = patch[patch > 0]
        if len(valid_depths) == 0:
            return None
        
        # Average depth in millimeters, convert to meters
        avg_depth_mm = np.mean(valid_depths)
        distance_m = avg_depth_mm / 1000.0
        
        return distance_m
    
    def get_distance_from_bbox(self, bbox, depth_frame=None):
        """
        Get distance at the center of a bounding box
        
        Args:
            bbox: Bounding box (x_min, y_min, x_max, y_max)
            depth_frame: Optional depth frame (if None, will get from camera)
            
        Returns:
            float: Distance in meters, or None if unavailable
        """
        if bbox is None:
            return None
        
        x_min, y_min, x_max, y_max = bbox
        
        # Calculate center of bounding box
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        
        return self.get_distance_at_point(center_x, center_y, depth_frame)
    
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
            self.depth_queue = None

