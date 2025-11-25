"""
Finger Tracker for Air Drawing
Tracks index finger position using MediaPipe
"""
import cv2
import mediapipe as mp
import numpy as np


class FingerTracker:
    def __init__(self):
        """Initialize MediaPipe hand detection for finger tracking"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
    
    def get_index_finger_position(self, frame):
        """
        Get the index finger tip position from frame
        
        Args:
            frame: BGR image frame
            
        Returns:
            tuple: (x, y, is_detected, annotated_frame)
                - x, y: Normalized coordinates (0-1) or pixel coordinates
                - is_detected: True if finger is detected
                - annotated_frame: Frame with hand landmarks drawn
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        annotated_frame = frame.copy()
        x, y = None, None
        is_detected = False
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks (optional, for visualization)
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
                
                # Get index finger tip (landmark 8)
                index_tip = hand_landmarks.landmark[8]
                
                # Convert normalized coordinates to pixel coordinates
                h, w = frame.shape[:2]
                x = int(index_tip.x * w)
                y = int(index_tip.y * h)
                
                is_detected = True
                
                # Draw a circle at index finger tip
                cv2.circle(annotated_frame, (x, y), 10, (0, 255, 0), -1)
                cv2.circle(annotated_frame, (x, y), 15, (0, 255, 0), 2)
        
        return x, y, is_detected, annotated_frame
    
    def release(self):
        """Release resources"""
        self.hands.close()

