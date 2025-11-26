"""
Simple test script for laptop testing (uses webcam only)
This script doesn't require OAKD camera or DepthAI
Perfect for testing on your laptop before deploying to Raspberry Pi
"""
import cv2
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import is_gui_available, safe_imshow, safe_waitkey, print_gui_warning
from hand_gesture_detector import HandGestureDetector, Gesture


def test_webcam_gesture():
    """Test webcam and gesture detection on laptop"""
    print("=" * 50)
    print("Laptop Test - Hand Gesture Detection")
    print("=" * 50)
    print("\nInstructions:")
    print("1. Make sure your laptop webcam is working")
    print("2. Show your hand to the camera")
    print("3. Try these gestures:")
    print("   - ROCK: Close your fist (all fingers closed)")
    print("   - PAPER: Open your hand (all fingers extended)")
    print("   - SCISSORS: Extend index and middle fingers")
    print("4. Press 'q' to quit\n")
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Could not open webcam!")
        print("Make sure your webcam is connected and not being used by another application.")
        return
    
    # Set webcam resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Initialize gesture detector
    detector = HandGestureDetector()
    
    # Check GUI availability
    gui_available = is_gui_available()
    if not gui_available:
        print_gui_warning()
    
    print("Camera initialized. Show your hand to test gesture detection...\n")
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect gesture
            gesture, annotated_frame = detector.detect_gesture(frame)
            
            # Display gesture on frame
            gesture_text = f"Gesture: {gesture.value.upper()}"
            color = (0, 255, 0) if gesture != Gesture.NONE else (0, 0, 255)
            
            cv2.putText(annotated_frame, gesture_text, 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # Add instructions
            cv2.putText(annotated_frame, "ROCK: Fist | PAPER: Open | SCISSORS: Two fingers", 
                       (10, annotated_frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(annotated_frame, "Press 'q' to quit", 
                       (10, annotated_frame.shape[0] - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            if gui_available:
                safe_imshow("Laptop Test - Gesture Detection", annotated_frame)
            
            # Print gesture every 30 frames to avoid spam
            if frame_count % 30 == 0 and gesture != Gesture.NONE:
                print(f"Detected: {gesture.value.upper()}")
            
            frame_count += 1
            
            key = safe_waitkey(1)
            if key == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cap.release()
        detector.release()
        if gui_available:
            try:
                cv2.destroyAllWindows()
            except:
                pass
        print("\nTest complete!")


if __name__ == "__main__":
    test_webcam_gesture()

