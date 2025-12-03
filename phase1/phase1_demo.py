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

# Add parent directory to path for utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from utils import is_gui_available, safe_imshow, safe_waitkey, print_gui_warning

# Import Phase 1 modules
from phase1_oakd_camera import Phase1OAKDCamera
from phase1_person_detector import PersonDetector, PersonDetectorFallback
from phase1_rps_game import Phase1RPSGame


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
        
        # Initialize RPS game
        print("\n[3/3] Initializing RPS game...")
        try:
            # Try to find model in project-1 directory
            model_path = os.path.join('project-1', 'rps_model_improved.pth')
            if not os.path.exists(model_path):
                model_path = None
            self.rps_game = Phase1RPSGame(model_path=model_path, use_model=True)
        except Exception as e:
            print(f"Warning: Could not initialize RPS game with model: {e}")
            print("Falling back to MediaPipe-based detection...")
            self.rps_game = Phase1RPSGame(use_model=False)
        
        # Check GUI availability
        self.gui_available = is_gui_available()
        if not self.gui_available:
            print_gui_warning()
        
        # Demo state
        self.running = True
        self.mode = "detection"  # "detection" or "interaction"
        self.person_found = False
        self.person_bbox = None
        self.distance_to_person = None
        self.last_rps_result = None
        
        print("\n" + "=" * 60)
        print("Initialization complete!")
        print("=" * 60)
        print("\nControls:")
        print("  'q' - Quit")
        print("  'i' - Switch to interaction mode (RPS game)")
        print("  'd' - Switch to detection mode (person + distance)")
        print("  'r' - Reset RPS game")
        print("\nStarting demo...\n")
    
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
            if self.mode == "interaction" and person_found:
                # Play RPS game
                rps_result = self.rps_game.play_round(frame)
                
                # Display RPS results
                if rps_result['result'] is not None:
                    self.last_rps_result = rps_result
                    self._draw_rps_result(display_frame, rps_result)
                elif rps_result['player_gesture'].value != 'none':
                    # Show current gesture being detected
                    gesture_text = f"Gesture: {rps_result['player_gesture'].value.upper()}"
                    cv2.putText(display_frame, gesture_text, (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
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
            
            # Draw RPS score if in interaction mode
            if self.mode == "interaction":
                score_text = f"Score: Player {self.rps_game.game.player_score} - AI {self.rps_game.game.ai_score}"
                cv2.putText(display_frame, score_text, (10, 120),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show display
            if self.gui_available:
                safe_imshow("Phase 1: OAK-D Demo", display_frame)
            
            # Print status to terminal
            if frame_count % 30 == 0:  # Print every 30 frames
                self._print_status()
            
            # Handle keyboard input
            key = safe_waitkey(1)
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
                self.rps_game.reset_game()
                print("\n>>> RPS game reset!")
            
            frame_count += 1
        
        print("\nDemo ended.")
    
    def _draw_rps_result(self, frame, rps_result):
        """Draw RPS game result on frame"""
        result = rps_result['result']
        player_gesture = rps_result['player_gesture']
        ai_gesture = rps_result['ai_gesture']
        
        if result is None:
            return
        
        # Draw result in center of frame
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        # Result text
        if result.value == "player_wins":
            result_text = "YOU WIN!"
            result_color = (0, 255, 0)
        elif result.value == "ai_wins":
            result_text = "AI WINS!"
            result_color = (0, 0, 255)
        else:
            result_text = "TIE!"
            result_color = (255, 255, 0)
        
        # Draw background rectangle
        text_size = cv2.getTextSize(result_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
        rect_x = center_x - text_size[0] // 2 - 20
        rect_y = center_y - text_size[1] // 2 - 20
        rect_w = text_size[0] + 40
        rect_h = text_size[1] + 40
        
        cv2.rectangle(frame, (rect_x, rect_y), (rect_x + rect_w, rect_y + rect_h),
                     (0, 0, 0), -1)
        cv2.rectangle(frame, (rect_x, rect_y), (rect_x + rect_w, rect_y + rect_h),
                     result_color, 3)
        
        # Draw result text
        cv2.putText(frame, result_text, (center_x - text_size[0] // 2, center_y + text_size[1] // 2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, result_color, 3)
        
        # Draw gestures
        gesture_text = f"Player: {player_gesture.value.upper()} vs AI: {ai_gesture.value.upper()}"
        gesture_size = cv2.getTextSize(gesture_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        cv2.putText(frame, gesture_text, (center_x - gesture_size[0] // 2, center_y + 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    def _print_status(self):
        """Print current status to terminal"""
        print(f"\n--- Status (Mode: {self.mode.upper()}) ---")
        print(f"Person detected: {self.person_found}")
        if self.person_found and self.person_bbox:
            print(f"Person bbox: {self.person_bbox}")
        if self.distance_to_person is not None:
            print(f"Distance to person: {self.distance_to_person:.2f}m")
        if self.mode == "interaction":
            print(f"RPS Score: Player {self.rps_game.game.player_score} - AI {self.rps_game.game.ai_score}")
            if self.last_rps_result and self.last_rps_result['result']:
                print(f"Last result: {self.last_rps_result['result'].value}")
        print("-" * 40)
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        self.camera.release()
        if hasattr(self.person_detector, 'release'):
            self.person_detector.release()
        self.rps_game.release()
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

