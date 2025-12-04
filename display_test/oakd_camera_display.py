"""
OAKD Camera Display - Direct framebuffer output
Displays OAKD camera feed directly to HDMI display without OpenCV window system
"""
import os
import sys
import time

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Add phase2 to path for OAKD camera
phase2_dir = os.path.join(parent_dir, 'phase2')
sys.path.insert(0, phase2_dir)

# Configure environment BEFORE any imports
# Remove DISPLAY to avoid X11/Qt issues
if 'DISPLAY' in os.environ:
    del os.environ['DISPLAY']

# Disable Qt completely
os.environ.pop('QT_QPA_PLATFORM', None)

import numpy as np

# Try to import cv2 (we'll use it minimally, just for frame operations)
try:
    import cv2
    CV2_AVAILABLE = True
except:
    CV2_AVAILABLE = False
    print("Warning: OpenCV not available, using numpy only")

from oakd_camera import OAKDCamera
from utils import safe_imshow, safe_waitkey


class FramebufferDisplay:
    """
    Direct framebuffer display for Raspberry Pi
    Writes frames directly to /dev/fb0 without using OpenCV window system
    """
    def __init__(self, width=1024, height=600):
        """
        Initialize framebuffer display
        
        Args:
            width: Display width
            height: Display height
        """
        self.width = width
        self.height = height
        self.fb_device = None
        self.fb_size = width * height * 4  # RGBA32
        
        # Try to get resolution from framebuffer
        try:
            import subprocess
            result = subprocess.run(['fbset', '-s'], 
                                  capture_output=True, text=True, timeout=1)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'geometry' in line.lower():
                        parts = line.split()
                        if len(parts) >= 3:
                            self.width = int(parts[1])
                            self.height = int(parts[2])
                            self.fb_size = self.width * self.height * 4
                            print(f"Detected framebuffer resolution: {self.width}x{self.height}")
                            break
        except Exception as e:
            print(f"Could not detect framebuffer resolution: {e}")
        
        # Try to open framebuffer device
        try:
            self.fb_device = open('/dev/fb0', 'wb')
            print(f"✓ Opened framebuffer device: /dev/fb0")
        except Exception as e:
            print(f"Warning: Could not open framebuffer: {e}")
            print("Falling back to OpenCV window (may have Qt issues)")
            self.fb_device = None
    
    def write_frame(self, frame):
        """
        Write frame to framebuffer
        
        Args:
            frame: numpy array (BGR or RGB frame)
        """
        if self.fb_device is None:
            # Fallback to OpenCV
            if CV2_AVAILABLE:
                cv2.imshow('Camera', frame)
            return
        
        # Resize frame to match framebuffer
        if CV2_AVAILABLE:
            if frame.shape[:2] != (self.height, self.width):
                frame = cv2.resize(frame, (self.width, self.height))
            
            # Convert BGR to RGB
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                frame_rgb = frame
        else:
            # Resize using numpy
            if frame.shape[:2] != (self.height, self.width):
                from PIL import Image
                img = Image.fromarray(frame)
                img = img.resize((self.width, self.height))
                frame_rgb = np.array(img)
            else:
                frame_rgb = frame
        
        # Convert to RGBA (framebuffer expects RGBA32)
        if len(frame_rgb.shape) == 3:
            if frame_rgb.shape[2] == 3:
                # RGB to RGBA
                alpha = np.ones((self.height, self.width, 1), dtype=frame_rgb.dtype) * 255
                frame_rgba = np.concatenate([frame_rgb, alpha], axis=2)
            else:
                frame_rgba = frame_rgb
        else:
            # Grayscale to RGBA
            frame_rgba = np.stack([frame_rgb, frame_rgb, frame_rgb, 
                                  np.ones_like(frame_rgb) * 255], axis=2)
        
        # Ensure correct format (uint8, RGBA)
        frame_rgba = frame_rgba.astype(np.uint8)
        
        # Write to framebuffer
        try:
            self.fb_device.seek(0)
            self.fb_device.write(frame_rgba.tobytes())
            self.fb_device.flush()
        except Exception as e:
            print(f"Error writing to framebuffer: {e}")
    
    def close(self):
        """Close framebuffer device"""
        if self.fb_device:
            self.fb_device.close()
            self.fb_device = None


class OAKDCameraDisplay:
    """
    Display OAKD camera feed directly to HDMI display
    """
    def __init__(self):
        """Initialize OAKD camera display"""
        print("=" * 60)
        print("OAKD Camera Display - Direct to HDMI")
        print("=" * 60)
        
        # Initialize camera
        print("\n[1/2] Initializing OAKD camera...")
        try:
            self.camera = OAKDCamera()
            if not self.camera.available:
                print("ERROR: OAKD camera not available")
                sys.exit(1)
            print("✓ Camera initialized")
        except Exception as e:
            print(f"ERROR: Could not initialize camera: {e}")
            sys.exit(1)
        
        # Initialize display
        print("\n[2/2] Initializing display...")
        self.display = FramebufferDisplay()
        
        print("\n" + "=" * 60)
        print("Initialization complete!")
        print("=" * 60)
        print("\nCamera feed will be displayed on HDMI screen")
        print("Press 'q' to quit\n")
    
    def run(self):
        """Main display loop"""
        try:
            while True:
                # Get frame from camera
                frame = self.camera.get_frame()
                
                if frame is not None:
                    # Write frame to framebuffer
                    self.display.write_frame(frame)
                else:
                    time.sleep(0.01)
                    continue
                
                # Check for quit key
                key = safe_waitkey(1)
                if key == ord('q') or key == 27:  # 'q' or ESC
                    break
                
                # Small delay
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        self.display.close()
        self.camera.release()
        if CV2_AVAILABLE:
            cv2.destroyAllWindows()
        print("Cleanup complete!")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Display OAKD camera feed on HDMI')
    parser.add_argument('--fps', type=float, default=30.0,
                       help='Target FPS (default: 30.0)')
    
    args = parser.parse_args()
    
    display = OAKDCameraDisplay()
    display.run()


if __name__ == "__main__":
    main()

