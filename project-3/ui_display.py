"""
UI Display for Shooting Game
Creates the referee display interface for the 7-inch screen
"""
import cv2
import numpy as np
from game_logic import GameState


class RefereeUI:
    def __init__(self, screen_width=800, screen_height=480, max_health=3):
        """
        Initialize the UI display
        
        Args:
            screen_width: Width of the display screen
            screen_height: Height of the display screen
            max_health: Maximum health for health bars
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_health = max_health
    
    def create_display(self, camera_frame, player_a_state, player_b_state, 
                      game_state, health_a, health_b, hit_info=None):
        """
        Create the referee display showing game state
        
        Args:
            camera_frame: Frame from camera
            player_a_state: Player A state from pistol detector
            player_b_state: Player B state from pistol detector
            game_state: Current game state
            health_a: Player A health
            health_b: Player B health
            hit_info: Information about recent hits
            
        Returns:
            numpy.ndarray: Display frame
        """
        # Create blank display
        display = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        display.fill(20)  # Dark background
        
        # Layout: Camera feed on top, game info on bottom
        camera_height = int(self.screen_height * 0.6)
        info_height = self.screen_height - camera_height
        
        # Resize and place camera frame
        if camera_frame is not None:
            camera_resized = cv2.resize(camera_frame, (self.screen_width, camera_height))
            display[:camera_height, :] = camera_resized
            
            # Draw dividing line
            cv2.line(display, (0, camera_height), 
                    (self.screen_width, camera_height), (100, 100, 100), 2)
        
        # Draw game information panel
        info_y = camera_height + 10
        
        # Title
        title = "1v1 SHOOTING GAME - REFEREE"
        cv2.putText(display, title, (10, info_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Player A info (left side)
        player_a_y = info_y + 30
        self._draw_player_info(display, "PLAYER A", player_a_state, 
                              health_a, self.max_health, 10, player_a_y, (100, 200, 255))
        
        # Player B info (right side)
        player_b_y = info_y + 30
        self._draw_player_info(display, "PLAYER B", player_b_state, 
                              health_b, self.max_health, 
                              self.screen_width // 2 + 10, player_b_y, (255, 100, 100))
        
        # Game state display
        state_y = info_y + 80
        self._draw_game_state(display, game_state, hit_info, state_y)
        
        # Instructions
        inst_y = self.screen_height - 20
        if game_state == GameState.WAITING:
            cv2.putText(display, "Press 's' to start game", (10, inst_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        elif game_state == GameState.PLAYING:
            cv2.putText(display, "Make pistol gesture and point at opponent", (10, inst_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        else:
            cv2.putText(display, "Press 'r' to reset game", (10, inst_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        
        cv2.putText(display, "Press 'q' to quit", (self.screen_width - 150, inst_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        
        return display
    
    def _draw_player_info(self, display, player_name, player_state, 
                         health, max_health, x, y, color):
        """
        Draw player information
        
        Args:
            display: Display frame
            player_name: Name of player
            player_state: Player state from detector
            health: Current health
            max_health: Maximum health
            x: X position
            y: Y position
            color: Player color (BGR)
        """
        # Player name
        cv2.putText(display, player_name, (x, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Pistol status
        pistol_status = "READY" if player_state['has_pistol'] else "NO PISTOL"
        pistol_color = (0, 255, 0) if player_state['has_pistol'] else (100, 100, 100)
        cv2.putText(display, f"Pistol: {pistol_status}", (x, y + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, pistol_color, 1)
        
        # Health bar
        health_y = y + 40
        bar_width = 200
        bar_height = 15
        health_ratio = health / max_health
        
        # Background
        cv2.rectangle(display, (x, health_y), 
                     (x + bar_width, health_y + bar_height), (50, 50, 50), -1)
        
        # Health fill
        health_width = int(bar_width * health_ratio)
        health_color = (0, 255, 0) if health_ratio > 0.5 else (0, 165, 255) if health_ratio > 0.25 else (0, 0, 255)
        cv2.rectangle(display, (x, health_y), 
                     (x + health_width, health_y + bar_height), health_color, -1)
        
        # Health text
        cv2.putText(display, f"HP: {health}/{max_health}", (x, health_y + 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    
    def _draw_game_state(self, display, game_state, hit_info, y):
        """
        Draw game state information
        
        Args:
            display: Display frame
            game_state: Current game state
            hit_info: Hit information
            y: Y position
        """
        center_x = self.screen_width // 2
        
        if game_state == GameState.WAITING:
            text = "WAITING FOR PLAYERS..."
            color = (150, 150, 150)
        elif game_state == GameState.PLAYING:
            if hit_info and hit_info.get('hit_occurred'):
                hit_player = hit_info.get('hit_player', '')
                text = f"!!! PLAYER {hit_player} HIT !!!"
                color = (0, 0, 255)  # Red
            else:
                text = "FIGHT!"
                color = (0, 255, 0)  # Green
        elif game_state == GameState.PLAYER_A_WINS:
            text = "!!! PLAYER A WINS !!!"
            color = (0, 255, 255)  # Yellow
        elif game_state == GameState.PLAYER_B_WINS:
            text = "!!! PLAYER B WINS !!!"
            color = (0, 255, 255)  # Yellow
        else:
            text = "GAME OVER"
            color = (100, 100, 100)
        
        # Get text size for centering
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        text_x = center_x - text_size[0] // 2
        
        cv2.putText(display, text, (text_x, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
    def set_max_health(self, max_health):
        """Set maximum health for health bar display"""
        self.max_health = max_health

