"""
OAKD Edge AI Camera Interface
Uses OAKD camera's built-in Myriad X VPU for hand detection and gesture classification
Runs hand detection and model inference directly on the camera
"""
import cv2
import numpy as np
import os

# Try to import depthai
try:
    import depthai as dai
    DEPTHAI_AVAILABLE = True
except ImportError:
    DEPTHAI_AVAILABLE = False
    print("Note: DepthAI not available. Edge AI features disabled.")


class OAKDEdgeAICamera:
    def __init__(self, model_blob_path=None, use_hand_detection=True):
        """
        Initialize OAKD camera with Edge AI capabilities
        
        Args:
            model_blob_path: Path to .blob model file for gesture classification
                           If None, will use hand detection only
            use_hand_detection: Whether to use built-in hand detection
        """
        self.pipeline = None
        self.device = None
        self.rgb_queue = None
        self.nn_queue = None
        self.hand_detection_queue = None
        self.model_blob_path = model_blob_path
        self.use_hand_detection = use_hand_detection
        self.use_edge_ai = model_blob_path is not None
        
        if not DEPTHAI_AVAILABLE:
            raise RuntimeError("DepthAI not available. Cannot use Edge AI features.")
        
        self.setup_pipeline()
    
    def setup_pipeline(self):
        """Set up DepthAI pipeline with hand detection and/or neural network"""
        try:
            self.pipeline = dai.Pipeline()
            
            # RGB Camera
            cam_rgb = self.pipeline.create(dai.node.ColorCamera)
            cam_rgb.setPreviewSize(640, 480)
            cam_rgb.setInterleaved(False)
            cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
            
            # Hand Detection (using MediaPipe hand detection model)
            if self.use_hand_detection:
                # Create hand detection network
                hand_nn = self.pipeline.create(dai.node.NeuralNetwork)
                
                # Use MediaPipe hand detection blob (if available)
                # For now, we'll use a simpler approach with ImageManip
                # You can load a hand detection blob model here
                hand_detection_in = self.pipeline.create(dai.node.XLinkIn)
                hand_detection_out = self.pipeline.create(dai.node.XLinkOut)
                hand_detection_in.setStreamName("hand_detection_in")
                hand_detection_out.setStreamName("hand_detection_out")
                
                # For hand detection, we'll use ImageManip to crop regions
                # and pass to neural network
                manip = self.pipeline.create(dai.node.ImageManip)
                manip.initialConfig.setResize(256, 256)  # Resize for hand detection
                manip.initialConfig.setFrameType(dai.ImgFrame.Type.RGB888p)
                
                cam_rgb.preview.link(manip.inputImage)
                manip.out.link(hand_detection_in.input)
            
            # Gesture Classification Neural Network (if blob provided)
            if self.use_edge_ai and self.model_blob_path:
                if not os.path.exists(self.model_blob_path):
                    print(f"Warning: Model blob not found at {self.model_blob_path}")
                    print("Falling back to hand detection only")
                    self.use_edge_ai = False
                else:
                    # Create neural network node
                    gesture_nn = self.pipeline.create(dai.node.NeuralNetwork)
                    gesture_nn.setBlobPath(self.model_blob_path)
                    gesture_nn.setNumInferenceThreads(2)
                    
                    # Create input for cropped hand regions
                    nn_input = self.pipeline.create(dai.node.XLinkIn)
                    nn_input.setStreamName("nn_input")
                    
                    # Create output
                    nn_output = self.pipeline.create(dai.node.XLinkOut)
                    nn_output.setStreamName("nn_output")
                    
                    nn_input.out.link(gesture_nn.input)
                    gesture_nn.out.link(nn_output.input)
            
            # RGB output
            xout_rgb = self.pipeline.create(dai.node.XLinkOut)
            xout_rgb.setStreamName("rgb")
            cam_rgb.preview.link(xout_rgb.input)
            
            # Connect device
            self.device = dai.Device(self.pipeline)
            self.rgb_queue = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            
            if self.use_edge_ai:
                self.nn_input = self.device.getInputQueue("nn_input", maxSize=1, blocking=False)
                self.nn_queue = self.device.getOutputQueue(name="nn_output", maxSize=4, blocking=False)
            
            print("OAKD Edge AI camera initialized successfully")
            if self.use_edge_ai:
                print(f"  - Edge AI model: {self.model_blob_path}")
            if self.use_hand_detection:
                print("  - Hand detection: Enabled")
        
        except Exception as e:
            print(f"Error initializing OAKD Edge AI camera: {e}")
            raise
    
    def get_frame_with_detection(self):
        """
        Get frame with hand detection bounding boxes
        
        Returns:
            tuple: (frame, hand_bboxes, nn_results)
                - frame: BGR image frame
                - hand_bboxes: List of (x, y, w, h) bounding boxes
                - nn_results: Neural network inference results (if available)
        """
        if self.rgb_queue is None:
            return None, [], None
        
        in_rgb = self.rgb_queue.tryGet()
        if in_rgb is None:
            return None, [], None
        
        frame = in_rgb.getCvFrame()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        hand_bboxes = []
        nn_results = None
        
        # Get neural network results if available
        if self.use_edge_ai and self.nn_queue:
            nn_data = self.nn_queue.tryGet()
            if nn_data:
                # Parse neural network output
                nn_results = self._parse_nn_output(nn_data)
        
        # For now, hand detection bboxes would come from a hand detection model
        # This is a placeholder - you would integrate a hand detection blob here
        # For now, we'll return empty bboxes and let MediaPipe handle it
        
        return frame_bgr, hand_bboxes, nn_results
    
    def _parse_nn_output(self, nn_data):
        """
        Parse neural network output
        
        Args:
            nn_data: Neural network output data
            
        Returns:
            dict: Parsed results with gesture classification
        """
        # Get output layer
        output = nn_data.getLayerFp16("output")  # or getLayerInt8, getLayerUInt8
        
        # Assuming output is [rock_prob, paper_prob, scissors_prob]
        if len(output) >= 3:
            return {
                'rock': output[0],
                'paper': output[1],
                'scissors': output[2],
                'predicted': np.argmax(output)
            }
        return None
    
    def send_hand_region_to_nn(self, bbox):
        """
        Send cropped hand region to neural network for classification
        
        Args:
            bbox: Bounding box (x, y, w, h) of hand region
        """
        if not self.use_edge_ai or self.nn_input is None:
            return
        
        # This would send the cropped region to the NN
        # Implementation depends on your specific setup
        pass
    
    def get_frame(self):
        """
        Get a frame from the camera (compatibility method)
        
        Returns:
            numpy.ndarray: BGR frame, or None if no frame available
        """
        frame, _, _ = self.get_frame_with_detection()
        return frame
    
    def release(self):
        """Release camera resources"""
        if self.device:
            del self.device
        self.pipeline = None
        self.rgb_queue = None
        self.nn_queue = None


# Simplified version using hand detection with bounding boxes
class OAKDHandDetectionCamera:
    """
    Simplified OAKD camera with hand detection bounding boxes
    Uses MediaPipe on host for hand detection, but optimized for OAKD
    """
    def __init__(self):
        """Initialize OAKD camera optimized for hand detection"""
        self.pipeline = None
        self.device = None
        self.rgb_queue = None
        
        if not DEPTHAI_AVAILABLE:
            raise RuntimeError("DepthAI not available.")
        
        self.setup_pipeline()
    
    def setup_pipeline(self):
        """Set up simple RGB pipeline"""
        try:
            self.pipeline = dai.Pipeline()
            
            cam_rgb = self.pipeline.create(dai.node.ColorCamera)
            xout_rgb = self.pipeline.create(dai.node.XLinkOut)
            
            xout_rgb.setStreamName("rgb")
            
            cam_rgb.setPreviewSize(640, 480)
            cam_rgb.setInterleaved(False)
            cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
            
            cam_rgb.preview.link(xout_rgb.input)
            
            self.device = dai.Device(self.pipeline)
            self.rgb_queue = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            
            print("OAKD camera initialized (hand detection ready)")
        
        except Exception as e:
            print(f"Error initializing OAKD camera: {e}")
            raise
    
    def get_frame(self):
        """Get frame from camera"""
        if self.rgb_queue is None:
            return None
        
        in_rgb = self.rgb_queue.tryGet()
        if in_rgb is not None:
            frame = in_rgb.getCvFrame()
            return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return None
    
    def release(self):
        """Release resources"""
        if self.device:
            del self.device
        self.pipeline = None
        self.rgb_queue = None

