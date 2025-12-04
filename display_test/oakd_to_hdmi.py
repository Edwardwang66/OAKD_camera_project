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


def get_framebuffer_info(fb_device='/dev/fb0'):
    """
    Get framebuffer resolution and format information
    
    Returns:
        tuple: (width, height, bits_per_pixel, format)
    """
    try:
        import subprocess
        result = subprocess.run(['fbset', '-i', '-fb', fb_device], 
                              capture_output=True, text=True, timeout=1)
        if result.returncode == 0:
            width, height = 1024, 600
            bits_per_pixel = 32
            format_str = 'RGBA32'
            
            for line in result.stdout.split('\n'):
                line_lower = line.lower()
                if 'geometry' in line_lower:
                    parts = line.split()
                    if len(parts) >= 3:
                        width = int(parts[1])
                        height = int(parts[2])
                elif 'bits_per_pixel' in line_lower or 'bpp' in line_lower:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'bits' in part.lower() or 'bpp' in part.lower():
                            if i + 1 < len(parts):
                                try:
                                    bits_per_pixel = int(parts[i + 1])
                                except:
                                    pass
            
            # Determine format based on bits per pixel
            if bits_per_pixel == 24:
                format_str = 'RGB24'
            elif bits_per_pixel == 32:
                format_str = 'RGBA32'
            
            return width, height, bits_per_pixel, format_str
    except:
        pass
    return 1024, 600, 24, 'RGB24'  # Default to RGB24


def get_framebuffer_resolution(fb_device='/dev/fb0'):
    """Get resolution from framebuffer (backward compatibility)"""
    width, height, _, _ = get_framebuffer_info(fb_device)
    return width, height


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
        self.bits_per_pixel = 24
        self.format = 'RGB24'
        
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
        
        # Get actual resolution and format from framebuffer
        width, height, bits_per_pixel, format_str = get_framebuffer_info(self.fb_path)
        self.width = width
        self.height = height
        self.bits_per_pixel = bits_per_pixel
        self.format = format_str
        
        # Calculate buffer size based on format
        if bits_per_pixel == 24:
            self.fb_size = width * height * 3  # RGB24
        elif bits_per_pixel == 32:
            self.fb_size = width * height * 4  # RGBA32
        else:
            # Default to RGB24
            self.fb_size = width * height * 3
            self.bits_per_pixel = 24
            self.format = 'RGB24'
        
        # Note: Device files don't report size correctly, so we'll use calculated size
        # and handle write errors gracefully
        print(f"Calculated frame size: {self.fb_size} bytes ({self.format})")
        self.write_enabled = True
        self.write_failures = 0
        
        # Open framebuffer device
        try:
            self.fb_device = open(self.fb_path, 'wb')
            print(f"✓ Opened framebuffer: {self.fb_path} ({width}x{height}, {self.format})")
        except Exception as e:
            print(f"ERROR: Could not open framebuffer {self.fb_path}: {e}")
            print(f"Make sure you have permission: sudo chmod 666 {self.fb_path}")
            raise
    
    def write_frame(self, frame):
        """
        Write frame to framebuffer (non-blocking, fails gracefully)
        
        Args:
            frame: numpy array (BGR frame from camera)
        """
        if self.fb_device is None or not self.write_enabled:
            return
        
        # If we've had failures, disable writing quickly to keep camera running
        if self.write_failures > 3:
            if not hasattr(self, '_disabled_shown'):
                print("\n⚠ Framebuffer writes disabled after failures")
                print("   OAKD camera will continue running (reading frames from queue)")
                print("   Display is disabled - check framebuffer configuration")
                self._disabled_shown = True
            self.write_enabled = False
            return
        
        try:
            # Resize frame to match framebuffer resolution
            if frame.shape[:2] != (self.height, self.width):
                frame = cv2.resize(frame, (self.width, self.height))
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Prepare frame based on framebuffer format
            if self.bits_per_pixel == 24:
                # RGB24 format (3 bytes per pixel)
                frame_output = frame_rgb.astype(np.uint8)
            elif self.bits_per_pixel == 32:
                # RGBA32 format (4 bytes per pixel)
                alpha = np.ones((self.height, self.width, 1), dtype=np.uint8) * 255
                frame_output = np.concatenate([frame_rgb, alpha], axis=2).astype(np.uint8)
            else:
                # Default to RGB24
                frame_output = frame_rgb.astype(np.uint8)
            
            # Ensure we're writing exactly the right amount of data
            expected_size = self.fb_size
            actual_size = frame_output.nbytes
            
            if actual_size != expected_size:
                # Resize if needed
                if actual_size > expected_size:
                    frame_output = frame_output[:self.height, :self.width]
                return
            
            # Write to framebuffer (non-blocking)
            self.fb_device.seek(0)
            frame_bytes = frame_output.tobytes()
            
            # Ensure we don't write more than expected
            if len(frame_bytes) > expected_size:
                frame_bytes = frame_bytes[:expected_size]
            
            bytes_written = self.fb_device.write(frame_bytes)
            self.fb_device.flush()
            
            # Reset failure count on successful write
            if bytes_written == expected_size:
                self.write_failures = 0
                
        except OSError as e:
            # Handle framebuffer write errors gracefully
            self.write_failures += 1
            error_str = str(e)
            
            if 'No space left on device' in error_str or 'errno 28' in error_str.lower():
                # Try switching to RGB24 if we haven't already
                if self.bits_per_pixel == 32 and self.write_failures == 1:
                    print(f"\n⚠ Framebuffer write error, trying RGB24 format...")
                    self.bits_per_pixel = 24
                    self.format = 'RGB24'
                    self.fb_size = self.width * self.height * 3
                # After a few failures, disable to keep camera running
                if self.write_failures >= 3:
                    self.write_enabled = False
            else:
                # Other errors - disable after a few failures
                if self.write_failures <= 3:
                    pass  # Silent retry
                else:
                    self.write_enabled = False
                    
        except Exception as e:
            self.write_failures += 1
            if self.write_failures <= 3:
                pass  # Silent retry
            else:
                self.write_enabled = False
    
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
    print("OAKD Camera feed is now displaying on HDMI screen")
    print("Press Ctrl+C to quit")
    print("=" * 60)
    print("\nNote: OAKD camera uses non-blocking queues.")
    print("      Frames are read continuously to prevent queue overflow.\n")
    
    frame_count = 0
    last_fps_time = time.time()
    fps = 0
    error_count = 0
    max_errors = 10
    skipped_frames = 0
    last_display_time = time.time()
    target_fps = 30.0
    frame_interval = 1.0 / target_fps
    
    print("OAKD Camera: Keep reading frames regularly to prevent queue overflow")
    print(f"Target display FPS: {target_fps}\n")
    
    try:
        while True:
            # CRITICAL: Always try to get frame from OAKD camera queue
            # OAKD camera uses non-blocking queues - we must read regularly
            # or the queue will fill up and cause X_LINK_ERROR
            try:
                frame = camera.get_frame()
            except RuntimeError as e:
                error_count += 1
                error_msg = str(e)
                
                # Check if it's an X_LINK_ERROR (communication error)
                if 'X_LINK_ERROR' in error_msg or 'Communication exception' in error_msg:
                    if error_count <= max_errors:
                        if error_count == 1:  # Only print first error
                            print(f"\n⚠ OAKD Camera communication error ({error_count}/{max_errors})")
                            print("   This can happen if camera queue overflows or USB connection issues")
                            print("   Continuing to read from queue...")
                        time.sleep(0.01)  # Very short delay, keep reading queue
                        continue
                    else:
                        print(f"\n❌ Too many OAKD camera communication errors ({error_count})")
                        print("Possible causes:")
                        print("  1. USB cable connection issue - try unplugging and replugging")
                        print("  2. USB port power issue - try a different USB port")
                        print("  3. Camera queue overflow - framebuffer writes too slow")
                        print("  4. Device needs to be reset")
                        print("\nExiting...")
                        break
                else:
                    # Other runtime errors
                    print(f"\n❌ OAKD Camera error: {error_msg}")
                    if error_count > max_errors:
                        print("Too many errors. Exiting...")
                        break
                    time.sleep(0.01)
                    continue
            except Exception as e:
                error_count += 1
                if error_count <= 3:  # Only print first few
                    print(f"\n⚠ Unexpected OAKD camera error ({error_count}/{max_errors}): {e}")
                if error_count > max_errors:
                    print("Too many errors. Exiting...")
                    break
                time.sleep(0.01)
                continue
            
            # Reset error count on successful frame read
            if frame is not None:
                error_count = 0
            
            # Display frame if available and enough time has passed
            current_time = time.time()
            if frame is not None:
                # Check if we should display this frame (frame rate limiting)
                if current_time - last_display_time >= frame_interval:
                    # Add overlay information
                    overlay = frame.copy()
                    
                    # Add FPS counter
                    frame_count += 1
                    if current_time - last_fps_time >= 1.0:
                        fps = frame_count
                        frame_count = 0
                        last_fps_time = current_time
                    
                    cv2.putText(overlay, f"FPS: {fps}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(overlay, "OAKD Camera - HDMI Output", (10, overlay.shape[0] - 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Write frame to framebuffer (non-blocking, fast)
                    display.write_frame(overlay)
                    last_display_time = current_time
                else:
                    # Skip frame to maintain frame rate
                    skipped_frames += 1
            
            # Very short delay - OAKD camera needs regular queue reads
            # Don't block here or camera queue will overflow
            time.sleep(0.001)  # 1ms - just enough to prevent CPU spinning
    
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
