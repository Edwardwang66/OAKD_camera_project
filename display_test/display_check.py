"""
Display Check Utility for Raspberry Pi
Checks display availability and capabilities
"""
import os
import sys

def check_display():
    """
    Check if display is available on Raspberry Pi
    
    Returns:
        dict: Display information
    """
    display_info = {
        'available': False,
        'display_var': None,
        'framebuffer': False,
        'tty': False,
        'resolution': None
    }
    
    # Check DISPLAY environment variable
    display_var = os.environ.get('DISPLAY')
    display_info['display_var'] = display_var
    
    if display_var:
        display_info['available'] = True
        print(f"✓ DISPLAY variable set: {display_var}")
    else:
        print("✗ DISPLAY variable not set")
    
    # Check framebuffer (for Raspberry Pi with attached display)
    if os.path.exists('/dev/fb0'):
        display_info['framebuffer'] = True
        print("✓ Framebuffer device found: /dev/fb0")
        
        # Try to get resolution from framebuffer
        try:
            import subprocess
            result = subprocess.run(['fbset', '-s'], 
                                  capture_output=True, text=True, timeout=1)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'geometry' in line.lower():
                        parts = line.split()
                        if len(parts) >= 2:
                            display_info['resolution'] = f"{parts[1]}x{parts[2]}"
                            print(f"✓ Resolution: {display_info['resolution']}")
                            break
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
    else:
        print("✗ Framebuffer device not found")
    
    # Check if running on TTY (local console)
    try:
        tty = os.ttyname(sys.stdout.fileno())
        if tty and 'tty' in tty:
            display_info['tty'] = True
            print(f"✓ Running on TTY: {tty}")
    except (OSError, AttributeError):
        pass
    
    # Check OpenCV display capability
    try:
        import cv2
        # Try to create a test window
        try:
            cv2.namedWindow('__test__', cv2.WINDOW_NORMAL)
            cv2.destroyWindow('__test__')
            print("✓ OpenCV display backend available")
            display_info['opencv_available'] = True
        except Exception as e:
            print(f"✗ OpenCV display backend error: {e}")
            display_info['opencv_available'] = False
    except ImportError:
        print("✗ OpenCV not installed")
        display_info['opencv_available'] = False
    
    return display_info


def check_display_mode():
    """
    Determine display mode
    
    Returns:
        str: 'local', 'x11_forward', 'headless', or 'unknown'
    """
    display_var = os.environ.get('DISPLAY')
    
    if os.path.exists('/dev/fb0'):
        if display_var and 'localhost' in str(display_var):
            return 'x11_forward'  # X11 forwarding from remote
        elif display_var:
            return 'local'  # Local X display
        else:
            return 'local'  # Framebuffer (direct display)
    elif display_var:
        if 'localhost' in str(display_var):
            return 'x11_forward'  # X11 forwarding
        else:
            return 'local'  # X display
    else:
        return 'headless'  # No display


def print_display_summary():
    """Print a summary of display status"""
    print("\n" + "=" * 60)
    print("Display Check Summary")
    print("=" * 60)
    
    info = check_display()
    mode = check_display_mode()
    
    print(f"\nDisplay Mode: {mode.upper()}")
    if info['resolution']:
        print(f"Resolution: {info['resolution']}")
    
    print("\nStatus:")
    if info['available'] or info['framebuffer']:
        print("  ✓ Display is AVAILABLE")
    else:
        print("  ✗ Display is NOT AVAILABLE")
    
    if info.get('opencv_available'):
        print("  ✓ OpenCV can display windows")
    else:
        print("  ✗ OpenCV cannot display windows")
    
    print("=" * 60 + "\n")
    
    return info, mode


if __name__ == "__main__":
    print_display_summary()

