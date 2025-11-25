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
        Detect hand gesture from frame
        
        Args:
            frame: BGR image frame
            
        Returns:
            tuple: (gesture, annotated_frame)
                - gesture: Gesture enum (ROCK, PAPER, SCISSORS, or NONE)
                - annotated_frame: Frame with hand landmarks drawn
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        annotated_frame = frame.copy()
        gesture = Gesture.NONE
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
                
                # Classify gesture
                gesture = self._classify_gesture(hand_landmarks)
        
        return gesture, annotated_frame
    
    def _classify_gesture(self, landmarks):
        """
        Classify hand gesture based on finger positions
        
        Args:
            landmarks: MediaPipe hand landmarks
            
        Returns:
            Gesture enum
        """
        # Get finger tip and joint positions
        # Thumb: 4, Index: 8, Middle: 12, Ring: 16, Pinky: 20
        # MCP joints: Thumb: 2, Index: 5, Middle: 9, Ring: 13, Pinky: 17
        
        thumb_tip = landmarks.landmark[4]
        thumb_mcp = landmarks.landmark[2]
        
        index_tip = landmarks.landmark[8]
        index_pip = landmarks.landmark[6]
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
        
        # Check if fingers are extended
        # Finger is extended if tip y is less than pip y (for most fingers)
        # Thumb detection: use wrist to determine hand orientation
        wrist = landmarks.landmark[0]
        
        fingers_extended = []
        
        # Thumb: check if it's extended based on hand orientation
        # For right hand: thumb tip x > thumb mcp x
        # For left hand: thumb tip x < thumb mcp x
        # Use wrist position relative to thumb to determine orientation
        is_right_hand = wrist.x < thumb_mcp.x  # Wrist is typically to the left of thumb MCP for right hand
        if is_right_hand:
            thumb_extended = thumb_tip.x > thumb_mcp.x
        else:
            thumb_extended = thumb_tip.x < thumb_mcp.x
        fingers_extended.append(1 if thumb_extended else 0)
        
        # Index finger
        if index_tip.y < index_pip.y:
            fingers_extended.append(1)
        else:
            fingers_extended.append(0)
        
        # Middle finger
        if middle_tip.y < middle_pip.y:
            fingers_extended.append(1)
        else:
            fingers_extended.append(0)
        
        # Ring finger
        if ring_tip.y < ring_pip.y:
            fingers_extended.append(1)
        else:
            fingers_extended.append(0)
        
        # Pinky
        if pinky_tip.y < pinky_pip.y:
            fingers_extended.append(1)
        else:
            fingers_extended.append(0)
        
        # Classify based on extended fingers
        total_extended = sum(fingers_extended)
        
        if total_extended == 0:
            # All fingers closed = Rock
            return Gesture.ROCK
        elif total_extended == 5:
            # All fingers open = Paper
            return Gesture.PAPER
        elif total_extended == 2 and fingers_extended[1] == 1 and fingers_extended[2] == 1:
            # Index and middle extended = Scissors
            return Gesture.SCISSORS
        else:
            # Unclear gesture
            return Gesture.NONE
    
    def release(self):
        """Release resources"""
        self.hands.close()

