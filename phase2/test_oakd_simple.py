"""
Simple OAKD Camera Test
Displays OAKD camera feed in a window
"""
import cv2
import sys
import os
import argparse

# Try to import depthai
try:
    import depthai as dai
    DEPTHAI_AVAILABLE = True
except ImportError:
    DEPTHAI_AVAILABLE = False
    print("Error: DepthAI not available. Please install with: pip install depthai")
    sys.exit(1)


def setup_oakd_camera():
    """Set up OAKD camera pipeline"""
    # Create pipeline
    pipeline = dai.Pipeline()
    
    # Create RGB camera
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    cam_rgb.setPreviewSize(640, 480)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setInterleaved(False)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    
    # Create output
    try:
        xout_rgb = pipeline.create(dai.node.XLinkOut)
    except AttributeError:
        # Try alternative API format
        xout_rgb = pipeline.create(dai.XLinkOut)
    
    xout_rgb.setStreamName("rgb")
    
    # Linking
    cam_rgb.preview.link(xout_rgb.input)
    
    return pipeline


def main():
    """Main function"""
    print("=" * 60)
    print("OAKD Camera Simple Test")
    print("=" * 60)
    print("\nPress 'q' to quit\n")

    # CLI flag to explicitly opt into GUI. Default is headless-safe to avoid Qt aborts.
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", action="store_true", help="Enable GUI window (requires working X11/display)")
    args = parser.parse_args()

    display_env = os.environ.get("DISPLAY")
    headless = True  # default to headless unless user explicitly opts in
    if args.show and display_env:
        headless = False
        print(f"[INFO] GUI requested (--show). DISPLAY={display_env}. Attempting cv2.imshow.")
    else:
        print("[INFO] Running headless (no cv2.imshow).")
        if args.show and not display_env:
            print("[WARN] --show requested but DISPLAY is not set; staying headless.")
        print("       Use ssh -Y/-X with XQuartz and pass --show if you want the live video window.")
        print("       In headless mode, exit with Ctrl+C.")
    
    try:
        # Set up pipeline
        print("Setting up OAKD camera...")
        pipeline = setup_oakd_camera()
        
        # Connect to device
        print("Connecting to OAKD device...")
        device = dai.Device(pipeline)
        print("Connected!")
        
        # Get output queue
        rgb_queue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        
        print("\nCamera is running. Displaying video...")
        print("Press 'q' to quit\n")
        
        frame_count = 0
        
        while True:
            # Get frame from queue
            in_rgb = rgb_queue.tryGet()
            
            if in_rgb is not None:
                # Get frame
                frame = in_rgb.getCvFrame()
                
                # Add frame counter
                frame_count += 1
                cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, "Press 'q' to quit", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Display frame if GUI is available
                if not headless:
                    try:
                        cv2.imshow("OAKD Camera", frame)
                    except Exception as e:
                        print(f"[INFO] Disabling GUI (imshow failed): {e}")
                        headless = True
            
            # Check for quit
            key = cv2.waitKey(1) & 0xFF if not headless else -1
            if key == ord('q'):
                print("\nQuitting...")
                break
    
    except RuntimeError as e:
        if "permissions" in str(e).lower() or "X_LINK" in str(e):
            print("\n" + "=" * 60)
            print("ERROR: OAKD Camera Permission Issue")
            print("=" * 60)
            print("\nThe OAKD camera requires proper permissions.")
            print("\nOn Linux, you may need to set up udev rules:")
            print("  sudo wget -qO - https://raw.githubusercontent.com/luxonis/depthai/main/scripts/install_dependencies.sh | bash")
            print("\nOn macOS, you may need to grant camera permissions.")
            print("\nAlternatively, try running with sudo (not recommended):")
            print("  sudo python test_oakd_simple.py")
            print("\n" + "=" * 60)
        else:
            print(f"\nError: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Cleanup
        if not headless:
            try:
                cv2.destroyAllWindows()
            except:
                pass
        if 'device' in locals():
            del device
        print("Cleanup complete!")


if __name__ == "__main__":
    main()
