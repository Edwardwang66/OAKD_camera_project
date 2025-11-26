"""
Hand Gesture Detector using Trained PyTorch Model
Uses MediaPipe for hand detection (bounding box) then model for classification
Replaces MediaPipe classification with the trained model from ECE176_final
Supports OAKD Edge AI mode
"""
import cv2
import numpy as np
from enum import Enum
import mediapipe as mp
from model_loader import ModelGestureDetector, Gesture
import os


class HandGestureDetectorModel:
    """
    Hand gesture detector using trained PyTorch model
    Uses MediaPipe to detect hand bounding box, then model for classification
    Compatible with the original HandGestureDetector interface
    """
    def __init__(self, model_path=None):
        """
        Initialize model-based gesture detector
        
        Args:
            model_path: Path to model file (rps_model_improved.pth or rps_model.pth)
        """
        print("Initializing model-based gesture detector...")
        self.model_detector = ModelGestureDetector(model_path=model_path)
        
        # Initialize MediaPipe for hand detection (bounding box)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        print("Model-based detector ready!")
    
    def _get_hand_bbox(self, frame):
        """
        Detect hand and return bounding box
        
        Args:
            frame: BGR image frame
            
        Returns:
            tuple: (bbox, landmarks) where bbox is (x, y, w, h) or None
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get bounding box from landmarks
                h, w = frame.shape[:2]
                x_coords = [lm.x * w for lm in hand_landmarks.landmark]
                y_coords = [lm.y * h for lm in hand_landmarks.landmark]
                
                x_min = int(min(x_coords))
                x_max = int(max(x_coords))
                y_min = int(min(y_coords))
                y_max = int(max(y_coords))
                
                # Add padding
                padding = 20
                x = max(0, x_min - padding)
                y = max(0, y_min - padding)
                width = min(w - x, x_max - x_min + 2 * padding)
                height = min(h - y, y_max - y_min + 2 * padding)
                
                return (x, y, width, height), hand_landmarks
        
        return None, None
    
    def detect_gesture(self, frame):
        """
        Detect hand gesture from frame
        Uses MediaPipe to find hand bounding box, then model for classification
        
        Args:
            frame: BGR image frame
            
        Returns:
            tuple: (gesture, annotated_frame, bbox)
                - gesture: Gesture enum (ROCK, PAPER, SCISSORS, or NONE)
                - annotated_frame: Frame with detection info and bounding box
                - bbox: Hand bounding box (x, y, w, h) or None
        """
        annotated_frame = frame.copy()
        
        # Get hand bounding box using MediaPipe
        bbox, landmarks = self._get_hand_bbox(frame)
        
        # Draw bounding box if detected
        if bbox is not None:
            x, y, w, h = bbox
            cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(annotated_frame, "Hand", (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Draw hand landmarks if detected
        if landmarks:
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )
        
        # Use model to classify gesture (with bounding box)
        gesture, confidence, annotated_frame = self.model_detector.detect_gesture(
            frame, confidence_threshold=0.5, hand_bbox=bbox
        )
        
        # Return gesture, annotated_frame, and bounding box
        return gesture, annotated_frame, bbox, bbox
    
    def release(self):
        """Release resources"""
        self.model_detector.release()
        self.hands.close()

