"""
Emoji Display for Raspberry Pi Framebuffer
Direct framebuffer access without Qt dependencies
"""
import os
import sys
import numpy as np
import time

# Set environment before importing cv2
os.environ.setdefault('DISPLAY', ':0.0')
# Disable Qt to avoid crashes
os.environ.pop('QT_QPA_PLATFORM', None)
os.environ.setdefault('OPENCV_VIDEOIO_PRIORITY_LIST', 'V4L2,FFMPEG')

import cv2

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)


class FramebufferEmojiDisplay:
    """
    Display emoji directly to framebuffer (for Raspberry Pi)
    """
    def __init__(self, width=1024, height=600):
        """
        Initialize framebuffer emoji display
        
        Args:
            width: Display width
            height: Display height
        """
        self.width = width
        self.height = height
        self.window_name = "Emoji Display"
        
        # Emoji characters
        self.emojis = {
            'smile': '😊',
            'heart': '❤️',
            'thumbs_up': '👍',
            'wave': '👋',
            'rocket': '🚀',
            'car': '🚗',
            'robot': '🤖',
            'star': '⭐',
            'fire': '🔥',
            'party': '🎉',
            'check': '✅',
            'warning': '⚠️',
        }
        
        # Try to get actual resolution from framebuffer
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
                            print(f"Detected resolution: {self.width}x{self.height}")
                            break
        except Exception:
            pass
    
    def create_emoji_frame(self, emoji_text, bg_color=(20, 20, 30), font_size=8):
        """
        Create frame with emoji using PIL for proper rendering
        
        Args:
            emoji_text: Emoji character or text
            bg_color: Background color (BGR)
            font_size: Font size multiplier
            
        Returns:
            numpy.ndarray: Frame with emoji
        """
        # Create blank frame
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:] = bg_color
        
        # Try using PIL for emoji support
        try:
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np
            
            # Create PIL image
            pil_image = Image.new('RGB', (self.width, self.height), 
                                color=(bg_color[2], bg_color[1], bg_color[0]))
            draw = ImageDraw.Draw(pil_image)
            
            # Try to load emoji-capable font
            font_size_px = font_size * 60
            font = None
            
            # Try different fonts
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/System/Library/Fonts/Apple Color Emoji.ttc",
            ]
            
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, size=font_size_px)
                    break
                except:
                    continue
            
            if font is None:
                font = ImageFont.load_default()
            
            # Get text bounding box
            try:
                bbox = draw.textbbox((0, 0), emoji_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except:
                # Fallback
                bbox = draw.textbbox((0, 0), emoji_text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            
            # Center the text
            x = (self.width - text_width) // 2
            y = (self.height - text_height) // 2
            
            # Draw emoji/text
            draw.text((x, y), emoji_text, font=font, fill=(255, 255, 255))
            
            # Convert PIL image to OpenCV format
            frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
        except ImportError:
            # Fallback: Use OpenCV text (won't show emoji properly)
            text = str(emoji_text)[:20]
            font_scale = font_size * 2
            thickness = 4
            
            # Get text size
            (text_width, text_height), baseline = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            
            # Center the text
            x = (self.width - text_width) // 2
            y = (self.height + text_height) // 2
            
            # Draw text
            cv2.putText(frame, text, (x, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
        
        return frame
    
    def show_emoji(self, emoji_key, duration=0):
        """
        Display emoji on framebuffer
        
        Args:
            emoji_key: Key from self.emojis dictionary
            duration: Duration in seconds (0 = until keypress)
        """
        emoji_text = self.emojis.get(emoji_key, emoji_key)
        frame = self.create_emoji_frame(emoji_text)
        
        # Try to use fullscreen on framebuffer
        try:
            cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, 
                                cv2.WINDOW_FULLSCREEN)
        except:
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_name, self.width, self.height)
        
        start_time = time.time()
        while True:
            cv2.imshow(self.window_name, frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                break
            
            if duration > 0 and time.time() - start_time >= duration:
                break
        
        cv2.destroyAllWindows()


def main():
    """Test framebuffer emoji display"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Display emoji on Raspberry Pi framebuffer')
    parser.add_argument('--emoji', type=str, default='smile',
                       help='Emoji to display (default: smile)')
    parser.add_argument('--width', type=int, default=1024,
                       help='Display width (default: 1024)')
    parser.add_argument('--height', type=int, default=600,
                       help='Display height (default: 600)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Framebuffer Emoji Display")
    print("=" * 60)
    
    display = FramebufferEmojiDisplay(width=args.width, height=args.height)
    
    print(f"\nDisplaying emoji: {args.emoji}")
    print("Press 'q' or ESC to quit\n")
    
    display.show_emoji(args.emoji)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

