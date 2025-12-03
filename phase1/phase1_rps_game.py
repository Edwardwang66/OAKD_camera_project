"""
Rock-Paper-Scissors Game Wrapper for Phase 1
Provides a simple interface to play RPS rounds
"""
import os
import sys

# Add project-1 to path (parent directory)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project1_path = os.path.join(parent_dir, 'project-1')
sys.path.insert(0, project1_path)

from game_logic import RockPaperScissorsGame, GameResult

# Try to import gesture detector
try:
    from hand_gesture_detector_model import HandGestureDetectorModel
    from model_loader import Gesture
    USE_MODEL = True
except (ImportError, FileNotFoundError):
    try:
        from hand_gesture_detector import HandGestureDetector, Gesture
        USE_MODEL = False
    except ImportError:
        print("Warning: Could not import gesture detector")
        Gesture = None
        USE_MODEL = False


class Phase1RPSGame:
    """
    Wrapper for Rock-Paper-Scissors game
    Provides simple play_round interface
    """
    def __init__(self, model_path=None, use_model=True):
        """
        Initialize the RPS game
        
        Args:
            model_path: Path to model file (optional)
            use_model: Whether to use model (True) or MediaPipe (False)
        """
        self.game = RockPaperScissorsGame()
        
        # Initialize gesture detector
        if Gesture is None:
            raise RuntimeError("Gesture detector not available")
        
        if use_model and USE_MODEL:
            try:
                self.gesture_detector = HandGestureDetectorModel(model_path=model_path)
                print("Using trained PyTorch model for RPS")
            except Exception as e:
                print(f"Failed to load model: {e}")
                print("Falling back to MediaPipe...")
                from hand_gesture_detector import HandGestureDetector
                self.gesture_detector = HandGestureDetector()
        else:
            from hand_gesture_detector import HandGestureDetector
            self.gesture_detector = HandGestureDetector()
        
        # Game state
        self.current_gesture = Gesture.NONE
        self.gesture_hold_time = 0
        self.gesture_hold_threshold = 30  # Frames to hold gesture before playing
    
    def play_round(self, frame):
        """
        Play a round of rock-paper-scissors
        
        Args:
            frame: BGR image frame containing hand gesture
            
        Returns:
            dict: Game result with keys:
                - 'result': GameResult enum or None (if no valid gesture yet)
                - 'player_gesture': Gesture enum
                - 'ai_gesture': Gesture enum or None
                - 'player_score': int
                - 'ai_score': int
                - 'round_count': int
        """
        # Detect gesture from frame
        result = self.gesture_detector.detect_gesture(frame)
        
        # Handle different return formats
        if isinstance(result, tuple):
            gesture = result[0]
        else:
            gesture = result
        
        # Update gesture hold time
        if gesture != Gesture.NONE:
            if gesture == self.current_gesture:
                self.gesture_hold_time += 1
            else:
                self.current_gesture = gesture
                self.gesture_hold_time = 1
        else:
            self.current_gesture = Gesture.NONE
            self.gesture_hold_time = 0
        
        # Play round if gesture held long enough
        game_result = None
        if (self.gesture_hold_time >= self.gesture_hold_threshold and 
            self.current_gesture != Gesture.NONE and
            self.game.result is None):
            game_result = self.game.play_round(self.current_gesture)
        
        return {
            'result': game_result,
            'player_gesture': self.current_gesture,
            'ai_gesture': self.game.ai_choice if game_result is not None else None,
            'player_score': self.game.player_score,
            'ai_score': self.game.ai_score,
            'round_count': self.game.round_count
        }
    
    def reset_round(self):
        """Reset the current round (keep scores)"""
        self.game.reset_round()
        self.current_gesture = Gesture.NONE
        self.gesture_hold_time = 0
    
    def reset_game(self):
        """Reset the entire game"""
        self.game.reset_game()
        self.current_gesture = Gesture.NONE
        self.gesture_hold_time = 0
    
    def release(self):
        """Release resources"""
        if hasattr(self, 'gesture_detector'):
            self.gesture_detector.release()

