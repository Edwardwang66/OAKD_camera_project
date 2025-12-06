"""
OAKD Lite Camera with Person Detection for Raspberry Pi
Integrates OAKD camera with person detection using MobileNet-SSD or MediaPipe
Designed for Raspberry Pi 5 with X11 forwarding
"""
import cv2
import numpy as np
import time

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
    def __init__(self, use_oakd=True, fallback_camera_id=0, video_source=None,
                 allow_fallback=False, usb2_mode=True, fast_mode=False):
        """
        Initialize OAKD camera with person detection

        Args:
            use_oakd: If True, attempt to use an attached OAK-D device
            fallback_camera_id: ID for cv2.VideoCapture fallback
            video_source: Optional path or device index override for fallback capture
            allow_fallback: If False, do not fall back to webcam/MediaPipe when DepthAI fails
            usb2_mode: If True, force USB2 for stability (reduces bandwidth/power draw)
            fast_mode: If True, reduce resolution and bump FPS for faster control loop
        """
        self.pipeline = None
        self.device = None
        self.rgb_queue = None
        self.nn_queue = None
        self.detection_nn = None
        self.available = False
        self.use_mediapipe_fallback = False
        self.mediapipe_pose = None
        self.fallback_camera = None
        self.using_fallback_camera = False
        self.use_oakd = use_oakd
        self.fallback_camera_id = fallback_camera_id
        self.video_source = video_source
        self._restart_attempted = False
        self._restart_in_progress = False
        self._restart_attempts = 0
        self.next_reconnect_time = 0
        self.reconnect_backoff = 1.0  # seconds, doubles up to a cap
        self._restart_attempted = False
        self._restart_in_progress = False
        self.allow_fallback = allow_fallback
        self.using_depthai_nn = False
        # Default to USB2 for stability; fast_mode can override at init time if desired
        self.usb2_mode = usb2_mode
        self.fast_mode = fast_mode
        
        # If user explicitly disabled OAKD or DepthAI isn't installed, go straight to fallback
        if not self.use_oakd or not DEPTHAI_AVAILABLE:
            if not DEPTHAI_AVAILABLE:
                print("Warning: DepthAI not available. Using fallback camera with MediaPipe if possible.")
            if self.allow_fallback:
                self.setup_webcam_fallback()
                return
            raise RuntimeError("DepthAI not available and fallback disabled")
        
        # Try to set up DepthAI pipeline
        try:
            self.setup_pipeline()
        except Exception as e:
            print(f"[OAKDCamera] DepthAI pipeline setup failed: {e}")
            if not self.allow_fallback:
                raise
            # Try MediaPipe fallback using OAKD camera first
            if MEDIAPIPE_AVAILABLE:
                try:
                    print("[OAKDCamera] Falling back to MediaPipe person detection")
                    self.setup_mediapipe_fallback()
                    return
                except Exception as mp_error:
                    print(f"[OAKDCamera] MediaPipe fallback on OAKD failed: {mp_error}")
            # Final fallback to regular webcam/video source
            print("[OAKDCamera] Attempting webcam/video fallback...")
            self.setup_webcam_fallback()
    
    def setup_pipeline(self):
        """Set up DepthAI pipeline with RGB camera and person detection"""
        try:
            # Ensure an OAK-D device is connected before building the pipeline
            if not self._is_depthai_device_connected():
                raise RuntimeError("No OAKD device found")
            
            # Create pipeline
            self.pipeline = dai.Pipeline()
            
            # Create RGB camera (stick to 1080P to avoid IMX378 warnings)
            cam_rgb = self.pipeline.create(dai.node.ColorCamera)
            cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
            cam_rgb.setPreviewSize(300, 300)   # NN input (square, letterboxed)
            cam_rgb.setVideoSize(640, 480)     # Display size (wider view)
            cam_rgb.setFps(20)                 # Balanced FPS/latency
            cam_rgb.setPreviewKeepAspectRatio(True)
            cam_rgb.setInterleaved(False)
            cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
            try:
                cam_rgb.setVideoKeepAspectRatio(True)
            except Exception:
                pass
            
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
                # Slightly lower threshold to improve recall in low light
                self.detection_nn.setConfidenceThreshold(0.35)
                try:
                    self.detection_nn.setNumInferenceThreads(2)
                except Exception:
                    pass
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
            
            # Linking: preview (300x300 letterboxed) -> NN; video (640x360) -> display
            cam_rgb.preview.link(self.detection_nn.input)
            cam_rgb.video.link(xout_rgb.input)
            self.detection_nn.out.link(xout_nn.input)
            
            # Connect to device
            try:
                self.device = dai.Device(self.pipeline, usb2Mode=self.usb2_mode)
            except TypeError:
                self.device = dai.Device(self.pipeline, self.usb2_mode)
            self.rgb_queue = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            self.nn_queue = self.device.getOutputQueue(name="nn", maxSize=4, blocking=False)
            
            self.available = True
            self.using_depthai_nn = True
            self.reconnect_backoff = 1.0
            print("[OAKDCamera] Camera initialized successfully with DepthAI person detection")
            
        except Exception as e:
            print(f"[OAKDCamera] Error setting up DepthAI detection: {e}")
            self.available = False
            raise
    
    def setup_mediapipe_fallback(self):
        """Set up OAKD camera with MediaPipe person detection fallback"""
        try:
            if not self._is_depthai_device_connected():
                raise RuntimeError("No OAKD device found for MediaPipe fallback")
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
            self.using_depthai_nn = False
            print("[OAKDCamera] Camera initialized with MediaPipe person detection fallback")
            
        except Exception as e:
            print(f"[OAKDCamera] Error setting up MediaPipe fallback: {e}")
            self.available = False
            raise

    def setup_webcam_fallback(self):
        """Set up webcam/video source with MediaPipe detection (no OAKD required)"""
        if not MEDIAPIPE_AVAILABLE:
            raise RuntimeError("MediaPipe not available for webcam fallback")
        
        source = self.video_source if self.video_source is not None else self.fallback_camera_id
        # Allow numeric strings for device indices
        if isinstance(source, str) and source.isdigit():
            source = int(source)
        self.fallback_camera = cv2.VideoCapture(source)
        if not self.fallback_camera.isOpened():
            raise RuntimeError(f"Could not open fallback camera/video source: {source}")
        
        # Configure basic resolution for consistent overlays
        self.fallback_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.fallback_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.mp_pose = mp.solutions.pose
        self.mediapipe_pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5
        )
        
        self.use_mediapipe_fallback = True
        self.using_fallback_camera = True
        self.available = True
        self.using_depthai_nn = False
        print("[OAKDCamera] Using webcam/video fallback with MediaPipe person detection")

    def _restart_depthai_pipeline(self):
        """Attempt to restart the DepthAI pipeline after a runtime error"""
        if not DEPTHAI_AVAILABLE or not self.use_oakd:
            return False
        if self._restart_attempted:
            return False
        self._restart_attempted = True
        self._restart_attempts += 1
        self._restart_in_progress = True
        try:
            # Release existing resources and rebuild pipeline
            self.release()
            self.using_depthai_nn = False
            self.exposure_locked = False
            self.setup_pipeline()
            self._restart_in_progress = False
            return self.available
        except Exception as e:
            print(f"[OAKDCamera] Restart attempt failed: {e}")
            self._restart_in_progress = False
            return False
    
    def get_frame(self):
        """
        Get a frame from the camera
        
        Returns:
            numpy.ndarray: BGR frame, or None if no frame available
        """
        if self.using_fallback_camera:
            if self.fallback_camera is None:
                return None
            ret, frame = self.fallback_camera.read()
            return frame if ret else None
        
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
        # If OAK-D is unavailable, periodically attempt reconnection
        if not self.available and self.use_oakd and not self.using_fallback_camera:
            now = time.time()
            if now >= self.next_reconnect_time and not self._restart_in_progress:
                print("[OAKDCamera] Attempting to reconnect to OAK-D...")
                if self._restart_depthai_pipeline():
                    try:
                        frame = self.get_frame()
                        if frame is None:
                            return False, None, None
                    except Exception as restart_error:
                        print(f"[OAKDCamera] Reconnect succeeded but failed to read frame: {restart_error}")
                        return False, None, None
                else:
                    return False, None, None
            elif not self.use_mediapipe_fallback:
                # Not ready to retry yet; no fallback available
                return False, None, None
        
        # Get frame
        try:
            frame = self.get_frame()
            # If we made it here, reset restart flag for future errors
            self._restart_attempted = False
        except RuntimeError as e:
            # Handle DepthAI link errors at runtime and fall back to webcam/MediaPipe
            if "X_LINK_ERROR" in str(e) or "Communication exception" in str(e):
                if self.use_oakd and not self.using_fallback_camera and not self._restart_in_progress:
                    print("[OAKDCamera] Runtime link error, marking camera unavailable and scheduling reconnect...")
                    self.available = False
                    self.next_reconnect_time = time.time() + self.reconnect_backoff
                    self.reconnect_backoff = min(self.reconnect_backoff * 2, 10.0)
                    return False, None, None
                else:
                    if not self.allow_fallback:
                        print("[OAKDCamera] Runtime link error and fallback disabled")
                        self.available = False
                        return False, None, None
                    print("[OAKDCamera] Runtime link error, switching to webcam fallback...")
                    try:
                        self.setup_webcam_fallback()
                        frame = self.get_frame()
                    except Exception as fallback_error:
                        print(f"[OAKDCamera] Webcam fallback failed: {fallback_error}")
                        self.available = False
                        return False, None, None
            else:
                raise
        
        if frame is None:
            return False, None, None
        
        annotated_frame = frame.copy()
        person_found = False
        person_bbox = None
        conf_threshold = 0.35
        
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
                
                if label == 15 and confidence > conf_threshold:  # Person class
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
    
    def _is_depthai_device_connected(self):
        """Check if an OAKD/DepthAI device is connected"""
        if not DEPTHAI_AVAILABLE:
            return False
        try:
            devices = dai.Device.getAllAvailableDevices()
            return len(devices) > 0
        except Exception:
            # If the API is unavailable, fall back to attempting connection elsewhere
            return True
    
    def release(self):
        """Release camera resources"""
        if self.mediapipe_pose:
            self.mediapipe_pose.close()
            self.mediapipe_pose = None
        if self.device:
            try:
                self.device.close()
            except Exception:
                pass
            self.device = None
        if self.fallback_camera:
            self.fallback_camera.release()
            self.fallback_camera = None
        self.pipeline = None
        self.rgb_queue = None
        self.nn_queue = None
        self.available = False
        self.using_depthai_nn = False
        self.use_mediapipe_fallback = False
        self.using_fallback_camera = False
        print("[OAKDCamera] Released")

    def get_status(self):
        """Expose backend/exposure status for UI overlays"""
        return {
            "using_depthai_nn": self.using_depthai_nn,
            "using_mediapipe": self.use_mediapipe_fallback,
            "using_webcam": self.using_fallback_camera,
            "camera_notes": [],
        }
