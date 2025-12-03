"""
Utility functions for the OAKD Camera Project
Includes GUI availability checks for headless/SSH operation
"""
import os
import sys

# Note: We don't set QT_QPA_PLATFORM=offscreen here because OpenCV's Qt plugin
# may not have that backend. Instead, we catch Qt errors gracefully at runtime.


def is_gui_available():
    """
    Check if OpenCV GUI is available (X11 forwarding or local display)
    
    Returns:
        bool: True if GUI is available, False otherwise
    """
    # Check if DISPLAY environment variable is set
    display = os.environ.get("DISPLAY")
    if display is None:
        return False
    
    # Try to import cv2 and check if GUI backend is available
    try:
        import cv2
        # Try to create a test window (will fail if no GUI)
        # We'll use a simpler check - just verify DISPLAY is set
        # The actual imshow will handle the error gracefully
        return True
    except ImportError:
        return False


def safe_imshow(window_name, image, check_gui=True):
    """
    Safely display an image using cv2.imshow with headless mode support
    
    Args:
        window_name: Name of the window
        image: Image to display
        check_gui: If True, check GUI availability first
        
    Returns:
        bool: True if image was displayed, False if skipped
    """
    if check_gui and not is_gui_available():
        return False
    
    try:
        import cv2
        # Try to use GTK backend if available (better X11 compatibility)
        # If this fails, OpenCV will try other backends
        try:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        except:
            pass  # Window might already exist or backend issue
        cv2.imshow(window_name, image)
        return True
    except Exception as e:
        error_str = str(e).lower()
        # Catch Qt/QPA errors and X11 connection errors
        if any(keyword in error_str for keyword in [
            "cannot connect to x server", "display", "no display", 
            "qt.qpa", "qt platform", "xcb", "could not connect to display"
        ]):
            return False
        # Suppress Qt errors silently
        if "qt" in error_str and "plugin" in error_str:
            return False
        # Other errors, let them propagate
        raise


def safe_waitkey(delay=1):
    """
    Safely wait for key press with headless mode support
    
    Args:
        delay: Delay in milliseconds (0 = wait indefinitely)
        
    Returns:
        int: Key code, or -1 if GUI not available
    """
    if not is_gui_available():
        return -1
    
    try:
        import cv2
        return cv2.waitKey(delay) & 0xFF
    except Exception:
        return -1


def print_gui_warning():
    """Print a friendly warning when GUI is not available"""
    print("\n" + "=" * 60)
    print("[WARNING] OpenCV GUI is not available!")
    print("=" * 60)
    print("The application will run without displaying windows.")
    print("\nTo enable GUI display:")
    print("  1. On Mac: Install XQuartz and enable 'Allow connections from network clients'")
    print("  2. Connect via SSH with X11 forwarding:")
    print("     ssh -Y pi@raspberrypi.local")
    print("     or")
    print("     ssh -X pi@raspberrypi.local")
    print("  3. Make sure XQuartz is running before SSH connection")
    print("\nThe camera and processing will continue to work without GUI.")
    print("=" * 60 + "\n")

