"""
Person Detection using OAK-D's MobileNet-SSD Model
Detects persons in the frame and returns bounding boxes
"""
import cv2
import numpy as np

# Try to import depthai
try:
    import depthai as dai
    DEPTHAI_AVAILABLE = True
except ImportError:
    DEPTHAI_AVAILABLE = False
    print("Note: DepthAI not available. Person detection will use fallback.")


class PersonDetector:
    """
    Person detector using OAK-D's built-in MobileNet-SSD model
    Note: This creates a separate pipeline. For better integration, 
    consider using a shared pipeline with the main camera.
    """
    def __init__(self, use_separate_pipeline=True):
        """
        Initialize person detector
        
        Args:
            use_separate_pipeline: If True, creates separate camera pipeline.
                                  If False, expects frames to be passed in.
        """
        self.pipeline = None
        self.device = None
        self.rgb_queue = None
        self.nn_queue = None
        self.detection_nn = None
        self.use_separate_pipeline = use_separate_pipeline
        
        if not DEPTHAI_AVAILABLE:
            print("Warning: DepthAI not available. Person detection disabled.")
            self.available = False
            return
        
        if use_separate_pipeline:
            self.available = True
            self.setup_pipeline()
        else:
            # Will use frames passed in detect_person
            self.available = True
            print("Person detector initialized (will use provided frames)")
    
    def setup_pipeline(self):
        """Set up DepthAI pipeline with MobileNet-SSD for person detection"""
        try:
            # Create pipeline
            self.pipeline = dai.Pipeline()
            
            # Create RGB camera
            cam_rgb = self.pipeline.create(dai.node.ColorCamera)
            cam_rgb.setPreviewSize(300, 300)  # MobileNet-SSD input size
            cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
            cam_rgb.setInterleaved(False)
            cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
            
            # Create detection network
            self.detection_nn = self.pipeline.create(dai.node.MobileNetDetectionNetwork)
            # Use built-in mobilenet-ssd model
            # The model path will be automatically downloaded by DepthAI
            try:
                blob_path = self._get_mobilenet_ssd_path()
                self.detection_nn.setBlobPath(blob_path)
            except Exception as e:
                print(f"Warning: Could not get mobilenet-ssd blob: {e}")
                print("Trying to use blobconverter...")
                try:
                    import blobconverter
                    blob_path = blobconverter.from_zoo(name="mobilenet-ssd", shaves=6)
                    self.detection_nn.setBlobPath(blob_path)
                except Exception as e2:
                    print(f"Error: Could not load mobilenet-ssd model: {e2}")
                    raise RuntimeError("Could not initialize MobileNet-SSD model")
            
            self.detection_nn.setConfidenceThreshold(0.5)
            self.detection_nn.input.setBlocking(False)
            
            # Create output
            xout_rgb = self.pipeline.create(dai.node.XLinkOut)
            xout_rgb.setStreamName("rgb")
            
            xout_nn = self.pipeline.create(dai.node.XLinkOut)
            xout_nn.setStreamName("nn")
            
            # Linking
            cam_rgb.preview.link(self.detection_nn.input)
            cam_rgb.preview.link(xout_rgb.input)
            self.detection_nn.out.link(xout_nn.input)
            
            # Connect to device
            self.device = dai.Device(self.pipeline)
            self.rgb_queue = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            self.nn_queue = self.device.getOutputQueue(name="nn", maxSize=4, blocking=False)
            
            print("Person detector initialized successfully")
            
        except Exception as e:
            print(f"Error setting up person detector: {e}")
            print("Falling back to basic detection...")
            self.available = False
    
    def _get_mobilenet_ssd_path(self):
        """
        Get path to MobileNet-SSD model blob
        DepthAI will download it automatically if not present
        """
        # Use blobconverter to get the model
        try:
            import blobconverter
            blob_path = blobconverter.from_zoo(
                name="mobilenet-ssd",
                shaves=6,
                version="2021.4"
            )
            return blob_path
        except ImportError:
            # If blobconverter not available, try to download manually
            # or use a local path if model is already downloaded
            import os
            model_path = os.path.expanduser("~/.cache/blobconverter/mobilenet-ssd_openvino_2021.4_6shave.blob")
            if os.path.exists(model_path):
                return model_path
            else:
                # Return a path that DepthAI might recognize
                # User will need to download the model manually
                raise RuntimeError(
                    "MobileNet-SSD model not found. Please install blobconverter:\n"
                    "pip install blobconverter\n"
                    "Or download the model manually."
                )
    
    def detect_person(self, frame=None):
        """
        Detect person in frame
        
        Args:
            frame: BGR frame to detect person in (required if not using separate pipeline)
                  If using separate pipeline and frame is None, will get from camera queue
            
        Returns:
            tuple: (person_found, person_bbox, annotated_frame)
                - person_found: True if person detected, False otherwise
                - person_bbox: (x_min, y_min, x_max, y_max) or None
                - annotated_frame: Frame with detection annotations
        """
        if not self.available:
            if frame is not None:
                return False, None, frame
            return False, None, None
        
        if self.use_separate_pipeline:
            # Get frame from camera queue (for detection)
            in_rgb = self.rgb_queue.tryGet()
            if in_rgb is None:
                if frame is not None:
                    return False, None, frame
                return False, None, None
            
            # Get detection frame (300x300 from camera)
            detection_frame = in_rgb.getCvFrame()
            
            # Use provided frame for display if available, otherwise use detection frame
            if frame is not None:
                annotated_frame = frame.copy()
                h, w = frame.shape[:2]
            else:
                annotated_frame = detection_frame.copy()
                h, w = annotated_frame.shape[:2]
            
            person_found = False
            person_bbox = None
            
            # Get detection results
            in_nn = self.nn_queue.tryGet()
            if in_nn is not None:
                detections = in_nn.detections
                
                # Find person detections (class 15 in COCO dataset for person)
                # Note: Detection coordinates are relative to 300x300 preview
                # We need to scale them to the actual frame size
                if frame is not None:
                    # Scale from 300x300 to actual frame size
                    scale_x = w / 300.0
                    scale_y = h / 300.0
                else:
                    scale_x = 1.0
                    scale_y = 1.0
                
                for detection in detections:
                    # COCO class 15 is "person"
                    if detection.label == 15:
                        person_found = True
                        
                        # Get bounding box coordinates (scale to actual frame size)
                        x_min = int(detection.xmin * 300 * scale_x)
                        y_min = int(detection.ymin * 300 * scale_y)
                        x_max = int(detection.xmax * 300 * scale_x)
                        y_max = int(detection.ymax * 300 * scale_y)
                        
                        # Clamp to frame bounds
                        x_min = max(0, min(w - 1, x_min))
                        y_min = max(0, min(h - 1, y_min))
                        x_max = max(0, min(w - 1, x_max))
                        y_max = max(0, min(h - 1, y_max))
                        
                        person_bbox = (x_min, y_min, x_max, y_max)
                        
                        # Draw bounding box
                        cv2.rectangle(annotated_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                        
                        # Draw label
                        label = f"Person {detection.confidence:.2f}"
                        cv2.putText(annotated_frame, label, (x_min, y_min - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        # Only take the first (most confident) person detection
                        break
            
            return person_found, person_bbox, annotated_frame
        else:
            # Not using separate pipeline - would need to process frame here
            # For now, fall back to fallback detector
            if frame is None:
                return False, None, None
            # Use a simple approach - just return frame without detection
            # In a full implementation, you'd process the frame here
            return False, None, frame
    
    def release(self):
        """Release resources"""
        if self.device:
            del self.device
        self.pipeline = None
        self.rgb_queue = None
        self.nn_queue = None


# Fallback person detector using OpenCV DNN (for testing without OAK-D)
class PersonDetectorFallback:
    """
    Fallback person detector using OpenCV DNN
    For testing when OAK-D is not available
    """
    def __init__(self):
        """Initialize fallback detector"""
        try:
            # Load MobileNet-SSD model
            self.net = cv2.dnn.readNetFromCaffe(
                'models/MobileNetSSD_deploy.prototxt',
                'models/MobileNetSSD_deploy.caffemodel'
            )
            self.available = True
        except:
            print("Warning: Could not load MobileNet-SSD model for fallback detection")
            self.available = False
            self.net = None
    
    def detect_person(self, frame):
        """
        Detect person in frame using OpenCV DNN
        
        Args:
            frame: BGR frame
            
        Returns:
            tuple: (person_found, person_bbox, annotated_frame)
        """
        if not self.available or self.net is None:
            return False, None, frame
        
        annotated_frame = frame.copy()
        person_found = False
        person_bbox = None
        
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()
        
        # Find person detections (class 15)
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            class_id = int(detections[0, 0, i, 1])
            
            if confidence > 0.5 and class_id == 15:  # Person class
                person_found = True
                
                # Get bounding box
                x_min = int(detections[0, 0, i, 3] * w)
                y_min = int(detections[0, 0, i, 4] * h)
                x_max = int(detections[0, 0, i, 5] * w)
                y_max = int(detections[0, 0, i, 6] * h)
                
                person_bbox = (x_min, y_min, x_max, y_max)
                
                # Draw bounding box
                cv2.rectangle(annotated_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"Person {confidence:.2f}", (x_min, y_min - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                break
        
        return person_found, person_bbox, annotated_frame
    
    def release(self):
        """Release resources"""
        pass

