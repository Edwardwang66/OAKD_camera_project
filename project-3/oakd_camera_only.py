"""
OAKD Camera Only - No Webcam Fallback
Forces use of OAKD camera, raises error if not available
"""
import cv2
import numpy as np

# Try to import depthai
try:
    import depthai as dai
    DEPTHAI_AVAILABLE = True
except ImportError:
    DEPTHAI_AVAILABLE = False


class OAKDCameraOnly:
    def __init__(self):
        """
        Initialize OAKD camera only (no webcam fallback)
        Raises error if OAKD camera is not available
        """
        self.pipeline = None
        self.device = None
        self.rgb_queue = None
        
        if not DEPTHAI_AVAILABLE:
            raise RuntimeError(
                "DepthAI not available. Please install: pip install depthai"
            )
        
        self.setup_pipeline()
    
    def setup_pipeline(self):
        """Set up DepthAI pipeline - OAKD camera only"""
        # Try multiple API methods for compatibility with different DepthAI versions
        methods_to_try = [
            # Method 1: Standard API (most common)
            lambda: self._setup_pipeline_method1(),
            # Method 2: Alternative API (for some versions)
            lambda: self._setup_pipeline_method2(),
        ]
        
        last_error = None
        for i, method in enumerate(methods_to_try, 1):
            try:
                method()
                return  # Success!
            except (AttributeError, TypeError) as e:
                # API compatibility error - try next method
                last_error = e
                if i < len(methods_to_try):
                    continue  # Try next method
                else:
                    # All methods failed - API compatibility issue
                    raise RuntimeError(
                        f"Could not initialize OAKD camera. DepthAI API compatibility issue.\n"
                        f"Error: {e}\n\n"
                        f"Please try:\n"
                        f"  1. Upgrade DepthAI: pip install --upgrade depthai\n"
                        f"  2. Check DepthAI version: python -c 'import depthai as dai; print(getattr(dai, \"__version__\", \"unknown\"))'\n"
                        f"  3. Reinstall DepthAI: pip uninstall depthai && pip install depthai\n"
                        f"  4. Make sure OAKD camera is connected via USB"
                    )
            except RuntimeError as e:
                error_str = str(e)
                # Check for permission errors
                if "permission" in error_str.lower() or "X_LINK_INSUFFICIENT_PERMISSIONS" in error_str:
                    # Permission error - provide platform-specific help
                    import platform
                    system = platform.system()
                    
                    if system == "Darwin":  # macOS
                        help_msg = (
                            f"OAKD camera permission error on macOS.\n\n"
                            f"To fix this:\n"
                            f"  1. Grant USB permissions:\n"
                            f"     - Go to System Preferences > Security & Privacy > Privacy > Full Disk Access\n"
                            f"     - Or run: sudo chmod 666 /dev/bus/usb/*/*\n"
                            f"  2. Try running with sudo: sudo python3 test_oakd_laptop.py\n"
                            f"  3. Check if camera is detected: python3 -c 'import depthai as dai; devices = dai.Device.getAllAvailableDevices(); print(devices)'\n\n"
                            f"Original error: {error_str}"
                        )
                    elif system == "Linux":
                        help_msg = (
                            f"OAKD camera permission error on Linux.\n\n"
                            f"To fix this, set up udev rules:\n"
                            f"  1. Run: echo 'SUBSYSTEM==\"usb\", ATTRS{{idVendor}}==\"03e7\", MODE=\"0666\"' | sudo tee /etc/udev/rules.d/80-movidius.rules\n"
                            f"  2. Run: sudo udevadm control --reload-rules\n"
                            f"  3. Run: sudo udevadm trigger\n"
                            f"  4. Unplug and replug the OAKD camera\n"
                            f"  5. Or add your user to the dialout group: sudo usermod -a -G dialout $USER\n\n"
                            f"Original error: {error_str}"
                        )
                    else:
                        help_msg = (
                            f"OAKD camera permission error.\n\n"
                            f"Original error: {error_str}\n\n"
                            f"Please check your system's USB device permissions."
                        )
                    
                    raise RuntimeError(help_msg) from e
                else:
                    # Other RuntimeError (device not found, etc.)
                    raise RuntimeError(
                        f"Could not initialize OAKD camera: {error_str}\n"
                        f"Make sure:\n"
                        f"  1. OAKD camera is connected via USB\n"
                        f"  2. DepthAI is installed: pip install depthai\n"
                        f"  3. Camera drivers are properly installed"
                    ) from e
            except Exception as e:
                # Other errors
                raise RuntimeError(
                    f"Could not initialize OAKD camera: {e}\n"
                    f"Make sure:\n"
                    f"  1. OAKD camera is connected via USB\n"
                    f"  2. DepthAI is installed: pip install depthai\n"
                    f"  3. Camera drivers are properly installed"
                ) from e
    
    def _setup_pipeline_method1(self):
        """Method 1: Standard DepthAI API"""
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
        print("OAKD Lite camera initialized successfully")
    
    def _setup_pipeline_method2(self):
        """Method 2: Alternative DepthAI API (for some versions)"""
        self.pipeline = dai.Pipeline()
        # Try using createColorCamera and createXLinkOut methods directly
        cam_rgb = self.pipeline.createColorCamera()
        xout_rgb = self.pipeline.createXLinkOut()
        
        xout_rgb.setStreamName("rgb")
        cam_rgb.setPreviewSize(640, 480)
        cam_rgb.setInterleaved(False)
        cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
        cam_rgb.preview.link(xout_rgb.input)
        
        self.device = dai.Device(self.pipeline)
        self.rgb_queue = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        print("OAKD Lite camera initialized successfully (using alternative API)")
    
    def get_frame(self):
        """
        Get a frame from the OAKD camera
        
        Returns:
            numpy.ndarray: BGR frame, or None if no frame available
        """
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
        if self.device:
            del self.device
        self.pipeline = None
        self.rgb_queue = None

