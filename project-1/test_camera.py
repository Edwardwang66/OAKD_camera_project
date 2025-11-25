"""
Simple test script to verify camera and gesture detection are working
Run this before running the full game to test your setup
"""
import cv2
from oakd_camera import OAKDCamera
from hand_gesture_detector import HandGestureDetector, Gesture


def test_camera_and_gesture():
    """Test camera and gesture detection"""
    print("Testing camera and gesture detection...")
    print("Press 'q' to quit")
    
    try:
        # Initialize camera (will fallback to webcam if OAKD not available)
        camera = OAKDCamera(use_oakd=True)
        detector = HandGestureDetector()
        
        print("Camera initialized. Show your hand to test gesture detection.")
        
        while True:
            frame = camera.get_frame()
            if frame is None:
                continue
            
            # Detect gesture
            gesture, annotated_frame = detector.detect_gesture(frame)
            
            # Display gesture on frame
            cv2.putText(annotated_frame, f"Gesture: {gesture.value.upper()}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow("Camera Test - Gesture Detection", annotated_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        camera.release()
        detector.release()
        cv2.destroyAllWindows()
        print("Test complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_camera_and_gesture()

