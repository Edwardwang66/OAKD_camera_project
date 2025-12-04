"""
OAKD Camera to HDMI Display
Directly displays OAKD camera feed to HDMI screen using framebuffer
"""
import os
import sys
import time

# CRITICAL: Configure environment BEFORE any imports
# Unset DISPLAY to avoid X11/Qt issues
if 'DISPLAY' in os.environ:
    del os.environ['DISPLAY']

# Disable Qt
os.environ.pop('QT_QPA_PLATFORM', None)

# Add paths
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

phase2_dir = os.path.join(parent_dir, 'phase2')
sys.path.insert(0, phase2_dir)

import numpy as np
import cv2

from oakd_camera import OAKDCamera


def get_framebuffer_resolution():
    """Get resolution from framebuffer"""
    try:
        import subprocess
        result = subprocess.run(['fbset', '-s'], 
                              capture_output=True, text=True, timeout=1)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'geometry' in line.lower():
                    parts = line.split()
                    if len(parts) >= 3:
                        return int(parts[1]), int(parts[2])
    except:
        pass
    return 1024, 600  # Default


class FramebufferDisplay:
    """Direct framebuffer display for Raspberry Pi HDMI"""
    def __init__(self, width=1024, height=600):
        self.width = width
        self.height = height
        self.fb_device = None
        
        # Get actual resolution from framebuffer
        width, height = get_framebuffer_resolution()
        self.width = width
        self.height = height
        self.fb_size = width * height * 4  # RGBA32
        
        # Open framebuffer device
        try:
            self.fb_device = open('/dev/fb0', 'wb')
            print(f"✓ Opened framebuffer: /dev/fb0 ({width}x{height})")
        except Exception as e:
            print(f"ERROR: Could not open framebuffer /dev/fb0: {e}")
            print("Make sure you have permission: sudo chmod 666 /dev/fb0")
            raise
    
    def write_frame(self, frame):
        """
        Write frame to framebuffer
        
        Args:
            frame: numpy array (BGR frame from camera)
        """
        # Resize frame to match framebuffer resolution
        if frame.shape[:2] != (self.height, self.width):
            frame = cv2.resize(frame, (self.width, self.height))
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to RGBA (framebuffer expects RGBA32)
        alpha = np.ones((self.height, self.width, 1), dtype=np.uint8) * 255
        frame_rgba = np.concatenate([frame_rgb, alpha], axis=2)
        
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


def main():
    """Main function"""
    print("=" * 60)
    print("OAKD Camera to HDMI Display")
    print("=" * 60)
    
    # Get display resolution
    width, height = get_framebuffer_resolution()
    print(f"\nDisplay Resolution: {width}x{height}")
    
    # Initialize OAKD camera
    print("\n[1/2] Initializing OAKD camera...")
    try:
        camera = OAKDCamera()
        if not camera.available:
            print("ERROR: OAKD camera not available")
            sys.exit(1)
        print("✓ Camera initialized")
    except Exception as e:
        print(f"ERROR: Could not initialize camera: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Initialize framebuffer display
    print("\n[2/2] Setting up framebuffer display...")
    try:
        display = FramebufferDisplay(width, height)
        print("✓ Framebuffer display ready")
    except Exception as e:
        print(f"ERROR: Could not initialize framebuffer: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Camera feed is now displaying on HDMI screen")
    print("Press Ctrl+C to quit")
    print("=" * 60 + "\n")
    
    frame_count = 0
    last_fps_time = time.time()
    fps = 0
    
    try:
        while True:
            # Get frame from camera
            frame = camera.get_frame()
            
            if frame is not None:
                # Add overlay information
                overlay = frame.copy()
                
                # Add FPS counter
                frame_count += 1
                current_time = time.time()
                if current_time - last_fps_time >= 1.0:
                    fps = frame_count
                    frame_count = 0
                    last_fps_time = current_time
                
                cv2.putText(overlay, f"FPS: {fps}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(overlay, "OAKD Camera - HDMI Output", (10, overlay.shape[0] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Write frame to framebuffer
                display.write_frame(overlay)
            else:
                time.sleep(0.01)
                continue
            
            # Small delay for frame rate control
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nCleaning up...")
        display.close()
        camera.release()
        print("Done!")


if __name__ == "__main__":
    main()
