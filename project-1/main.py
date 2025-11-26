"""
Main Application for Rock-Paper-Scissors Game
Integrates OAKD camera, hand gesture detection, game logic, and UI display
Uses trained PyTorch model from ECE176_final project
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

# Try to use model-based detector, fallback to MediaPipe
try:
    from hand_gesture_detector_model import HandGestureDetectorModel
    from model_loader import Gesture
    USE_MODEL = True
    print("Using trained PyTorch model for gesture detection")
except (ImportError, FileNotFoundError) as e:
    print(f"Model not available ({e}), falling back to MediaPipe...")
    from hand_gesture_detector import HandGestureDetector, Gesture
    USE_MODEL = False


class RockPaperScissorsApp:
    def __init__(self, model_path=None, use_model=True):
        """
        Initialize the application
        
        Args:
            model_path: Path to model file (optional, will auto-detect)
            use_model: Whether to use model (True) or MediaPipe (False)
        """
        print("Initializing Rock-Paper-Scissors Game...")
        
        # Initialize components
        # Use OAKD camera (will fallback to webcam if not available)
        self.camera = OAKDCamera()
        
        # Initialize hand detector for bounding boxes
        try:
            from oakd_hand_detector import OAKDHandDetector
            self.hand_detector = OAKDHandDetector()
            self.use_hand_detection = True
            print("Hand detection with bounding boxes enabled")
        except Exception as e:
            print(f"Hand detector not available: {e}")
            self.hand_detector = None
            self.use_hand_detection = False
        
        # Initialize gesture detector
        if use_model and USE_MODEL:
            try:
                self.gesture_detector = HandGestureDetectorModel(model_path=model_path)
                print("Using trained PyTorch model")
            except Exception as e:
                print(f"Failed to load model: {e}")
                print("Falling back to MediaPipe...")
                from hand_gesture_detector import HandGestureDetector
                self.gesture_detector = HandGestureDetector()
        else:
            from hand_gesture_detector import HandGestureDetector
            self.gesture_detector = HandGestureDetector()
        
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
            
            # Detect gesture (hand detector already includes bbox detection)
            result = self.gesture_detector.detect_gesture(frame)
            
            # Handle different return formats
            if isinstance(result, tuple):
                if len(result) == 3:
                    gesture, annotated_frame, bbox = result
                elif len(result) == 2:
                    gesture, annotated_frame = result
                    bbox = None
                else:
                    gesture = result[0]
                    annotated_frame = result[1] if len(result) > 1 else frame
                    bbox = None
            else:
                gesture = result
                annotated_frame = frame
                bbox = None
            
            # Additional bounding box drawing if hand detector available
            if self.use_hand_detection and self.hand_detector and bbox is None:
                # Try to get bbox from hand detector
                try:
                    bbox, landmarks, frame_with_bbox = self.hand_detector.detect_hand_bbox(frame)
                    if bbox:
                        # Merge annotations
                        x, y, w, h = bbox
                        cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                        cv2.putText(annotated_frame, "Hand BBox", (x, y-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                except:
                    pass
            
            # Draw bounding box if available from gesture detector
            if bbox:
                x, y, w, h = bbox
                cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(annotated_frame, "Model Input Region", (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
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

