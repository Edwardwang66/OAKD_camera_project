"""
UI Display Module for 7-inch Screen
Creates a game interface using OpenCV to display on the Raspberry Pi screen
"""
import cv2
import numpy as np
from hand_gesture_detector import Gesture
from game_logic import GameResult


class GameUI:
    def __init__(self, screen_width=800, screen_height=480):
        """
        Initialize the game UI
        
        Args:
            screen_width: Width of the display screen
            screen_height: Height of the display screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.display_frame = None
    
    def create_display(self, camera_frame, player_gesture, ai_gesture, 
                      game_result, player_score, ai_score, round_count):
        """
        Create the game display frame
        
        Args:
            camera_frame: Frame from camera (will be resized)
            player_gesture: Player's detected gesture
            ai_gesture: AI's choice
            game_result: Result of the game (GameResult enum)
            player_score: Player's score
            ai_score: AI's score
            round_count: Current round number
            
        Returns:
            numpy.ndarray: Display frame ready to show
        """
        # Create blank display
        self.display_frame = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        self.display_frame.fill(30)  # Dark background
        
        # Layout: Camera feed on left, game info on right
        camera_width = int(self.screen_width * 0.6)
        info_width = self.screen_width - camera_width
        
        # Resize and place camera frame
        if camera_frame is not None:
            camera_resized = cv2.resize(camera_frame, (camera_width, self.screen_height))
            self.display_frame[:, :camera_width] = camera_resized
        
        # Draw dividing line
        cv2.line(self.display_frame, (camera_width, 0), 
                (camera_width, self.screen_height), (100, 100, 100), 2)
        
        # Draw game information panel
        info_x = camera_width + 20
        y_offset = 30
        
        # Title
        self._draw_text("ROCK PAPER SCISSORS", info_x, y_offset, 
                       font_scale=0.8, thickness=2, color=(255, 255, 255))
        y_offset += 50
        
        # Scores
        self._draw_text(f"Player: {player_score}", info_x, y_offset, 
                       font_scale=0.6, color=(100, 255, 100))
        y_offset += 35
        self._draw_text(f"Donkey Car: {ai_score}", info_x, y_offset, 
                       font_scale=0.6, color=(100, 100, 255))
        y_offset += 35
        self._draw_text(f"Round: {round_count}", info_x, y_offset, 
                       font_scale=0.5, color=(200, 200, 200))
        y_offset += 60
        
        # Player gesture
        self._draw_text("Your Choice:", info_x, y_offset, 
                       font_scale=0.5, color=(200, 200, 200))
        y_offset += 30
        player_text = player_gesture.value.upper() if player_gesture != Gesture.NONE else "WAITING..."
        player_color = (100, 255, 100) if player_gesture != Gesture.NONE else (150, 150, 150)
        self._draw_text(player_text, info_x, y_offset, 
                       font_scale=0.7, thickness=2, color=player_color)
        y_offset += 60
        
        # AI gesture
        self._draw_text("Donkey Car Choice:", info_x, y_offset, 
                       font_scale=0.5, color=(200, 200, 200))
        y_offset += 30
        ai_text = ai_gesture.value.upper() if ai_gesture != Gesture.NONE else "WAITING..."
        ai_color = (100, 100, 255) if ai_gesture != Gesture.NONE else (150, 150, 150)
        self._draw_text(ai_text, info_x, y_offset, 
                       font_scale=0.7, thickness=2, color=ai_color)
        y_offset += 60
        
        # Result
        if game_result:
            self._draw_text("Result:", info_x, y_offset, 
                           font_scale=0.5, color=(200, 200, 200))
            y_offset += 30
            
            if game_result == GameResult.PLAYER_WINS:
                result_text = "YOU WIN!"
                result_color = (0, 255, 0)
            elif game_result == GameResult.AI_WINS:
                result_text = "DONKEY CAR WINS!"
                result_color = (0, 100, 255)
            else:
                result_text = "TIE!"
                result_color = (255, 255, 0)
            
            self._draw_text(result_text, info_x, y_offset, 
                           font_scale=0.8, thickness=2, color=result_color)
        
        # Instructions at bottom
        y_offset = self.screen_height - 80
        self._draw_text("Show your hand to the camera", info_x, y_offset, 
                       font_scale=0.4, color=(150, 150, 150))
        y_offset += 25
        self._draw_text("Press 'q' to quit", info_x, y_offset, 
                       font_scale=0.4, color=(150, 150, 150))
        
        return self.display_frame
    
    def _draw_text(self, text, x, y, font_scale=0.5, thickness=1, color=(255, 255, 255)):
        """
        Helper method to draw text on the display
        
        Args:
            text: Text to draw
            x: X coordinate
            y: Y coordinate
            font_scale: Font scale
            thickness: Text thickness
            color: Text color (BGR)
        """
        cv2.putText(self.display_frame, text, (x, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

