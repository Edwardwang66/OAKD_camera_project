"""
Main Application for Rock-Paper-Scissors Game
Integrates OAKD camera, hand gesture detection, game logic, and UI display
Uses MediaPipe hand pose detection (no neural network)
"""
import cv2
import time
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import is_gui_available, safe_imshow, safe_waitkey, print_gui_warning
from oakd_camera import OAKDCamera
from game_logic import RockPaperScissorsGame
from ui_display import GameUI
from hand_gesture_detector import HandGestureDetector, Gesture


class RockPaperScissorsApp:
    def __init__(self):
        """
        Initialize the application
        Uses MediaPipe hand pose detection (no neural network)
        """
        print("Initializing Rock-Paper-Scissors Game...")
        print("Using MediaPipe hand pose detection")
        
        # Initialize components
        # Use OAKD camera (will fallback to webcam if not available)
        self.camera = OAKDCamera()
        
        # Initialize gesture detector using MediaPipe hand pose
        self.gesture_detector = HandGestureDetector()
        print("MediaPipe hand pose detector initialized")
        
        self.game = RockPaperScissorsGame()
        self.ui = GameUI(screen_width=800, screen_height=480)
        
        # Check GUI availability
        self.gui_available = is_gui_available()
        if not self.gui_available:
            print_gui_warning()
        
        # Game state
        self.running = True
        self.current_player_gesture = Gesture.NONE
        self.gesture_hold_time = 0
        self.gesture_hold_threshold = 30  # Frames to hold gesture before playing
        self.last_result = None
        
        print("Initialization complete!")
    
    def run(self):
        """Main game loop"""
        print("Starting game loop...")
        print("Show your hand to the camera to play!")
        
        frame_count = 0
        
        while self.running:
            # Get frame from camera
            frame = self.camera.get_frame()
            
            if frame is None:
                time.sleep(0.01)
                continue
            
            # Detect gesture using MediaPipe hand pose
            gesture, annotated_frame = self.gesture_detector.detect_gesture(frame)
            
            # Update current gesture
            if gesture != Gesture.NONE:
                if gesture == self.current_player_gesture:
                    self.gesture_hold_time += 1
                else:
                    self.current_player_gesture = gesture
                    self.gesture_hold_time = 1
            else:
                self.current_player_gesture = Gesture.NONE
                self.gesture_hold_time = 0
            
            # Play round if gesture held long enough
            if (self.gesture_hold_time >= self.gesture_hold_threshold and 
                self.current_player_gesture != Gesture.NONE and
                self.game.result is None):
                # Play the round
                self.last_result = self.game.play_round(self.current_player_gesture)
                if self.last_result is not None:
                    print(f"Round {self.game.round_count}: "
                          f"Player: {self.current_player_gesture.value}, "
                          f"AI: {self.game.ai_choice.value}, "
                          f"Result: {self.last_result.value}")
            
            # Reset round after showing result for a while
            if self.last_result and self.gesture_hold_time < 10:
                # Reset for next round
                self.game.reset_round()
                self.last_result = None
            
            # Create display
            display = self.ui.create_display(
                camera_frame=annotated_frame,
                player_gesture=self.current_player_gesture,
                ai_gesture=self.game.ai_choice,
                game_result=self.last_result,
                player_score=self.game.player_score,
                ai_score=self.game.ai_score,
                round_count=self.game.round_count
            )
            
            # Show display (on 7-inch screen or via X11)
            if self.gui_available:
                safe_imshow("Rock Paper Scissors", display)
            
            # Check for quit
            key = safe_waitkey(1)
            if key == ord('q'):
                self.running = False
            elif key == ord('r'):
                # Reset game
                self.game.reset_game()
                print("Game reset!")
            
            frame_count += 1
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        self.camera.release()
        self.gesture_detector.release()
        if self.gui_available:
            try:
                cv2.destroyAllWindows()
            except:
                pass
        print("Cleanup complete!")


def main():
    """Main entry point"""
    app = RockPaperScissorsApp()
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()

