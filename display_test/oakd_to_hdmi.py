"""
OAKD Camera to HDMI Display
Directly displays OAKD camera feed to HDMI screen without OpenCV window system
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

# Import OpenCV AFTER environment setup
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


def display_frame_to_hdmi(frame, width=1024, height=600):
    """
    Display frame directly to HDMI using OpenCV window
    
    Args:
        frame: numpy array (BGR frame)
        width: Display width
        height: Display height
    """
    # Resize frame to match display
    if frame.shape[:2] != (height, width):
        frame = cv2.resize(frame, (width, height))
    
    return frame


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
    
    # Create display window
    print("\n[2/2] Setting up display...")
    window_name = "OAKD Camera - HDMI Output"
    
    try:
        # Try fullscreen mode
        cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        print("✓ Fullscreen mode enabled")
    except Exception as e:
        print(f"Warning: Could not set fullscreen: {e}")
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, width, height)
        print("✓ Window mode enabled")
    
    print("\n" + "=" * 60)
    print("Camera feed is now displaying on HDMI screen")
    print("Press 'q' to quit")
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
                cv2.putText(overlay, "Press 'q' to quit", (10, overlay.shape[0] - 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                
                # Display frame
                display_frame = display_frame_to_hdmi(overlay, width, height)
                cv2.imshow(window_name, display_frame)
            else:
                time.sleep(0.01)
                continue
            
            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                break
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nCleaning up...")
        camera.release()
        cv2.destroyAllWindows()
        print("Done!")


if __name__ == "__main__":
    main()

