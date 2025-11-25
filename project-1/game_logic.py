"""
Rock-Paper-Scissors Game Logic
Handles game state, AI opponent, and result calculation
"""
import random
from enum import Enum
from hand_gesture_detector import Gesture


class GameResult(Enum):
    PLAYER_WINS = "player_wins"
    AI_WINS = "ai_wins"
    TIE = "tie"


class RockPaperScissorsGame:
    def __init__(self):
        """Initialize the game"""
        self.player_choice = Gesture.NONE
        self.ai_choice = Gesture.NONE
        self.result = None
        self.round_count = 0
        self.player_score = 0
        self.ai_score = 0
    
    def make_ai_choice(self):
        """Generate a random choice for the AI opponent"""
        choices = [Gesture.ROCK, Gesture.PAPER, Gesture.SCISSORS]
        self.ai_choice = random.choice(choices)
        return self.ai_choice
    
    def play_round(self, player_gesture):
        """
        Play a round of rock-paper-scissors
        
        Args:
            player_gesture: Gesture enum from player
            
        Returns:
            GameResult enum
        """
        if player_gesture == Gesture.NONE:
            return None
        
        self.player_choice = player_gesture
        self.make_ai_choice()
        self.result = self._calculate_result()
        self.round_count += 1
        
        # Update scores
        if self.result == GameResult.PLAYER_WINS:
            self.player_score += 1
        elif self.result == GameResult.AI_WINS:
            self.ai_score += 1
        
        return self.result
    
    def _calculate_result(self):
        """
        Calculate game result based on player and AI choices
        
        Returns:
            GameResult enum
        """
        if self.player_choice == self.ai_choice:
            return GameResult.TIE
        
        # Winning conditions
        if (self.player_choice == Gesture.ROCK and self.ai_choice == Gesture.SCISSORS) or \
           (self.player_choice == Gesture.PAPER and self.ai_choice == Gesture.ROCK) or \
           (self.player_choice == Gesture.SCISSORS and self.ai_choice == Gesture.PAPER):
            return GameResult.PLAYER_WINS
        else:
            return GameResult.AI_WINS
    
    def reset_round(self):
        """Reset the current round (keep scores)"""
        self.player_choice = Gesture.NONE
        self.ai_choice = Gesture.NONE
        self.result = None
    
    def reset_game(self):
        """Reset the entire game"""
        self.reset_round()
        self.round_count = 0
        self.player_score = 0
        self.ai_score = 0

