"""
Pistol Gesture Detector
Detects pistol/gun pointing gestures and determines shooting direction
"""
import cv2
import mediapipe as mp
import numpy as np
from enum import Enum


class PlayerSide(Enum):
    LEFT = "left"
    RIGHT = "right"
    NONE = "none"


class PistolDetector:
    def __init__(self):
        """Initialize MediaPipe hand detection for pistol gesture"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  # Detect up to 2 hands (2 players)
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
    
    def detect_pistol_gestures(self, frame):
        """
        Detect pistol gestures from frame and determine shooting direction
        
        Args:
            frame: BGR image frame
            
        Returns:
            dict: {
                'player_a': {'has_pistol': bool, 'pointing_at': PlayerSide, 'position': (x, y)},
                'player_b': {'has_pistol': bool, 'pointing_at': PlayerSide, 'position': (x, y)},
                'annotated_frame': frame with landmarks drawn
            }
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        annotated_frame = frame.copy()
        
        # Initialize player states
        players = {
            'player_a': {'has_pistol': False, 'pointing_at': PlayerSide.NONE, 'position': None},
            'player_b': {'has_pistol': False, 'pointing_at': PlayerSide.NONE, 'position': None}
        }
        
        if results.multi_hand_landmarks:
            hand_positions = []
            
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
                
                # Check if this is a pistol gesture
                is_pistol = self._is_pistol_gesture(hand_landmarks)
                
                if is_pistol:
                    # Get hand position and determine which side of screen
                    h, w = frame.shape[:2]
                    wrist = hand_landmarks.landmark[0]
                    hand_x = int(wrist.x * w)
                    
                    # Get index finger tip for direction
                    index_tip = hand_landmarks.landmark[8]
                    index_x = int(index_tip.x * w)
                    index_y = int(index_tip.y * h)
                    
                    # Determine which player (left or right side of screen)
                    player_side = PlayerSide.LEFT if hand_x < w / 2 else PlayerSide.RIGHT
                    
                    # Determine shooting direction based on index finger direction
                    pointing_at = self._determine_shooting_direction(
                        hand_landmarks, hand_x, w
                    )
                    
                    hand_positions.append({
                        'x': hand_x,
                        'y': int(wrist.y * h),
                        'side': player_side,
                        'pointing_at': pointing_at,
                        'index_pos': (index_x, index_y)
                    })
            
            # Assign to players based on position
            if len(hand_positions) > 0:
                # Sort by x position (left to right)
                hand_positions.sort(key=lambda p: p['x'])
                
                if len(hand_positions) >= 1:
                    # Player A (left side)
                    p1 = hand_positions[0]
                    players['player_a'] = {
                        'has_pistol': True,
                        'pointing_at': p1['pointing_at'],
                        'position': (p1['x'], p1['y']),
                        'index_pos': p1['index_pos']
                    }
                
                if len(hand_positions) >= 2:
                    # Player B (right side)
                    p2 = hand_positions[1]
                    players['player_b'] = {
                        'has_pistol': True,
                        'pointing_at': p2['pointing_at'],
                        'position': (p2['x'], p2['y']),
                        'index_pos': p2['index_pos']
                    }
        
        players['annotated_frame'] = annotated_frame
        return players
    
    def _is_pistol_gesture(self, landmarks):
        """
        Check if hand gesture is a pistol (index finger extended, thumb up, others closed)
        
        Args:
            landmarks: MediaPipe hand landmarks
            
        Returns:
            bool: True if pistol gesture detected
        """
        # Get finger positions
        thumb_tip = landmarks.landmark[4]
        thumb_ip = landmarks.landmark[3]
        thumb_mcp = landmarks.landmark[2]
        
        index_tip = landmarks.landmark[8]
        index_pip = landmarks.landmark[6]
        index_mcp = landmarks.landmark[5]
        
        middle_tip = landmarks.landmark[12]
        middle_pip = landmarks.landmark[10]
        
        ring_tip = landmarks.landmark[16]
        ring_pip = landmarks.landmark[14]
        
        pinky_tip = landmarks.landmark[20]
        pinky_pip = landmarks.landmark[18]
        
        wrist = landmarks.landmark[0]
        
        # Check thumb (should be extended/up)
        # For right hand: thumb tip x > thumb mcp x
        # For left hand: thumb tip x < thumb mcp x
        is_right_hand = wrist.x < thumb_mcp.x
        if is_right_hand:
            thumb_extended = thumb_tip.x > thumb_mcp.x
        else:
            thumb_extended = thumb_tip.x < thumb_mcp.x
        
        # Index finger should be extended
        index_extended = index_tip.y < index_pip.y
        
        # Middle, ring, and pinky should be closed
        middle_closed = middle_tip.y > middle_pip.y
        ring_closed = ring_tip.y > ring_pip.y
        pinky_closed = pinky_tip.y > pinky_pip.y
        
        # Pistol gesture: thumb up, index extended, others closed
        is_pistol = (thumb_extended and index_extended and 
                    middle_closed and ring_closed and pinky_closed)
        
        return is_pistol
    
    def _determine_shooting_direction(self, landmarks, hand_x, frame_width):
        """
        Determine which direction the pistol is pointing
        
        Args:
            landmarks: MediaPipe hand landmarks
            hand_x: X coordinate of hand
            frame_width: Width of the frame
            
        Returns:
            PlayerSide: Which side the pistol is pointing at
        """
        # Get index finger tip and base
        index_tip = landmarks.landmark[8]
        index_mcp = landmarks.landmark[5]
        
        # Calculate direction vector
        direction_x = index_tip.x - index_mcp.x
        
        # Determine pointing direction
        # If pointing right (positive direction), likely pointing at right side
        # If pointing left (negative direction), likely pointing at left side
        threshold = 0.05  # Threshold for direction detection
        
        if direction_x > threshold:
            return PlayerSide.RIGHT
        elif direction_x < -threshold:
            return PlayerSide.LEFT
        else:
            return PlayerSide.NONE
    
    def release(self):
        """Release resources"""
        self.hands.close()

