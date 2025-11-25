"""
Simple test script for laptop testing - Air Drawing
Tests finger tracking without full drawing functionality
"""
import cv2
from camera import Camera
from finger_tracker import FingerTracker


def test_finger_tracking():
    """Test finger tracking on laptop"""
    print("=" * 50)
    print("Laptop Test - Index Finger Tracking")
    print("=" * 50)
    print("\nInstructions:")
    print("1. Make sure your laptop webcam is working")
    print("2. Show your hand to the camera")
    print("3. Point your index finger")
    print("4. Move your finger around to see tracking")
    print("5. Press 'q' to quit\n")
    
    try:
        # Initialize camera (will fallback to webcam)
        camera = Camera(use_oakd=True)
        tracker = FingerTracker()
        
        print("Camera initialized. Point your index finger to test tracking...\n")
        
        while True:
            frame = camera.get_frame()
            if frame is None:
                continue
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Track index finger
            x, y, is_detected, annotated_frame = tracker.get_index_finger_position(frame)
            
            # Display tracking info
            if is_detected:
                status_text = f"Finger detected at ({x}, {y})"
                status_color = (0, 255, 0)
            else:
                status_text = "No finger detected"
                status_color = (0, 0, 255)
            
            cv2.putText(annotated_frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            cv2.putText(annotated_frame, "Point your index finger to track", 
                       (10, annotated_frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(annotated_frame, "Press 'q' to quit", 
                       (10, annotated_frame.shape[0] - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow("Finger Tracking Test", annotated_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        camera.release()
        tracker.release()
        cv2.destroyAllWindows()
        print("\nTest complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_finger_tracking()

