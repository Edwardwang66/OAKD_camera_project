#!/usr/bin/env python3
"""
Quick display test script
Checks display and shows a test emoji
"""
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from display_check import print_display_summary
from emoji_display import EmojiDisplay
import cv2

# Import safe functions
from utils import safe_imshow, safe_waitkey

def main():
    print("=" * 60)
    print("Raspberry Pi Display Test")
    print("=" * 60)
    
    # Check display
    info, mode = print_display_summary()
    
    if not info.get('available') and not info.get('framebuffer'):
        print("⚠️  Warning: No display detected!")
        print("   The program will still try to run, but may not display windows.")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    print("\n" + "=" * 60)
    print("Displaying Test Emoji")
    print("=" * 60)
    print("\nAvailable emojis:")
    print("  1. 😊 smile")
    print("  2. ❤️ heart")
    print("  3. 👍 thumbs_up")
    print("  4. 👋 wave")
    print("  5. 🚀 rocket")
    print("  6. 🚗 car")
    print("  7. 🤖 robot")
    print("  8. ⭐ star")
    print("  9. 🔥 fire")
    print(" 10. 🎉 party")
    print("\nPress number to select, or 'q' to quit")
    print("=" * 60)
    
    display = EmojiDisplay(width=800, height=480)
    
    emoji_map = {
        '1': 'smile',
        '2': 'heart',
        '3': 'thumbs_up',
        '4': 'wave',
        '5': 'rocket',
        '6': 'car',
        '7': 'robot',
        '8': 'star',
        '9': 'fire',
        '10': 'party'
    }
    
    cv2.namedWindow("Emoji Display", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Emoji Display", 800, 480)
    
    current_emoji = 'smile'
    frame = display.show_emoji(current_emoji, duration=0.1)  # Just create frame
    
    print(f"\nCurrently showing: {current_emoji}")
    print("Press number (1-10) to change emoji, 'a' for animation, 'q' to quit\n")
    
    animating = False
    
    while True:
        if not animating:
            frame = display.create_emoji_frame(
                display.emojis.get(current_emoji, current_emoji), 
                font_size=8
            )
        
        safe_imshow("Emoji Display", frame, check_gui=False)
        
        key = safe_waitkey(1) & 0xFF
        
        if key == ord('q') or key == 27:
            break
        elif key == ord('a'):
            animating = not animating
            if animating:
                print("Animation mode: Press 'a' again to stop")
                emoji_list = ['smile', 'heart', 'thumbs_up', 'wave', 'rocket', 
                             'car', 'robot', 'star', 'fire', 'party']
                display.animate_emojis(emoji_list, delay=0.8, loop=True)
                animating = False
                current_emoji = 'smile'
        elif chr(key) in emoji_map:
            current_emoji = emoji_map[chr(key)]
            print(f"Switched to: {current_emoji}")
            animating = False
    
    cv2.destroyAllWindows()
    print("\nDisplay test complete!")


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
        cv2.destroyAllWindows()

