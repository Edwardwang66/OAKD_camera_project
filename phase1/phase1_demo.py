"""
Phase 1 Demo: OAK-D Desktop Demo
Combines person detection, distance estimation, and Rock-Paper-Scissors game

Features:
- Person detection with bounding box
- Distance estimation from depth map
- RPS game in interaction mode
"""
import cv2
import numpy as np
import time
import os
import sys
import threading
import queue

# Add parent directory to path for utils and project-1
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
project1_path = os.path.join(parent_dir, 'project-1')
sys.path.insert(0, project1_path)

from utils import is_gui_available, safe_imshow, safe_waitkey, print_gui_warning

# Import Phase 1 modules
from phase1_oakd_camera import Phase1OAKDCamera
from phase1_person_detector import PersonDetector, PersonDetectorFallback

# Import project-1 RPS game components
from game_logic import RockPaperScissorsGame, GameResult
from ui_display import GameUI

# Try to use model-based detector, fallback to MediaPipe
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


class SimplePersonDetector:
    """
    Simple person detector using MediaPipe or basic heuristics
    For Phase 1 demo - can be replaced with full mobilenet-ssd later
    """
    def __init__(self):
        """Initialize simple person detector"""
        try:
            import mediapipe as mp
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.5
            )
            self.use_mediapipe = True
            print("Using MediaPipe for person detection")
        except ImportError:
            self.use_mediapipe = False
            print("MediaPipe not available, using basic detection")
        
        self.available = True
    
    def detect_person(self, frame):
        """
        Detect person in frame
        
        Args:
            frame: BGR frame
            
        Returns:
            tuple: (person_found, person_bbox, annotated_frame)
        """
        annotated_frame = frame.copy()
        
        if self.use_mediapipe:
            # Use MediaPipe Pose to detect person
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks:
                # Get bounding box from pose landmarks
                h, w = frame.shape[:2]
                landmarks = results.pose_landmarks.landmark
                
                x_coords = [lm.x * w for lm in landmarks]
                y_coords = [lm.y * h for lm in landmarks]
                
                x_min = int(min(x_coords))
                x_max = int(max(x_coords))
                y_min = int(min(y_coords))
                y_max = int(max(y_coords))
                
                # Add padding
                padding = 20
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(w, x_max + padding)
                y_max = min(h, y_max + padding)
                
                person_bbox = (x_min, y_min, x_max, y_max)
                
                # Draw bounding box
                cv2.rectangle(annotated_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                cv2.putText(annotated_frame, "Person Detected", (x_min, y_min - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                return True, person_bbox, annotated_frame
        
        # No person detected
        return False, None, annotated_frame
    
    def release(self):
        """Release resources"""
        if hasattr(self, 'pose'):
            self.pose.close()


class Phase1Demo:
    """
    Phase 1 Demo Application
    Combines person detection, distance estimation, and RPS game
    """
    def __init__(self):
        """Initialize Phase 1 demo"""
        print("=" * 60)
        print("Phase 1: OAK-D Desktop Demo")
        print("=" * 60)
        
        # Initialize camera with depth support
        print("\n[1/3] Initializing OAK-D camera with depth...")
        self.camera = Phase1OAKDCamera()
        
        # Initialize person detector
        # Note: For Phase 1, we'll use a simple approach that works with frames
        # The full mobilenet-ssd integration would require sharing the camera pipeline
        print("\n[2/3] Initializing person detector...")
        print("Note: Using simple detection (full mobilenet-ssd requires pipeline integration)")
        try:
            # Try to use mobilenet-ssd, but it creates separate pipeline which may conflict
            # For now, use fallback or a simpler method
            self.person_detector = PersonDetectorFallback()
            # If fallback not available, create a dummy detector
            if not self.person_detector.available:
                print("Creating simple person detector...")
                self.person_detector = SimplePersonDetector()
        except Exception as e:
            print(f"Person detector initialization failed: {e}")
            print("Using simple detector...")
            self.person_detector = SimplePersonDetector()
        
        # Initialize RPS game (using project-1 components)
        print("\n[3/3] Initializing RPS game...")
        self.game = RockPaperScissorsGame()
        self.ui = GameUI(screen_width=800, screen_height=480)
        
        # Initialize gesture detector
        try:
            # Try to find model in project-1 directory
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(parent_dir, 'project-1', 'rps_model_improved.pth')
            if not os.path.exists(model_path):
                model_path = None
            
            if USE_MODEL and model_path and os.path.exists(model_path):
                try:
                    self.gesture_detector = HandGestureDetectorModel(model_path=model_path)
                    print("Using trained PyTorch model for gesture detection")
                except Exception as e:
                    print(f"Failed to load model: {e}")
                    print("Falling back to MediaPipe...")
                    from hand_gesture_detector import HandGestureDetector
                    self.gesture_detector = HandGestureDetector()
            else:
                from hand_gesture_detector import HandGestureDetector
                self.gesture_detector = HandGestureDetector()
                print("Using MediaPipe for gesture detection")
        except Exception as e:
            print(f"Warning: Could not initialize gesture detector: {e}")
            raise
        
        # Check GUI availability and XQuartz
        self.gui_available = is_gui_available()
        display = os.environ.get("DISPLAY")
        if display:
            print(f"✓ Display detected: {display}")
            print("  XQuartz display should work correctly")
        else:
            print("⚠ Warning: DISPLAY not set. XQuartz may not work.")
            print("  Set DISPLAY=:0 or ensure XQuartz is running")
            print("  On Mac: export DISPLAY=:0")
        
        if not self.gui_available:
            print_gui_warning()
        else:
            # Test XQuartz connection
            try:
                import cv2
                test_img = np.zeros((100, 100, 3), dtype=np.uint8)
                cv2.namedWindow("XQuartz Test", cv2.WINDOW_NORMAL)
                cv2.imshow("XQuartz Test", test_img)
                cv2.waitKey(1)
                cv2.destroyWindow("XQuartz Test")
                print("✓ XQuartz connection test successful")
            except Exception as e:
                print(f"⚠ XQuartz test failed: {e}")
                print("  Windows may still work, but check XQuartz settings")
        
        # Demo state
        self.running = True
        self.mode = "detection"  # "detection" or "interaction"
        self.person_found = False
        self.person_bbox = None
        self.distance_to_person = None
        self.last_rps_result = None
        
        # RPS game state (using project-1 style)
        self.current_player_gesture = Gesture.NONE if Gesture else None
        self.gesture_hold_time = 0
        self.gesture_hold_threshold = 30  # Frames to hold gesture before playing
        
        # Terminal input handling
        self.terminal_input_queue = queue.Queue()
        self.terminal_input_thread = None
        self.start_terminal_input_thread()
        
        print("\n" + "=" * 60)
        print("Initialization complete!")
        print("=" * 60)
        print("\nControls:")
        print("  'q' or 'quit' - Quit")
        print("  'i' or 'interaction' - Switch to interaction mode (RPS game)")
        print("  'd' or 'detection' - Switch to detection mode (person + distance)")
        print("  'r' or 'reset' - Reset RPS game")
        print("\nNote: You can type commands in the terminal or press keys in the OpenCV window")
        print("Starting demo...\n")
    
    def run(self):
        """Main demo loop"""
        frame_count = 0
        
        while self.running:
            # Get frame from camera
            frame = self.camera.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue
            
            # Get depth frame
            depth_frame = self.camera.get_depth_frame()
            
            # Create display frame
            display_frame = frame.copy()
            
            # Person detection
            person_found, person_bbox, detected_frame = self.person_detector.detect_person(frame)
            self.person_found = person_found
            self.person_bbox = person_bbox
            
            # Update display with person detection
            if person_found and person_bbox:
                display_frame = detected_frame
                
                # Calculate distance
                if depth_frame is not None:
                    self.distance_to_person = self.camera.get_distance_from_bbox(
                        person_bbox, depth_frame
                    )
                else:
                    self.distance_to_person = None
                
                # Draw distance info
                if self.distance_to_person is not None:
                    x_min, y_min, x_max, y_max = person_bbox
                    distance_text = f"Distance: {self.distance_to_person:.2f}m"
                    cv2.putText(display_frame, distance_text, (x_min, y_max + 25),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Mode-specific processing
            if self.mode == "interaction":
                # Detect gesture using project-1 gesture detector (use original frame)
                result = self.gesture_detector.detect_gesture(frame)
                
                # Handle different return formats
                if isinstance(result, tuple):
                    if len(result) >= 2:
                        gesture = result[0]
                        annotated_frame = result[1]
                        # Use annotated frame for camera display (has hand detection overlay)
                        camera_frame_for_ui = annotated_frame
                    else:
                        gesture = result[0]
                        camera_frame_for_ui = frame
                else:
                    gesture = result
                    camera_frame_for_ui = frame
                
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
                
                # Play round if gesture held long enough (only if person detected)
                if person_found and (self.gesture_hold_time >= self.gesture_hold_threshold and 
                    self.current_player_gesture != Gesture.NONE and
                    self.game.result is None):
                    # Play the round
                    self.last_rps_result = self.game.play_round(self.current_player_gesture)
                    if self.last_rps_result is not None:
                        print(f"Round {self.game.round_count}: "
                              f"Player: {self.current_player_gesture.value}, "
                              f"AI: {self.game.ai_choice.value}, "
                              f"Result: {self.last_rps_result.value}")
                
                # Reset round after showing result for a while
                if self.last_rps_result and self.gesture_hold_time < 10:
                    # Reset for next round
                    self.game.reset_round()
                    self.last_rps_result = None
                
                # Add person detection overlay to camera frame if person found
                if person_found and person_bbox:
                    # Draw person bbox on camera frame
                    x_min, y_min, x_max, y_max = person_bbox
                    cv2.rectangle(camera_frame_for_ui, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    cv2.putText(camera_frame_for_ui, "Person Detected", (x_min, y_min - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # Draw distance if available
                    if self.distance_to_person is not None:
                        distance_text = f"Distance: {self.distance_to_person:.2f}m"
                        cv2.putText(camera_frame_for_ui, distance_text, (x_min, y_max + 25),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                else:
                    # Draw "No person detected" message
                    h, w = camera_frame_for_ui.shape[:2]
                    text = "No person detected - Show yourself to play!"
                    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                    text_x = (w - text_size[0]) // 2
                    text_y = h // 2
                    cv2.putText(camera_frame_for_ui, text, (text_x, text_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Use project-1 UI to create display (always use original frame dimensions)
                display_frame = self.ui.create_display(
                    camera_frame=camera_frame_for_ui,
                    player_gesture=self.current_player_gesture,
                    ai_gesture=self.game.ai_choice,
                    game_result=self.last_rps_result,
                    player_score=self.game.player_score,
                    ai_score=self.game.ai_score,
                    round_count=self.game.round_count
                )
            else:
                # Detection mode - draw overlays on camera frame
                # Draw mode indicator
                mode_text = f"Mode: {self.mode.upper()}"
                if self.mode == "interaction":
                    mode_color = (0, 255, 0)
                else:
                    mode_color = (255, 255, 0)
                
                cv2.putText(display_frame, mode_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, mode_color, 2)
                
                # Draw person status
                if person_found:
                    status_text = "Person: DETECTED"
                    status_color = (0, 255, 0)
                else:
                    status_text = "Person: NOT DETECTED"
                    status_color = (0, 0, 255)
                
                cv2.putText(display_frame, status_text, (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            # Show display (will output to XQuartz if DISPLAY is set)
            if self.gui_available:
                safe_imshow("Phase 1: OAK-D Demo", display_frame)
            
            # Print status to terminal
            if frame_count % 30 == 0:  # Print every 30 frames
                self._print_status()
            
            # Handle keyboard input from OpenCV window
            key = safe_waitkey(1)
            if key != -1:
                if key == ord('q'):
                    self.running = False
                elif key == ord('i'):
                    self.mode = "interaction"
                    print("\n>>> Switched to INTERACTION mode (RPS game)")
                    print("    Show your hand gesture to play!")
                elif key == ord('d'):
                    self.mode = "detection"
                    print("\n>>> Switched to DETECTION mode (person + distance)")
                elif key == ord('r'):
                    self.game.reset_game()
                    print("\n>>> RPS game reset!")
            
            # Handle terminal input (non-blocking)
            try:
                while True:
                    command = self.terminal_input_queue.get_nowait().strip().lower()
                    if command in ['q', 'quit', 'exit']:
                        self.running = False
                        print("\n>>> Quitting...")
                    elif command in ['i', 'interaction', 'interact']:
                        self.mode = "interaction"
                        print("\n>>> Switched to INTERACTION mode (RPS game)")
                        print("    Show your hand gesture to play!")
                    elif command in ['d', 'detection', 'detect']:
                        self.mode = "detection"
                        print("\n>>> Switched to DETECTION mode (person + distance)")
                    elif command in ['r', 'reset']:
                        self.game.reset_game()
                        print("\n>>> RPS game reset!")
                    elif command:
                        print(f"Unknown command: {command}. Type 'q' to quit, 'i' for interaction, 'd' for detection, 'r' to reset")
            except queue.Empty:
                pass  # No terminal input available
            
            frame_count += 1
        
        print("\nDemo ended.")
    
    
    def _print_status(self):
        """Print current status to terminal"""
        print(f"\n--- Status (Mode: {self.mode.upper()}) ---")
        print(f"Person detected: {self.person_found}")
        if self.person_found and self.person_bbox:
            print(f"Person bbox: {self.person_bbox}")
        if self.distance_to_person is not None:
            print(f"Distance to person: {self.distance_to_person:.2f}m")
        if self.mode == "interaction":
            print(f"RPS Score: Player {self.game.player_score} - AI {self.game.ai_score}")
            if self.last_rps_result:
                print(f"Last result: {self.last_rps_result.value}")
        print("-" * 40)
    
    def start_terminal_input_thread(self):
        """Start a thread to read terminal input"""
        def read_terminal_input():
            while self.running:
                try:
                    if sys.stdin.isatty():
                        # Read a line (this will block, but that's OK in a separate thread)
                        line = sys.stdin.readline()
                        if line:
                            self.terminal_input_queue.put(line)
                    else:
                        time.sleep(0.1)
                except (EOFError, KeyboardInterrupt):
                    break
                except Exception as e:
                    # Silently handle errors (e.g., if stdin is closed)
                    time.sleep(0.1)
        
        self.terminal_input_thread = threading.Thread(target=read_terminal_input, daemon=True)
        self.terminal_input_thread.start()
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        self.running = False  # Stop terminal input thread
        if self.terminal_input_thread:
            self.terminal_input_thread.join(timeout=1.0)
        self.camera.release()
        if hasattr(self.person_detector, 'release'):
            self.person_detector.release()
        if hasattr(self, 'gesture_detector') and hasattr(self.gesture_detector, 'release'):
            self.gesture_detector.release()
        if self.gui_available:
            try:
                cv2.destroyAllWindows()
            except:
                pass
        print("Cleanup complete!")


def main():
    """Main entry point"""
    demo = Phase1Demo()
    
    try:
        demo.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        demo.cleanup()


if __name__ == "__main__":
    main()

