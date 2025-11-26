"""
Simple test script for laptop testing - Pistol Detection
Tests pistol gesture detection without full game
"""
import cv2
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import is_gui_available, safe_imshow, safe_waitkey, print_gui_warning
from camera import Camera
from pistol_detector import PistolDetector


def test_pistol_detection():
    """Test pistol detection on laptop"""
    print("=" * 60)
    print("Laptop Test - Pistol Gesture Detection")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Make a pistol gesture:")
    print("   - Extend your index finger")
    print("   - Extend your thumb upward")
    print("   - Keep other fingers closed")
    print("2. Point left or right to test direction detection")
    print("3. Press 'q' to quit\n")
    
    try:
        # Initialize camera (will fallback to webcam)
        camera = Camera(use_oakd=True)
        detector = PistolDetector()
        
        # Check GUI availability
        gui_available = is_gui_available()
        if not gui_available:
            print_gui_warning()
        
        print("Camera initialized. Make a pistol gesture to test...\n")
        
        while True:
            frame = camera.get_frame()
            if frame is None:
                continue
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect pistol gestures
            players = detector.detect_pistol_gestures(frame)
            player_a = players['player_a']
            player_b = players['player_b']
            annotated_frame = players['annotated_frame']
            
            # Display status
            status_y = 30
            
            if player_a['has_pistol']:
                status_text = f"Player A: PISTOL DETECTED - Pointing {player_a['pointing_at'].value.upper()}"
                status_color = (0, 255, 0)
            else:
                status_text = "Player A: No pistol"
                status_color = (100, 100, 100)
            
            cv2.putText(annotated_frame, status_text, (10, status_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
            
            if player_b['has_pistol']:
                status_text = f"Player B: PISTOL DETECTED - Pointing {player_b['pointing_at'].value.upper()}"
                status_color = (0, 255, 0)
            else:
                status_text = "Player B: No pistol"
                status_color = (100, 100, 100)
            
            cv2.putText(annotated_frame, status_text, (10, status_y + 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
            
            # Instructions
            cv2.putText(annotated_frame, "Make pistol: Index + Thumb up, others closed", 
                       (10, annotated_frame.shape[0] - 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(annotated_frame, "Press 'q' to quit", 
                       (10, annotated_frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            if gui_available:
                safe_imshow("Pistol Detection Test", annotated_frame)
            
            key = safe_waitkey(1)
            if key == ord('q'):
                break
        
        camera.release()
        detector.release()
        if gui_available:
            try:
                cv2.destroyAllWindows()
            except:
                pass
        print("\nTest complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_pistol_detection()

