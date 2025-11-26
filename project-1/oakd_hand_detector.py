"""
OAKD Hand Detection with Bounding Boxes
Detects hands and returns bounding boxes for gesture classification
"""
import cv2
import numpy as np
import mediapipe as mp


class OAKDHandDetector:
    """
    Hand detector that works with OAKD camera
    Uses MediaPipe for hand detection and returns bounding boxes
    """
    def __init__(self):
        """Initialize hand detector"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
    
    def detect_hand_bbox(self, frame):
        """
        Detect hand and return bounding box
        
        Args:
            frame: BGR image frame
            
        Returns:
            tuple: (bbox, landmarks, annotated_frame)
                - bbox: (x, y, w, h) bounding box or None
                - landmarks: MediaPipe hand landmarks or None
                - annotated_frame: Frame with annotations
        """
        annotated_frame = frame.copy()
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        bbox = None
        landmarks = None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = hand_landmarks
                
                # Get bounding box from landmarks
                h, w = frame.shape[:2]
                x_coords = [lm.x * w for lm in hand_landmarks.landmark]
                y_coords = [lm.y * h for lm in hand_landmarks.landmark]
                
                x_min = int(min(x_coords))
                x_max = int(max(x_coords))
                y_min = int(min(y_coords))
                y_max = int(max(y_coords))
                
                # Add padding
                padding = 30
                x = max(0, x_min - padding)
                y = max(0, y_min - padding)
                width = min(w - x, x_max - x_min + 2 * padding)
                height = min(h - y, y_max - y_min + 2 * padding)
                
                bbox = (x, y, width, height)
                
                # Draw bounding box
                cv2.rectangle(annotated_frame, (x, y), (x+width, y+height), (0, 255, 0), 2)
                
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
                
                # Draw label
                cv2.putText(annotated_frame, "Hand Detected", (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return bbox, landmarks, annotated_frame
    
    def crop_hand_region(self, frame, bbox):
        """
        Crop hand region from frame using bounding box
        
        Args:
            frame: BGR image frame
            bbox: Bounding box (x, y, w, h)
            
        Returns:
            numpy.ndarray: Cropped hand region or None
        """
        if bbox is None:
            return None
        
        x, y, w, h = bbox
        cropped = frame[y:y+h, x:x+w]
        return cropped
    
    def release(self):
        """Release resources"""
        self.hands.close()

