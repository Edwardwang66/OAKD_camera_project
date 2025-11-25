"""
Game Selection Menu
Displays game selection interface and handles user interaction
"""
import cv2
import numpy as np
from enum import Enum


class GameChoice(Enum):
    NONE = "none"
    GAME_1 = "game_1"  # Rock-Paper-Scissors
    GAME_2 = "game_2"  # Air Drawing
    GAME_3 = "game_3"  # Shooting Game
    REGISTER = "register"  # User registration
    QUIT = "quit"


class GameMenu:
    def __init__(self, screen_width=800, screen_height=480):
        """
        Initialize game menu
        
        Args:
            screen_width: Width of display screen
            screen_height: Height of display screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.selected_game = GameChoice.NONE
    
    def create_menu_display(self, camera_frame, user_name=None, is_stranger=False):
        """
        Create game selection menu display
        
        Args:
            camera_frame: Frame from camera
            user_name: Name of recognized user (None if stranger)
            is_stranger: Whether user is a stranger
            
        Returns:
            numpy.ndarray: Menu display frame
        """
        # Create blank display
        display = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        display.fill(20)  # Dark background
        
        # Layout: Camera feed on left, menu on right
        camera_width = int(self.screen_width * 0.5)
        menu_width = self.screen_width - camera_width
        
        # Resize and place camera frame
        if camera_frame is not None:
            camera_resized = cv2.resize(camera_frame, (camera_width, self.screen_height))
            display[:, :camera_width] = camera_resized
        
        # Draw dividing line
        cv2.line(display, (camera_width, 0), 
                (camera_width, self.screen_height), (100, 100, 100), 2)
        
        # Draw greeting
        menu_x = camera_width + 20
        y_offset = 30
        
        if user_name:
            greeting = f"Hello, {user_name}!"
            color = (0, 255, 0)  # Green for registered user
        else:
            greeting = "Hello, Stranger!"
            color = (0, 165, 255)  # Orange for stranger
        
        cv2.putText(display, greeting, (menu_x, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        y_offset += 40
        
        if is_stranger:
            cv2.putText(display, "What game do you want to play?", (menu_x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        else:
            cv2.putText(display, "Select a game to play:", (menu_x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        y_offset += 50
        
        # Game options
        games = [
            ("1", "Rock-Paper-Scissors", GameChoice.GAME_1, (100, 200, 255)),
            ("2", "Air Drawing", GameChoice.GAME_2, (100, 255, 100)),
            ("3", "1v1 Shooting Game", GameChoice.GAME_3, (255, 100, 100)),
        ]
        
        for key, name, choice, color in games:
            # Highlight selected game
            if self.selected_game == choice:
                # Draw background for selected item
                cv2.rectangle(display, (menu_x - 10, y_offset - 25), 
                            (menu_x + menu_width - 30, y_offset + 5), (50, 50, 50), -1)
                cv2.rectangle(display, (menu_x - 10, y_offset - 25), 
                            (menu_x + menu_width - 30, y_offset + 5), color, 2)
            
            # Game number and name
            text = f"Press '{key}' - {name}"
            text_color = color if self.selected_game == choice else (200, 200, 200)
            cv2.putText(display, text, (menu_x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
            y_offset += 40
        
        y_offset += 20
        
        # Registration option
        if is_stranger:
            cv2.putText(display, "Press 'r' - Register as new user", (menu_x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 255), 1)
            y_offset += 30
        
        # Quit option
        cv2.putText(display, "Press 'q' - Quit", (menu_x, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        
        return display
    
    def handle_key(self, key):
        """
        Handle keyboard input for menu selection
        
        Args:
            key: Key code from cv2.waitKey
            
        Returns:
            GameChoice: Selected game choice
        """
        key_char = chr(key & 0xFF) if key > 0 else None
        
        if key_char == '1':
            self.selected_game = GameChoice.GAME_1
            return GameChoice.GAME_1
        elif key_char == '2':
            self.selected_game = GameChoice.GAME_2
            return GameChoice.GAME_2
        elif key_char == '3':
            self.selected_game = GameChoice.GAME_3
            return GameChoice.GAME_3
        elif key_char == 'r':
            return GameChoice.REGISTER
        elif key_char == 'q':
            return GameChoice.QUIT
        
        return GameChoice.NONE

