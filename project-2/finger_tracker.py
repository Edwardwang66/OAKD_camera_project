"""
Finger Tracker for Air Drawing
Detects fist (stop drawing) vs index finger (draw) using MediaPipe
"""
import cv2
import mediapipe as mp
import numpy as np
from enum import Enum


class DrawingGesture(Enum):
    FIST = "fist"  # Stop drawing
    INDEX_FINGER = "index_finger"  # Draw
    NONE = "none"  # No hand detected


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
    
    def _detect_gesture(self, hand_landmarks):
        """
        Detect if hand is making a fist or pointing with index finger
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            DrawingGesture enum
        """
        # Get finger positions
        thumb_tip = hand_landmarks.landmark[4]
        thumb_ip = hand_landmarks.landmark[3]
        thumb_mcp = hand_landmarks.landmark[2]
        
        index_tip = hand_landmarks.landmark[8]
        index_pip = hand_landmarks.landmark[6]
        
        middle_tip = hand_landmarks.landmark[12]
        middle_pip = hand_landmarks.landmark[10]
        
        ring_tip = hand_landmarks.landmark[16]
        ring_pip = hand_landmarks.landmark[14]
        
        pinky_tip = hand_landmarks.landmark[20]
        pinky_pip = hand_landmarks.landmark[18]
        
        wrist = hand_landmarks.landmark[0]
        
        # Check thumb (for fist detection)
        is_right_hand = wrist.x < thumb_mcp.x
        if is_right_hand:
            thumb_extended = thumb_tip.x > thumb_mcp.x
        else:
            thumb_extended = thumb_tip.x < thumb_mcp.x
        
        # Check fingers
        index_extended = index_tip.y < index_pip.y
        middle_extended = middle_tip.y < middle_pip.y
        ring_extended = ring_tip.y < ring_pip.y
        pinky_extended = pinky_tip.y < pinky_pip.y
        
        # Fist: all fingers closed (including thumb)
        if not thumb_extended and not index_extended and not middle_extended and not ring_extended and not pinky_extended:
            return DrawingGesture.FIST
        
        # Index finger pointing: only index extended, others closed
        if index_extended and not middle_extended and not ring_extended and not pinky_extended:
            return DrawingGesture.INDEX_FINGER
        
        return DrawingGesture.NONE
    
    def get_finger_state(self, frame):
        """
        Get finger position and drawing state from frame
        
        Args:
            frame: BGR image frame
            
        Returns:
            tuple: (x, y, gesture, can_draw, annotated_frame)
                - x, y: Index finger position (pixel coordinates)
                - gesture: DrawingGesture enum
                - can_draw: True if should draw (index finger), False if fist
                - annotated_frame: Frame with annotations
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        annotated_frame = frame.copy()
        x, y = None, None
        gesture = DrawingGesture.NONE
        can_draw = False
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Detect gesture
                gesture = self._detect_gesture(hand_landmarks)
                
                # Get index finger tip (landmark 8)
                index_tip = hand_landmarks.landmark[8]
                
                # Convert normalized coordinates to pixel coordinates
                h, w = frame.shape[:2]
                x = int(index_tip.x * w)
                y = int(index_tip.y * h)
                
                # Determine if can draw
                can_draw = (gesture == DrawingGesture.INDEX_FINGER)
                
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
                
                # Draw indicator based on gesture
                if gesture == DrawingGesture.INDEX_FINGER:
                    # Green circle for drawing mode
                    cv2.circle(annotated_frame, (x, y), 12, (0, 255, 0), -1)
                    cv2.circle(annotated_frame, (x, y), 15, (0, 255, 0), 2)
                    cv2.putText(annotated_frame, "DRAWING", (x + 20, y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                elif gesture == DrawingGesture.FIST:
                    # Red circle for stop mode
                    cv2.circle(annotated_frame, (x, y), 12, (0, 0, 255), -1)
                    cv2.circle(annotated_frame, (x, y), 15, (0, 0, 255), 2)
                    cv2.putText(annotated_frame, "STOP", (x + 20, y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return x, y, gesture, can_draw, annotated_frame
    
    def release(self):
        """Release resources"""
        self.hands.close()

