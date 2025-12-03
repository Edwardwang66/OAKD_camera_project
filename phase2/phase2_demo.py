"""
Phase 2 Demo: Person Following and Approaching
Designed for Raspberry Pi 5 with OAKD Lite camera
Uses X11 forwarding (XQuartz) for display on Mac

State Machine:
- SEARCH: Rotate slowly to find person
- APPROACH: Move towards person (left/right/straight based on person position)
- INTERACT: Stop in front of person
"""
import cv2
import time
import sys
import os

# Add parent directory to path for utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from utils import is_gui_available, safe_imshow, safe_waitkey, print_gui_warning
from oakd_camera import OAKDCamera
from car_controller import CarController
from person_follower import PersonFollower, SearchController


class Phase2Demo:
    """
    Phase 2 Demo: Person following and approaching
    Designed for Raspberry Pi 5 with OAKD camera and VESC control
    """
    def __init__(self, target_distance=1.0, vesc_port=None, simulation_mode=False):
        """
        Initialize Phase 2 demo
        
        Args:
            target_distance: Target distance to person in meters
            vesc_port: VESC serial port (e.g., '/dev/ttyACM0'), None for auto-detect
            simulation_mode: If True, car commands are printed only (for testing)
        """
        print("=" * 60)
        print("Phase 2: Person Following and Approaching")
        print("Raspberry Pi 5 + OAKD Lite + DonkeyCar/VESC")
        print("=" * 60)
        
        # Check DISPLAY for X11 forwarding
        display = os.environ.get("DISPLAY")
        if display:
            print(f"\n[X11] Display forwarding enabled: {display}")
            print("[X11] Windows will appear on your Mac via XQuartz")
        else:
            print("\n[WARNING] DISPLAY not set. X11 forwarding may not be working.")
            print("[WARNING] Windows may not appear, but processing will continue.")
        
        # Initialize OAKD camera with person detection
        print("\n[1/3] Initializing OAKD camera with person detection...")
        try:
            self.camera = OAKDCamera()
            if not self.camera.available:
                print("ERROR: OAKD camera not available. Exiting.")
                sys.exit(1)
        except Exception as e:
            print(f"ERROR: Could not initialize OAKD camera: {e}")
            print("\nTroubleshooting:")
            print("  1. Check OAKD camera is connected via USB")
            print("  2. Check permissions: sudo usermod -a -G dialout $USER")
            print("  3. Try: sudo python phase2_demo.py (not recommended)")
            sys.exit(1)
        
        # Initialize car controller
        print("\n[2/3] Initializing car controller...")
        if simulation_mode:
            print("[CarController] Running in SIMULATION mode")
        else:
            print("[CarController] Attempting to connect to VESC...")
        
        self.car = CarController(
            vesc_port=vesc_port,
            use_donkeycar=True,
            simulation_mode=simulation_mode
        )
        
        # Initialize controllers
        print("\n[3/3] Initializing control logic...")
        self.follower = PersonFollower(
            target_distance=target_distance,
            max_linear_speed=0.5,
            max_angular_speed=1.0,
            k_angle=1.0,
            k_linear=0.5,
            angle_threshold=0.1,
            distance_threshold=0.2
        )
        self.searcher = SearchController(search_angular_speed=0.3)
        
        # Check GUI availability (for X11 forwarding)
        self.gui_available = is_gui_available()
        if not self.gui_available:
            print_gui_warning()
        else:
            print("\n[GUI] OpenCV display available via X11 forwarding")
        
        # State machine
        self.state = "SEARCH"  # SEARCH, APPROACH, INTERACT, STOP
        self.running = True
        
        # Detection state
        self.person_found = False
        self.person_bbox = None
        
        print("\n" + "=" * 60)
        print("Initialization complete!")
        print("=" * 60)
        print("\nState Machine:")
        print("  SEARCH: Rotating slowly to find person")
        print("  APPROACH: Moving towards person (LEFT/RIGHT/STRAIGHT)")
        print("  INTERACT: Stopped in front of person")
        print("  STOP: Emergency stop")
        print("\nControls:")
        print("  'q' - Quit and stop car")
        print("  's' - Emergency stop")
        print("  'r' - Reset to SEARCH state")
        print("\nStarting demo...\n")
    
    def run(self):
        """Main demo loop"""
        frame_count = 0
        last_status_print = 0
        
        while self.running:
            # Person detection
            person_found, person_bbox, detected_frame = self.camera.detect_person()
            self.person_found = person_found
            self.person_bbox = person_bbox
            
            if detected_frame is None:
                time.sleep(0.01)
                continue
            
            # State machine
            self._update_state_machine(detected_frame)
            
            # Create display
            display_frame = self._create_display(detected_frame)
            
            # Show display (via X11 forwarding)
            if self.gui_available:
                safe_imshow("Phase 2: Person Following (Raspberry Pi)", display_frame)
            
            # Print status periodically (every 2 seconds)
            current_time = time.time()
            if current_time - last_status_print > 2.0:
                self._print_status()
                last_status_print = current_time
            
            # Handle keyboard input
            key = safe_waitkey(1)
            if key != -1:
                if key == ord('q'):
                    self.running = False
                elif key == ord('s'):
                    self.state = "STOP"
                    self.car.stop()
                    print("\n>>> Emergency stop!")
                elif key == ord('r'):
                    self.state = "SEARCH"
                    self.car.stop()
                    print("\n>>> Reset to SEARCH state")
            
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
                # For now, we don't have depth, so pass None
                control = self.follower.compute_control(
                    self.person_bbox, w, distance_to_person=None
                )
                
                # Check if ready for interaction
                if self.follower.is_ready_for_interaction(
                    self.person_bbox, w, distance_to_person=None
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
                    self.person_bbox, w, distance_to_person=None
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
            "SEARCH": (255, 255, 0),    # Yellow
            "APPROACH": (0, 255, 255),  # Cyan
            "INTERACT": (0, 255, 0),    # Green
            "STOP": (0, 0, 255)         # Red
        }
        state_color = state_colors.get(self.state, (255, 255, 255))
        
        cv2.putText(display, f"State: {self.state}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, state_color, 2)
        
        # Draw person detection info
        if self.person_found:
            cv2.putText(display, "Person: DETECTED", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Draw center line
            cv2.line(display, (w // 2, 0), (w // 2, h), (255, 255, 255), 1)
            
            # Draw person center if bbox available
            if self.person_bbox:
                x_min, y_min, x_max, y_max = self.person_bbox
                person_center_x = (x_min + x_max) // 2
                person_center_y = (y_min + y_max) // 2
                cv2.circle(display, (person_center_x, person_center_y), 5, (0, 255, 0), -1)
                cv2.line(display, (w // 2, person_center_y), (person_center_x, person_center_y), (0, 255, 0), 2)
        else:
            cv2.putText(display, "Person: NOT DETECTED", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Draw car state
        car_state = self.car.get_state()
        direction_text = "STOP"
        if car_state['angular'] > 0.1:
            direction_text = "LEFT TURN"
        elif car_state['angular'] < -0.1:
            direction_text = "RIGHT TURN"
        elif car_state['linear'] > 0.1:
            direction_text = "FORWARD"
        
        cv2.putText(display, f"Command: {direction_text}", (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(display, f"Linear: {car_state['linear']:.2f} m/s", (10, 140),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(display, f"Angular: {car_state['angular']:.2f} rad/s", (10, 170),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        if car_state['simulation']:
            cv2.putText(display, "[SIMULATION MODE]", (10, 200),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 2)
        else:
            cv2.putText(display, "[VESC ACTIVE]", (10, 200),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Add X11 forwarding indicator
        display_env = os.environ.get("DISPLAY", "N/A")
        cv2.putText(display, f"DISPLAY: {display_env}", (10, h - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        return display
    
    def _print_status(self):
        """Print current status to terminal"""
        print(f"\n--- Status (State: {self.state}) ---")
        print(f"Person detected: {self.person_found}")
        if self.person_found and self.person_bbox:
            print(f"Person bbox: {self.person_bbox}")
        car_state = self.car.get_state()
        print(f"Car: linear={car_state['linear']:.2f} m/s, angular={car_state['angular']:.2f} rad/s")
        print(f"Mode: {'SIMULATION' if car_state['simulation'] else 'VESC ACTIVE'}")
        print("-" * 40)
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        self.running = False
        self.car.stop()
        self.car.release()
        self.camera.release()
        if self.gui_available:
            try:
                cv2.destroyAllWindows()
            except:
                pass
        print("Cleanup complete!")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Phase 2: Person Following Demo (Raspberry Pi)')
    parser.add_argument('--target-distance', type=float, default=1.0,
                       help='Target distance to person in meters (default: 1.0)')
    parser.add_argument('--vesc-port', type=str, default=None,
                       help='VESC serial port (e.g., /dev/ttyACM0), None for auto-detect')
    parser.add_argument('--simulation', action='store_true',
                       help='Run in simulation mode (no actual car control)')
    
    args = parser.parse_args()
    
    demo = Phase2Demo(
        target_distance=args.target_distance,
        vesc_port=args.vesc_port,
        simulation_mode=args.simulation
    )
    
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
