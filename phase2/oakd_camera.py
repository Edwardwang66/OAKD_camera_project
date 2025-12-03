"""
OAKD Lite Camera with Person Detection for Raspberry Pi
Integrates OAKD camera with person detection using MobileNet-SSD or MediaPipe
Designed for Raspberry Pi 5 with X11 forwarding
"""
import cv2
import numpy as np

# Try to import depthai
try:
    import depthai as dai
    DEPTHAI_AVAILABLE = True
except ImportError:
    DEPTHAI_AVAILABLE = False
    print("Error: DepthAI not available. Please install with: pip install depthai")

# Try to import mediapipe for fallback
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False


class OAKDCamera:
    """
    OAKD Lite camera with integrated person detection
    Designed for Raspberry Pi 5
    """
    def __init__(self):
        """Initialize OAKD camera with person detection"""
        self.pipeline = None
        self.device = None
        self.rgb_queue = None
        self.nn_queue = None
        self.detection_nn = None
        self.available = False
        self.use_mediapipe_fallback = False
        self.mediapipe_pose = None
        
        if not DEPTHAI_AVAILABLE:
            print("Error: DepthAI not available. Camera will not work.")
            raise RuntimeError("DepthAI not available")
        
        # Try to set up DepthAI pipeline
        try:
            self.setup_pipeline()
        except Exception as e:
            print(f"[OAKDCamera] DepthAI pipeline setup failed: {e}")
            # Try MediaPipe fallback
            if MEDIAPIPE_AVAILABLE:
                print("[OAKDCamera] Falling back to MediaPipe person detection")
                self.setup_mediapipe_fallback()
            else:
                print("[OAKDCamera] No fallback available. Camera will not work.")
                raise
    
    def setup_pipeline(self):
        """Set up DepthAI pipeline with RGB camera and person detection"""
        try:
            # Create pipeline
            self.pipeline = dai.Pipeline()
            
            # Create RGB camera
            cam_rgb = self.pipeline.create(dai.node.ColorCamera)
            cam_rgb.setPreviewSize(640, 480)  # Display size
            cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
            cam_rgb.setInterleaved(False)
            cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
            
            # Create detection network for person detection
            # Try MobileNetDetectionNetwork first (older DepthAI versions)
            # Fall back to NeuralNetwork (newer versions)
            try:
                self.detection_nn = self.pipeline.create(dai.node.MobileNetDetectionNetwork)
                use_mobilenet_node = True
            except AttributeError:
                # Use generic NeuralNetwork node (newer DepthAI versions)
                self.detection_nn = self.pipeline.create(dai.node.NeuralNetwork)
                use_mobilenet_node = False
            
            # Try to get MobileNet-SSD model
            try:
                import blobconverter
                blob_path = blobconverter.from_zoo(
                    name="mobilenet-ssd",
                    shaves=6,
                    version="2021.4"
                )
                self.detection_nn.setBlobPath(blob_path)
            except ImportError:
                print("Warning: blobconverter not available. Install with: pip install blobconverter")
                print("Person detection will be disabled.")
                raise RuntimeError("blobconverter required for person detection")
            except Exception as e:
                print(f"Warning: Could not load MobileNet-SSD model: {e}")
                raise
            
            # Set confidence threshold (only for MobileNetDetectionNetwork)
            if use_mobilenet_node:
                self.detection_nn.setConfidenceThreshold(0.5)
            self.detection_nn.input.setBlocking(False)
            
            # Create outputs
            # Try different API formats for compatibility
            try:
                xout_rgb = self.pipeline.create(dai.node.XLinkOut)
            except AttributeError:
                xout_rgb = self.pipeline.create(dai.XLinkOut)
            xout_rgb.setStreamName("rgb")
            
            try:
                xout_nn = self.pipeline.create(dai.node.XLinkOut)
            except AttributeError:
                xout_nn = self.pipeline.create(dai.XLinkOut)
            xout_nn.setStreamName("nn")
            
            # Create ImageManip to resize for detection network (300x300)
            # MobileNet-SSD expects 300x300 input
            manip = self.pipeline.create(dai.node.ImageManip)
            manip.initialConfig.setResize(300, 300)
            manip.initialConfig.setFrameType(dai.ImgFrame.Type.BGR888p)
            manip.setMaxOutputFrameSize(300 * 300 * 3)
            
            # Linking
            # Camera preview -> ImageManip -> Detection Network
            cam_rgb.preview.link(manip.inputImage)
            manip.out.link(self.detection_nn.input)
            # Camera preview -> RGB output (for display)
            cam_rgb.preview.link(xout_rgb.input)
            # Detection Network -> NN output
            self.detection_nn.out.link(xout_nn.input)
            
            # Connect to device
            self.device = dai.Device(self.pipeline)
            self.rgb_queue = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            self.nn_queue = self.device.getOutputQueue(name="nn", maxSize=4, blocking=False)
            
            self.available = True
            print("[OAKDCamera] Camera initialized successfully with DepthAI person detection")
            
        except Exception as e:
            print(f"[OAKDCamera] Error setting up DepthAI detection: {e}")
            # Try MediaPipe fallback
            if MEDIAPIPE_AVAILABLE:
                print("[OAKDCamera] Falling back to MediaPipe person detection")
                self.setup_mediapipe_fallback()
            else:
                print("[OAKDCamera] No fallback available. Camera will not work.")
                self.available = False
                raise
    
    def setup_mediapipe_fallback(self):
        """Set up OAKD camera with MediaPipe person detection fallback"""
        try:
            # Create simple RGB pipeline
            self.pipeline = dai.Pipeline()
            
            cam_rgb = self.pipeline.create(dai.node.ColorCamera)
            cam_rgb.setPreviewSize(640, 480)
            cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
            cam_rgb.setInterleaved(False)
            cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
            
            # Try different API formats for compatibility
            try:
                xout_rgb = self.pipeline.create(dai.node.XLinkOut)
            except AttributeError:
                xout_rgb = self.pipeline.create(dai.XLinkOut)
            xout_rgb.setStreamName("rgb")
            
            cam_rgb.preview.link(xout_rgb.input)
            
            self.device = dai.Device(self.pipeline)
            self.rgb_queue = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            
            # Initialize MediaPipe Pose
            self.mp_pose = mp.solutions.pose
            self.mediapipe_pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.5
            )
            
            self.use_mediapipe_fallback = True
            self.available = True
            print("[OAKDCamera] Camera initialized with MediaPipe person detection fallback")
            
        except Exception as e:
            print(f"[OAKDCamera] Error setting up MediaPipe fallback: {e}")
            self.available = False
            raise
    
    def get_frame(self):
        """
        Get a frame from the camera
        
        Returns:
            numpy.ndarray: BGR frame, or None if no frame available
        """
        if not self.available or self.rgb_queue is None:
            return None
        
        in_rgb = self.rgb_queue.tryGet()
        if in_rgb is not None:
            frame = in_rgb.getCvFrame()
            return frame
        return None
    
    def detect_person(self):
        """
        Detect person in the current frame
        
        Returns:
            tuple: (person_found, person_bbox, frame)
                - person_found: bool, True if person detected
                - person_bbox: (x_min, y_min, x_max, y_max) or None
                - frame: BGR frame with annotations
        """
        if not self.available:
            return False, None, None
        
        # Get frame
        frame = self.get_frame()
        if frame is None:
            return False, None, None
        
        annotated_frame = frame.copy()
        person_found = False
        person_bbox = None
        
        # Use MediaPipe fallback if enabled
        if self.use_mediapipe_fallback:
            return self._detect_person_mediapipe(frame)
        
        # Use DepthAI detection network
        if self.nn_queue is None:
            return False, None, annotated_frame
        
        # Get detection results
        in_nn = self.nn_queue.tryGet()
        if in_nn is not None:
            h, w = frame.shape[:2]
            
            # Handle different output formats
            try:
                # Try to get detections (MobileNetDetectionNetwork format)
                detections = in_nn.detections
                detection_format = "mobilenet"
            except AttributeError:
                # Try to get as NeuralNetwork output (tensor format)
                try:
                    detection_data = in_nn.getLayerFp16("DetectionOutput")
                    detections = self._parse_neural_network_output(detection_data)
                    detection_format = "tensor"
                except:
                    detections = []
                    detection_format = "unknown"
            
            # Find person detections (class 15 in COCO dataset)
            for detection in detections:
                # Handle different detection formats
                if detection_format == "mobilenet":
                    label = detection.label
                    confidence = detection.confidence
                    xmin = detection.xmin
                    ymin = detection.ymin
                    xmax = detection.xmax
                    ymax = detection.ymax
                elif detection_format == "tensor":
                    label = int(detection[1])
                    confidence = detection[2]
                    xmin = detection[3]
                    ymin = detection[4]
                    xmax = detection[5]
                    ymax = detection[6]
                else:
                    continue
                
                if label == 15 and confidence > 0.5:  # Person class with confidence > 0.5
                    person_found = True
                    
                    # Get bounding box coordinates
                    # Detection coordinates are normalized (0-1)
                    x_min = int(xmin * w)
                    y_min = int(ymin * h)
                    x_max = int(xmax * w)
                    y_max = int(ymax * h)
                    
                    # Clamp to frame bounds
                    x_min = max(0, min(w - 1, x_min))
                    y_min = max(0, min(h - 1, y_min))
                    x_max = max(0, min(w - 1, x_max))
                    y_max = max(0, min(h - 1, y_max))
                    
                    person_bbox = (x_min, y_min, x_max, y_max)
                    
                    # Draw bounding box
                    cv2.rectangle(annotated_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    
                    # Draw label
                    label_text = f"Person {confidence:.2f}"
                    cv2.putText(annotated_frame, label_text, (x_min, y_min - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # Only take the first (most confident) person detection
                    break
        
        return person_found, person_bbox, annotated_frame
    
    def _detect_person_mediapipe(self, frame):
        """Detect person using MediaPipe Pose"""
        annotated_frame = frame.copy()
        person_found = False
        person_bbox = None
        
        if self.mediapipe_pose is None:
            return False, None, annotated_frame
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mediapipe_pose.process(rgb_frame)
        
        if results.pose_landmarks:
            # Get bounding box from pose landmarks
            h, w = frame.shape[:2]
            landmarks = results.pose_landmarks.landmark
            
            x_coords = [lm.x * w for lm in landmarks]
            y_coords = [lm.y * h for lm in landmarks]
            
            x_min = int(min(x_coords))
            x_max = int(max(x_coords))
            y_min = int(min(y_coords))
            y_max = int(max(y_coords))
            
            # Add padding
            padding = 20
            x_min = max(0, x_min - padding)
            y_min = max(0, y_min - padding)
            x_max = min(w, x_max + padding)
            y_max = min(h, y_max + padding)
            
            person_bbox = (x_min, y_min, x_max, y_max)
            person_found = True
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            cv2.putText(annotated_frame, "Person (MediaPipe)", (x_min, y_min - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return person_found, person_bbox, annotated_frame
    
    def _parse_neural_network_output(self, detection_data):
        """
        Parse NeuralNetwork output tensor into detection format
        MobileNet-SSD output: [batch, num_detections, 7]
        Each detection: [image_id, label, confidence, x_min, y_min, x_max, y_max]
        """
        detections = []
        if detection_data is None or len(detection_data) == 0:
            return detections
        
        # Reshape to [num_detections, 7]
        num_detections = len(detection_data) // 7
        for i in range(num_detections):
            idx = i * 7
            if idx + 6 < len(detection_data):
                detection = detection_data[idx:idx+7]
                # Filter out invalid detections (confidence = -1 means no detection)
                if detection[2] > 0:
                    detections.append(detection)
        
        return detections
    
    def release(self):
        """Release camera resources"""
        if self.mediapipe_pose:
            self.mediapipe_pose.close()
        if self.device:
            del self.device
        self.pipeline = None
        self.rgb_queue = None
        self.nn_queue = None
        print("[OAKDCamera] Released")
