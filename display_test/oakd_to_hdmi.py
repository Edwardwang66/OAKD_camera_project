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


def find_framebuffer_device():
    """
    Find available framebuffer devices and return the best one for HDMI
    
    Returns:
        str: Path to framebuffer device (e.g., '/dev/fb0')
    """
    import subprocess
    import glob
    
    # List all framebuffer devices
    fb_devices = sorted(glob.glob('/dev/fb*'))
    
    if not fb_devices:
        return None
    
    # Try to find the active one by checking fbset
    for fb_device in fb_devices:
        try:
            # Try to get info about this framebuffer
            result = subprocess.run(['fbset', '-i', '-fb', fb_device], 
                                  capture_output=True, text=True, timeout=1)
            if result.returncode == 0:
                # Check if it has a valid resolution
                for line in result.stdout.split('\n'):
                    if 'geometry' in line.lower():
                        return fb_device
        except:
            continue
    
    # Fallback to first available device
    return fb_devices[0]


def get_framebuffer_resolution(fb_device='/dev/fb0'):
    """Get resolution from framebuffer"""
    try:
        import subprocess
        result = subprocess.run(['fbset', '-s', '-fb', fb_device], 
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


def check_framebuffer_permissions(fb_device):
    """
    Check if we have permission to access framebuffer device
    Returns True if accessible, False otherwise
    """
    try:
        # Try to open the device
        test_file = open(fb_device, 'wb')
        test_file.close()
        return True
    except PermissionError:
        return False
    except Exception:
        return False


def setup_framebuffer_permissions(fb_device):
    """
    Attempt to set permissions on framebuffer device
    Returns True if successful, False otherwise
    """
    import subprocess
    
    try:
        # Try to set permissions (requires sudo)
        result = subprocess.run(['sudo', 'chmod', '666', fb_device],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True
    except:
        pass
    
    return False


class FramebufferDisplay:
    """Direct framebuffer display for Raspberry Pi HDMI"""
    def __init__(self, width=1024, height=600, fb_device=None):
        self.width = width
        self.height = height
        self.fb_device = None
        self.fb_path = fb_device
        
        # Find framebuffer device if not specified
        if self.fb_path is None:
            print("Detecting framebuffer device...")
            self.fb_path = find_framebuffer_device()
            if self.fb_path is None:
                raise RuntimeError("No framebuffer device found. Make sure HDMI is connected.")
            print(f"Found framebuffer device: {self.fb_path}")
        
        # Check permissions
        if not check_framebuffer_permissions(self.fb_path):
            print(f"\n⚠ Permission denied for {self.fb_path}")
            print("Attempting to set permissions...")
            if setup_framebuffer_permissions(self.fb_path):
                print("✓ Permissions set successfully")
            else:
                print(f"\n❌ Could not set permissions automatically.")
                print(f"Please run manually: sudo chmod 666 {self.fb_path}")
                raise PermissionError(f"Cannot access {self.fb_path}. Run: sudo chmod 666 {self.fb_path}")
        
        # Get actual resolution from framebuffer
        width, height = get_framebuffer_resolution(self.fb_path)
        self.width = width
        self.height = height
        self.fb_size = width * height * 4  # RGBA32
        
        # Open framebuffer device
        try:
            self.fb_device = open(self.fb_path, 'wb')
            print(f"✓ Opened framebuffer: {self.fb_path} ({width}x{height})")
        except Exception as e:
            print(f"ERROR: Could not open framebuffer {self.fb_path}: {e}")
            print(f"Make sure you have permission: sudo chmod 666 {self.fb_path}")
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Display OAKD camera on HDMI via framebuffer')
    parser.add_argument('--fb', type=str, default=None,
                       help='Framebuffer device path (e.g., /dev/fb0). Auto-detect if not specified.')
    args = parser.parse_args()
    
    print("=" * 60)
    print("OAKD Camera to HDMI Display")
    print("=" * 60)
    
    # Find framebuffer device
    if args.fb:
        fb_device = args.fb
        print(f"\nUsing specified framebuffer: {fb_device}")
    else:
        print("\nDetecting framebuffer device...")
        fb_device = find_framebuffer_device()
        if fb_device is None:
            print("ERROR: No framebuffer device found!")
            print("Available devices:")
            import glob
            for dev in glob.glob('/dev/fb*'):
                print(f"  - {dev}")
            print("\nMake sure HDMI is connected and try:")
            print("  python3 oakd_to_hdmi.py --fb /dev/fb0")
            sys.exit(1)
        print(f"Using framebuffer: {fb_device}")
    
    # Get display resolution
    width, height = get_framebuffer_resolution(fb_device)
    print(f"Display Resolution: {width}x{height}")
    
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
        display = FramebufferDisplay(width, height, fb_device=fb_device)
        print("✓ Framebuffer display ready")
    except PermissionError as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not initialize framebuffer: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Camera feed is now displaying on HDMI screen")
    print("Press Ctrl+C to quit")
    print("=" * 60 + "\n")
    
    frame_count = 0
    last_fps_time = time.time()
    fps = 0
    error_count = 0
    max_errors = 10
    
    try:
        while True:
            # Get frame from camera with error handling
            try:
                frame = camera.get_frame()
            except RuntimeError as e:
                error_count += 1
                error_msg = str(e)
                
                # Check if it's an X_LINK_ERROR (communication error)
                if 'X_LINK_ERROR' in error_msg or 'Communication exception' in error_msg:
                    if error_count <= max_errors:
                        print(f"\n⚠ Camera communication error ({error_count}/{max_errors}): {error_msg}")
                        print("Attempting to continue...")
                        time.sleep(0.1)
                        continue
                    else:
                        print(f"\n❌ Too many camera communication errors ({error_count})")
                        print("Possible causes:")
                        print("  1. USB cable connection issue - try unplugging and replugging")
                        print("  2. USB port power issue - try a different USB port")
                        print("  3. Device needs to be reset")
                        print("\nExiting...")
                        break
                else:
                    # Other runtime errors
                    print(f"\n❌ Camera error: {error_msg}")
                    if error_count > max_errors:
                        print("Too many errors. Exiting...")
                        break
                    time.sleep(0.1)
                    continue
            except Exception as e:
                error_count += 1
                print(f"\n⚠ Unexpected camera error ({error_count}/{max_errors}): {e}")
                if error_count > max_errors:
                    print("Too many errors. Exiting...")
                    break
                time.sleep(0.1)
                continue
            
            # Reset error count on successful frame
            if frame is not None:
                error_count = 0
            
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
