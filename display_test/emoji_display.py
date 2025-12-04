"""
Emoji Display Utility for Raspberry Pi
Displays emoji on the Raspberry Pi screen using OpenCV
"""
import cv2
import numpy as np
import time
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from utils import is_gui_available, safe_imshow, safe_waitkey


class EmojiDisplay:
    """
    Display emoji on Raspberry Pi screen using OpenCV
    """
    def __init__(self, width=800, height=480, fullscreen=False):
        """
        Initialize emoji display
        
        Args:
            width: Screen width (default: 800 for common Pi displays)
            height: Screen height (default: 480 for common Pi displays)
            fullscreen: If True, try to use fullscreen mode
        """
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.window_name = "Emoji Display"
        
        # Common emoji unicode characters
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
            'clap': '👏',
            'ok': '👌',
            'victory': '✌️',
            'love': '💕',
            'party': '🎉',
            'sun': '☀️',
            'moon': '🌙',
            'earth': '🌍',
            'check': '✅',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
    
    def create_emoji_frame(self, emoji_text, text_color=(255, 255, 255), 
                          bg_color=(30, 30, 30), font_size=10):
        """
        Create a frame with emoji displayed
        
        Args:
            emoji_text: Emoji character or text to display
            text_color: Text color (BGR)
            bg_color: Background color (BGR)
            font_size: Font size multiplier
            
        Returns:
            numpy.ndarray: Frame with emoji
        """
        # Create blank frame
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:] = bg_color
        
        # Draw emoji in center
        # Note: OpenCV doesn't support emoji directly, so we'll use text rendering
        # For better emoji support, we might need PIL/Pillow
        
        try:
            # Try using PIL for emoji support
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np
            
            # Create PIL image
            pil_image = Image.new('RGB', (self.width, self.height), 
                                color=(bg_color[2], bg_color[1], bg_color[0]))
            draw = ImageDraw.Draw(pil_image)
            
            # Try to use a font that supports emoji
            try:
                # Try to load a system font that supports emoji
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 
                                         size=font_size * 40)
            except:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 
                                             size=font_size * 40)
                except:
                    font = ImageFont.load_default()
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), emoji_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center the text
            x = (self.width - text_width) // 2
            y = (self.height - text_height) // 2
            
            # Draw emoji
            draw.text((x, y), emoji_text, font=font, 
                     fill=(text_color[2], text_color[1], text_color[0]))
            
            # Convert PIL image to OpenCV format
            frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
        except ImportError:
            # Fallback: Use OpenCV text (won't show emoji properly)
            text = emoji_text if len(emoji_text) < 20 else emoji_text[:17] + "..."
            font_scale = font_size * 2
            thickness = 3
            
            # Get text size
            (text_width, text_height), baseline = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            
            # Center the text
            x = (self.width - text_width) // 2
            y = (self.height + text_height) // 2
            
            # Draw text
            cv2.putText(frame, text, (x, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness)
        
        return frame
    
    def show_emoji(self, emoji_key, duration=2.0):
        """
        Display an emoji for a specified duration
        
        Args:
            emoji_key: Key from self.emojis dictionary
            duration: How long to display (seconds)
        """
        emoji_text = self.emojis.get(emoji_key, emoji_key)
        frame = self.create_emoji_frame(emoji_text)
        
        # Display
        if self.fullscreen:
            cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, 
                                cv2.WINDOW_FULLSCREEN)
        else:
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_name, self.width, self.height)
        
        start_time = time.time()
        while time.time() - start_time < duration:
            safe_imshow(self.window_name, frame, check_gui=False)
            key = safe_waitkey(1)
            if key == ord('q') or key == 27:  # 'q' or ESC
                break
        
        return frame
    
    def animate_emojis(self, emoji_keys, delay=1.0, loop=True):
        """
        Animate through multiple emojis
        
        Args:
            emoji_keys: List of emoji keys to display
            delay: Delay between emojis (seconds)
            loop: If True, loop indefinitely
        """
        if self.fullscreen:
            cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, 
                                cv2.WINDOW_FULLSCREEN)
        else:
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_name, self.width, self.height)
        
        while True:
            for emoji_key in emoji_keys:
                emoji_text = self.emojis.get(emoji_key, emoji_key)
                frame = self.create_emoji_frame(emoji_text, font_size=8)
                
                start_time = time.time()
                while time.time() - start_time < delay:
                    safe_imshow(self.window_name, frame, check_gui=False)
                    key = safe_waitkey(1)
                    if key == ord('q') or key == 27:  # 'q' or ESC
                        cv2.destroyAllWindows()
                        return
                
            if not loop:
                break
        
        cv2.destroyAllWindows()
    
    def show_text_with_emoji(self, text, emoji_key=None, font_size=2):
        """
        Show text with optional emoji
        
        Args:
            text: Text to display
            emoji_key: Optional emoji key to add
            font_size: Font size multiplier
        """
        if emoji_key:
            emoji_text = self.emojis.get(emoji_key, '')
            display_text = f"{emoji_text} {text} {emoji_text}"
        else:
            display_text = text
        
        frame = self.create_emoji_frame(display_text, font_size=font_size)
        
        if self.fullscreen:
            cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, 
                                cv2.WINDOW_FULLSCREEN)
        else:
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_name, self.width, self.height)
        
        safe_imshow(self.window_name, frame, check_gui=False)
        return frame


def main():
    """Test emoji display"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Display emoji on Raspberry Pi')
    parser.add_argument('--emoji', type=str, default='smile',
                       help='Emoji to display (default: smile)')
    parser.add_argument('--fullscreen', action='store_true',
                       help='Use fullscreen mode')
    parser.add_argument('--width', type=int, default=800,
                       help='Screen width (default: 800)')
    parser.add_argument('--height', type=int, default=480,
                       help='Screen height (default: 480)')
    parser.add_argument('--animate', action='store_true',
                       help='Animate through multiple emojis')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between emojis in animation (default: 1.0)')
    
    args = parser.parse_args()
    
    # Check display first
    print("Checking display...")
    from display_check import print_display_summary
    info, mode = print_display_summary()
    
    if not info['available'] and not info['framebuffer']:
        print("Warning: No display detected. Continuing anyway...")
    
    # Create emoji display
    display = EmojiDisplay(width=args.width, height=args.height, 
                          fullscreen=args.fullscreen)
    
    print(f"\nDisplaying emoji: {args.emoji}")
    print("Press 'q' or ESC to quit\n")
    
    if args.animate:
        # Animate through common emojis
        emoji_list = ['smile', 'heart', 'thumbs_up', 'wave', 'rocket', 
                     'car', 'robot', 'star', 'fire', 'party']
        display.animate_emojis(emoji_list, delay=args.delay)
    else:
        # Display single emoji
        frame = display.show_emoji(args.emoji, duration=999999)  # Display until keypress
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

