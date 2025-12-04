"""
Hand Gesture Detector using MediaPipe and OpenCV
Detects and classifies hand gestures as Rock, Paper, or Scissors
"""
import cv2
import mediapipe as mp
import numpy as np
from enum import Enum


class Gesture(Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"
    NONE = "none"


class HandGestureDetector:
    def __init__(self):
        """Initialize MediaPipe hand detection"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
    
    def detect_gesture(self, frame):
        """
        Detect hand gesture from frame using MediaPipe hand pose landmarks
        
        Args:
            frame: BGR image frame
            
        Returns:
            tuple: (gesture, annotated_frame)
                - gesture: Gesture enum (ROCK, PAPER, SCISSORS, or NONE)
                - annotated_frame: Frame with hand landmarks and gesture label drawn
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        annotated_frame = frame.copy()
        gesture = Gesture.NONE
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks (pose visualization)
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )
                
                # Classify gesture based on pose/keypoints
                gesture = self._classify_gesture(hand_landmarks)
                
                # Draw gesture label on frame
                if gesture != Gesture.NONE:
                    # Get wrist position for label placement
                    wrist = hand_landmarks.landmark[0]
                    h, w = frame.shape[:2]
                    label_x = int(wrist.x * w)
                    label_y = int(wrist.y * h) - 30
                    
                    # Draw gesture label
                    cv2.putText(annotated_frame, gesture.value.upper(), 
                               (label_x, label_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        
        return gesture, annotated_frame
    
    def _classify_gesture(self, landmarks):
        """
        Classify hand gesture based on finger pose/keypoints (not bounding box)
        Uses MediaPipe hand landmarks to determine finger positions
        
        Args:
            landmarks: MediaPipe hand landmarks (21 keypoints)
            
        Returns:
            Gesture enum
        """
        # MediaPipe hand landmark indices:
        # Wrist: 0
        # Thumb: 1-4 (tip at 4)
        # Index: 5-8 (tip at 8)
        # Middle: 9-12 (tip at 12)
        # Ring: 13-16 (tip at 16)
        # Pinky: 17-20 (tip at 20)
        
        # Get key landmark positions
        wrist = landmarks.landmark[0]
        thumb_tip = landmarks.landmark[4]
        thumb_ip = landmarks.landmark[3]  # Interphalangeal joint
        thumb_mcp = landmarks.landmark[2]  # Metacarpophalangeal joint
        
        index_tip = landmarks.landmark[8]
        index_pip = landmarks.landmark[6]  # Proximal interphalangeal
        index_mcp = landmarks.landmark[5]
        
        middle_tip = landmarks.landmark[12]
        middle_pip = landmarks.landmark[10]
        middle_mcp = landmarks.landmark[9]
        
        ring_tip = landmarks.landmark[16]
        ring_pip = landmarks.landmark[14]
        ring_mcp = landmarks.landmark[13]
        
        pinky_tip = landmarks.landmark[20]
        pinky_pip = landmarks.landmark[18]
        pinky_mcp = landmarks.landmark[17]
        
        # Determine if fingers are extended based on pose
        # A finger is extended if its tip is above (lower y value) its PIP joint
        fingers_extended = []
        
        # Thumb: Special case - check if extended outward (perpendicular to palm)
        # Use distance from thumb tip to index MCP to determine if thumb is extended
        thumb_to_index_mcp_dist = abs(thumb_tip.x - index_mcp.x)
        thumb_extended = thumb_to_index_mcp_dist > 0.05  # Threshold for thumb extension
        fingers_extended.append(1 if thumb_extended else 0)
        
        # Index finger: extended if tip is above PIP
        index_extended = index_tip.y < index_pip.y
        fingers_extended.append(1 if index_extended else 0)
        
        # Middle finger: extended if tip is above PIP
        middle_extended = middle_tip.y < middle_pip.y
        fingers_extended.append(1 if middle_extended else 0)
        
        # Ring finger: extended if tip is above PIP
        ring_extended = ring_tip.y < ring_pip.y
        fingers_extended.append(1 if ring_extended else 0)
        
        # Pinky: extended if tip is above PIP
        pinky_extended = pinky_tip.y < pinky_pip.y
        fingers_extended.append(1 if pinky_extended else 0)
        
        # Classify gesture based on finger pose
        total_extended = sum(fingers_extended)
        thumb, index, middle, ring, pinky = fingers_extended
        
        # Rock: All fingers closed (fist)
        if total_extended == 0:
            return Gesture.ROCK
        
        # Paper: All fingers extended (open hand)
        elif total_extended == 5:
            return Gesture.PAPER
        
        # Scissors: Only index and middle fingers extended
        elif total_extended == 2 and index == 1 and middle == 1:
            return Gesture.SCISSORS
        
        # Alternative Scissors: Index and middle extended, others closed
        # (More lenient - allows thumb to be slightly extended)
        elif total_extended <= 3 and index == 1 and middle == 1 and ring == 0 and pinky == 0:
            return Gesture.SCISSORS
        
        # Unclear gesture - return NONE
        else:
            return Gesture.NONE
    
    def release(self):
        """Release resources"""
        self.hands.close()

