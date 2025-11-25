"""
Game Logic for 1v1 Shooting Game
Manages game state, hits, health, and win conditions
"""
from enum import Enum
from pistol_detector import PlayerSide


class GameState(Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    PLAYER_A_WINS = "player_a_wins"
    PLAYER_B_WINS = "player_b_wins"
    GAME_OVER = "game_over"


class ShootingGame:
    def __init__(self, max_health=3):
        """
        Initialize the shooting game
        
        Args:
            max_health: Maximum health for each player
        """
        self.max_health = max_health
        self.player_a_health = max_health
        self.player_b_health = max_health
        self.state = GameState.WAITING
        self.hit_cooldown = 0  # Cooldown to prevent multiple hits
        self.hit_cooldown_max = 60  # Frames before next hit allowed
        self.last_hit_player = None
    
    def update(self, player_a_state, player_b_state):
        """
        Update game state based on player actions
        
        Args:
            player_a_state: State dict from pistol detector for player A
            player_b_state: State dict from pistol detector for player B
            
        Returns:
            dict: Game update result with hit information
        """
        result = {
            'hit_occurred': False,
            'hit_player': None,
            'game_state': self.state
        }
        
        if self.state != GameState.PLAYING:
            return result
        
        # Check for hits
        # Player A shoots at Player B (pointing right)
        if (player_a_state['has_pistol'] and 
            player_a_state['pointing_at'] == PlayerSide.RIGHT and
            self.hit_cooldown == 0):
            self.player_b_health -= 1
            result['hit_occurred'] = True
            result['hit_player'] = 'B'
            self.hit_cooldown = self.hit_cooldown_max
            self.last_hit_player = 'A'
            print(f"Player A hit Player B! B health: {self.player_b_health}")
        
        # Player B shoots at Player A (pointing left)
        elif (player_b_state['has_pistol'] and 
              player_b_state['pointing_at'] == PlayerSide.LEFT and
              self.hit_cooldown == 0):
            self.player_a_health -= 1
            result['hit_occurred'] = True
            result['hit_player'] = 'A'
            self.hit_cooldown = self.hit_cooldown_max
            self.last_hit_player = 'B'
            print(f"Player B hit Player A! A health: {self.player_a_health}")
        
        # Update cooldown
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        
        # Check win conditions
        if self.player_a_health <= 0:
            self.state = GameState.PLAYER_B_WINS
            result['game_state'] = self.state
            print("Player B wins!!!")
        elif self.player_b_health <= 0:
            self.state = GameState.PLAYER_A_WINS
            result['game_state'] = self.state
            print("Player A wins!!!")
        
        return result
    
    def start_game(self):
        """Start a new game"""
        self.player_a_health = self.max_health
        self.player_b_health = self.max_health
        self.state = GameState.PLAYING
        self.hit_cooldown = 0
        self.last_hit_player = None
        print("Game started! Players ready...")
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.player_a_health = self.max_health
        self.player_b_health = self.max_health
        self.state = GameState.WAITING
        self.hit_cooldown = 0
        self.last_hit_player = None
        print("Game reset!")
    
    def get_health(self):
        """Get current health of both players"""
        return {
            'player_a': self.player_a_health,
            'player_b': self.player_b_health
        }

