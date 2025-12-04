#!/usr/bin/env python3
"""
Simple Emoji Display - Direct framebuffer access
Avoids Qt backend issues by using minimal OpenCV setup
"""
import os
import sys

# CRITICAL: Configure environment BEFORE any imports
# Remove DISPLAY to avoid X11/Qt issues
if 'DISPLAY' in os.environ:
    del os.environ['DISPLAY']

# Disable Qt
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ.pop('QT_QPA_PLATFORM', None)  # Remove it completely

import numpy as np
import cv2
import time

# Get framebuffer resolution
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

def create_emoji_frame(emoji, width, height):
    """Create frame with emoji"""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame.fill(20)  # Dark background
    
    # Try PIL for emoji
    try:
        from PIL import Image, ImageDraw, ImageFont
        pil_image = Image.new('RGB', (width, height), color=(20, 20, 30))
        draw = ImageDraw.Draw(pil_image)
        
        # Try to load font
        font_size = 300
        font = None
        for font_path in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]:
            try:
                font = ImageFont.truetype(font_path, size=font_size)
                break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
        
        # Get text size and center
        try:
            bbox = draw.textbbox((0, 0), emoji, font=font)
        except:
            bbox = draw.textbbox((0, 0), emoji)
        
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), emoji, font=font, fill=(255, 255, 255))
        frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    except:
        # Fallback: text only
        text = str(emoji)[:10]
        font_scale = 5
        thickness = 4
        (text_width, text_height), _ = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        x = (width - text_width) // 2
        y = (height + text_height) // 2
        cv2.putText(frame, text, (x, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
    
    return frame

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Display emoji on framebuffer')
    parser.add_argument('--emoji', type=str, default='😊', help='Emoji to display')
    args = parser.parse_args()
    
    width, height = get_framebuffer_resolution()
    print(f"Resolution: {width}x{height}")
    print(f"Displaying: {args.emoji}")
    print("Press 'q' to quit")
    
    frame = create_emoji_frame(args.emoji, width, height)
    
    window_name = "Emoji"
    try:
        cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    except:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, width, height)
    
    while True:
        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted")
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        cv2.destroyAllWindows()

