"""
Phase 2 Demo: Car Following and Approaching
Car can search for person, approach, and stop in front of them
"""
import cv2
import numpy as np
import time
import os
import sys
import threading
import queue

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'phase1'))

from utils import is_gui_available, safe_imshow, safe_waitkey, print_gui_warning
from phase1_oakd_camera import Phase1OAKDCamera
from phase1_person_detector import PersonDetectorFallback
from phase1_demo import SimplePersonDetector

# Import Phase 2 modules
from car_controller import CarController
from person_follower import PersonFollower, SearchController


class Phase2Demo:
    """
    Phase 2 Demo: Car following and approaching
    """
    def __init__(self, target_distance=1.0):
        """
        Initialize Phase 2 demo
        
        Args:
            target_distance: Target distance to person in meters
        """
        print("=" * 60)
        print("Phase 2: Car Following and Approaching")
        print("=" * 60)
        
        # Initialize camera
        print("\n[1/4] Initializing OAK-D camera with depth...")
        self.camera = Phase1OAKDCamera()
        
        # Initialize person detector
        print("\n[2/4] Initializing person detector...")
        try:
            self.person_detector = PersonDetectorFallback()
            if not self.person_detector.available:
                self.person_detector = SimplePersonDetector()
        except Exception as e:
            print(f"Person detector initialization failed: {e}")
            self.person_detector = SimplePersonDetector()
        
        # Initialize car controller
        print("\n[3/4] Initializing car controller...")
        # Try to use DonkeyCar VESC, fallback to simulation
        self.car = CarController(use_donkeycar=True)
        
        # Initialize controllers
        print("\n[4/4] Initializing control logic...")
        self.follower = PersonFollower(
            target_distance=target_distance,
            max_linear_speed=0.5,
            max_angular_speed=1.0,
            k_angle=1.0,
            k_linear=0.5
        )
        self.searcher = SearchController(search_angular_speed=0.3)
        
        # Check GUI availability
        self.gui_available = is_gui_available()
        if not self.gui_available:
            print_gui_warning()
        
        # State machine
        self.state = "SEARCH"  # SEARCH, APPROACH, INTERACT, STOP
        self.running = True
        
        # Detection state
        self.person_found = False
        self.person_bbox = None
        self.distance_to_person = None
        
        # Terminal input handling
        self.terminal_input_queue = queue.Queue()
        self.terminal_input_thread = None
        self.start_terminal_input_thread()
        
        print("\n" + "=" * 60)
        print("Initialization complete!")
        print("=" * 60)
        print("\nState Machine:")
        print("  SEARCH: Rotating to find person")
        print("  APPROACH: Moving towards person")
        print("  INTERACT: Stopped in front of person")
        print("  STOP: Emergency stop")
        print("\nControls:")
        print("  'q' or 'quit' - Quit and stop car")
        print("  's' or 'stop' - Emergency stop")
        print("  'r' or 'reset' - Reset to SEARCH state")
        print("\nStarting demo...\n")
    
    def start_terminal_input_thread(self):
        """Start a thread to read terminal input"""
        def read_terminal_input():
            while self.running:
                try:
                    if sys.stdin.isatty():
                        line = sys.stdin.readline()
                        if line:
                            self.terminal_input_queue.put(line)
                    else:
                        time.sleep(0.1)
                except (EOFError, KeyboardInterrupt):
                    break
                except Exception:
                    time.sleep(0.1)
        
        self.terminal_input_thread = threading.Thread(target=read_terminal_input, daemon=True)
        self.terminal_input_thread.start()
    
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
            
            # Person detection
            person_found, person_bbox, detected_frame = self.person_detector.detect_person(frame)
            self.person_found = person_found
            self.person_bbox = person_bbox
            
            # Calculate distance
            if person_found and person_bbox and depth_frame is not None:
                self.distance_to_person = self.camera.get_distance_from_bbox(
                    person_bbox, depth_frame
                )
            else:
                self.distance_to_person = None
            
            # State machine
            self._update_state_machine(frame)
            
            # Create display
            display_frame = self._create_display(detected_frame if person_found else frame)
            
            # Show display
            if self.gui_available:
                safe_imshow("Phase 2: Car Following", display_frame)
            
            # Print status
            if frame_count % 30 == 0:  # Every 30 frames
                self._print_status()
            
            # Handle keyboard input
            key = safe_waitkey(1)
            if key != -1:
                if key == ord('q'):
                    self.running = False
                elif key == ord('s'):
                    self.state = "STOP"
                    self.car.stop()
                    print("\n>>> Emergency stop!")
            
            # Handle terminal input
            try:
                while True:
                    command = self.terminal_input_queue.get_nowait().strip().lower()
                    if command in ['q', 'quit', 'exit']:
                        self.running = False
                    elif command in ['s', 'stop']:
                        self.state = "STOP"
                        self.car.stop()
                        print("\n>>> Emergency stop!")
                    elif command in ['r', 'reset']:
                        self.state = "SEARCH"
                        self.car.stop()
                        print("\n>>> Reset to SEARCH state")
            except queue.Empty:
                pass
            
            frame_count += 1
        
        print("\nDemo ended. Stopping car...")
        self.car.stop()
    
    def _update_state_machine(self, frame):
        """Update state machine based on current detection"""
        h, w = frame.shape[:2]
        
        if self.state == "STOP":
            # Emergency stop - do nothing
            self.car.stop()
            return
        
        if self.state == "SEARCH":
            # Search for person - rotate slowly
            if self.person_found:
                # Person detected - switch to APPROACH
                self.state = "APPROACH"
                print("\n>>> Person detected! Switching to APPROACH mode")
            else:
                # No person - continue searching
                control = self.searcher.compute_control()
                self.car.set_velocity(control['linear'], control['angular'])
        
        elif self.state == "APPROACH":
            # Approach person
            if not self.person_found:
                # Lost person - go back to SEARCH
                self.state = "SEARCH"
                self.car.stop()
                print("\n>>> Person lost! Switching to SEARCH mode")
            else:
                # Compute control to approach person
                control = self.follower.compute_control(
                    self.person_bbox, w, self.distance_to_person
                )
                
                # Check if ready for interaction
                if self.follower.is_ready_for_interaction(
                    self.person_bbox, w, self.distance_to_person
                ):
                    # Close enough and aligned - switch to INTERACT
                    self.state = "INTERACT"
                    self.car.stop()
                    print("\n>>> Reached target! Switching to INTERACT mode")
                else:
                    # Continue approaching
                    self.car.set_velocity(control['linear'], control['angular'])
        
        elif self.state == "INTERACT":
            # Interact with person - stay stopped
            if not self.person_found:
                # Lost person - go back to SEARCH
                self.state = "SEARCH"
                print("\n>>> Person lost! Switching to SEARCH mode")
            else:
                # Check if still at target distance
                if not self.follower.is_ready_for_interaction(
                    self.person_bbox, w, self.distance_to_person
                ):
                    # Moved away - go back to APPROACH
                    self.state = "APPROACH"
                    print("\n>>> Person moved! Switching to APPROACH mode")
                else:
                    # Stay stopped
                    self.car.stop()
    
    def _create_display(self, frame):
        """Create display frame with overlays"""
        display = frame.copy()
        h, w = display.shape[:2]
        
        # Draw state
        state_colors = {
            "SEARCH": (255, 255, 0),
            "APPROACH": (0, 255, 255),
            "INTERACT": (0, 255, 0),
            "STOP": (0, 0, 255)
        }
        state_color = state_colors.get(self.state, (255, 255, 255))
        
        cv2.putText(display, f"State: {self.state}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, state_color, 2)
        
        # Draw person detection info
        if self.person_found:
            cv2.putText(display, "Person: DETECTED", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if self.distance_to_person is not None:
                distance_text = f"Distance: {self.distance_to_person:.2f}m"
                cv2.putText(display, distance_text, (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        else:
            cv2.putText(display, "Person: NOT DETECTED", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Draw car state
        car_state = self.car.get_state()
        if not car_state['simulation']:
            speed_text = f"Speed: {car_state['linear']:.2f} m/s, {car_state['angular']:.2f} rad/s"
            cv2.putText(display, speed_text, (10, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            cv2.putText(display, "[SIMULATION MODE]", (10, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 128, 128), 2)
        
        return display
    
    def _print_status(self):
        """Print current status to terminal"""
        print(f"\n--- Status (State: {self.state}) ---")
        print(f"Person detected: {self.person_found}")
        if self.person_found and self.person_bbox:
            print(f"Person bbox: {self.person_bbox}")
        if self.distance_to_person is not None:
            print(f"Distance to person: {self.distance_to_person:.2f}m")
        car_state = self.car.get_state()
        print(f"Car: linear={car_state['linear']:.2f} m/s, angular={car_state['angular']:.2f} rad/s")
        print("-" * 40)
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        self.running = False
        if self.terminal_input_thread:
            self.terminal_input_thread.join(timeout=1.0)
        self.car.stop()
        self.car.release()
        self.camera.release()
        if hasattr(self.person_detector, 'release'):
            self.person_detector.release()
        if self.gui_available:
            try:
                cv2.destroyAllWindows()
            except:
                pass
        print("Cleanup complete!")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Phase 2: Car Following Demo')
    parser.add_argument('--target-distance', type=float, default=1.0,
                       help='Target distance to person in meters (default: 1.0)')
    parser.add_argument('--vesc-port', type=str, default=None,
                       help='VESC serial port (e.g., /dev/ttyACM0)')
    
    args = parser.parse_args()
    
    demo = Phase2Demo(target_distance=args.target_distance)
    
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

