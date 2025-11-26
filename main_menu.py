"""
Main Menu System
Integrates user recognition, registration, and game selection
"""
import cv2
import time
import sys
import os

# Add project directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project-1'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project-2'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project-3'))

# Import camera from root directory
from camera import Camera
from user_registration import UserRegistration
from game_menu import GameMenu, GameChoice
from registration_ui import RegistrationUI
from utils import is_gui_available, safe_imshow, safe_waitkey, print_gui_warning


class MainMenuSystem:
    def __init__(self):
        """Initialize main menu system"""
        print("=" * 60)
        print("OAKD Camera Projects - Main Menu")
        print("=" * 60)
        print("\nInitializing...")
        
        # Initialize components
        self.camera = Camera(use_oakd=True)
        self.registration = UserRegistration()
        self.menu = GameMenu(screen_width=800, screen_height=480)
        self.reg_ui = RegistrationUI(screen_width=800, screen_height=480)
        
        self.running = True
        self.current_user = None
        self.is_stranger = True
        
        # Check GUI availability
        self.gui_available = is_gui_available()
        if not self.gui_available:
            print_gui_warning()
        
        print("Initialization complete!")
        print("\nSystem ready. Looking for users...")
    
    def recognize_user(self, frame):
        """
        Recognize user from frame
        
        Returns:
            tuple: (user_name, is_stranger, annotated_frame)
        """
        user_name, confidence, annotated_frame = self.registration.recognize_user(frame)
        
        if user_name:
            return user_name, False, annotated_frame
        else:
            return None, True, annotated_frame
    
    def register_new_user(self):
        """Register a new user"""
        print("\n=== User Registration ===")
        print("Enter user name (type on keyboard, press ENTER when done):")
        
        # Simple name input (in production, use proper input method)
        name = input("Name: ").strip()
        
        if not name:
            print("Registration cancelled.")
            return False
        
        if name in self.registration.get_registered_users():
            print(f"User '{name}' already exists!")
            return False
        
        print(f"\nCollecting face samples for {name}...")
        print("Look at the camera and press SPACE to capture samples.")
        print("Press ENTER when you have enough samples (at least 5).")
        
        samples = []
        samples_needed = 5
        status_message = ""
        
        while len(samples) < samples_needed:
            frame = self.camera.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue
            
            # Flip for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect face
            faces, frame_with_faces = self.registration.detect_face(frame)
            
            # Create registration display
            display = self.reg_ui.create_registration_display(
                camera_frame=frame_with_faces,
                samples_collected=len(samples),
                total_samples=samples_needed,
                user_name=name,
                status_message=status_message
            )
            
            if self.gui_available:
                safe_imshow("User Registration", display)
            
            key = safe_waitkey(1)
            
            if key == ord(' '):  # Space to capture
                if len(faces) > 0:
                    samples.append(frame.copy())
                    status_message = f"Sample {len(samples)} captured!"
                    print(f"Sample {len(samples)}/{samples_needed} captured")
                else:
                    status_message = "No face detected!"
            
            elif key == 13:  # Enter to finish
                if len(samples) >= 3:  # Minimum 3 samples
                    break
                else:
                    status_message = f"Need at least 3 samples! ({len(samples)} collected)"
            
            elif key == ord('q'):
                print("Registration cancelled.")
                cv2.destroyAllWindows()
                return False
        
        # Register user
        if self.registration.register_user(name, samples):
            print(f"User '{name}' registered successfully!")
            cv2.destroyAllWindows()
            return True
        else:
            print("Registration failed!")
            cv2.destroyAllWindows()
            return False
    
    def run_menu(self):
        """Run main menu loop"""
        print("\n=== Main Menu ===")
        
        while self.running:
            frame = self.camera.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue
            
            # Flip frame for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Recognize user (check every 30 frames to reduce computation)
            if int(time.time() * 10) % 30 == 0:  # Check roughly 3 times per second
                self.current_user, self.is_stranger, annotated_frame = self.recognize_user(frame)
            else:
                # Use previous recognition result
                _, _, annotated_frame = self.registration.recognize_user(frame)
                # Draw current user status
                if self.current_user:
                    h, w = annotated_frame.shape[:2]
                    cv2.putText(annotated_frame, f"User: {self.current_user}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    cv2.putText(annotated_frame, "Stranger", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Create menu display
            display = self.menu.create_menu_display(
                camera_frame=annotated_frame,
                user_name=self.current_user,
                is_stranger=self.is_stranger
            )
            
            if self.gui_available:
                safe_imshow("Main Menu - Game Selection", display)
            
            # Handle keyboard input
            key = safe_waitkey(1)
            choice = self.menu.handle_key(key)
            
            if choice == GameChoice.REGISTER:
                cv2.destroyAllWindows()
                self.register_new_user()
                # Reopen menu window
                continue
            
            elif choice == GameChoice.QUIT:
                self.running = False
                break
            
            elif choice in [GameChoice.GAME_1, GameChoice.GAME_2, GameChoice.GAME_3]:
                cv2.destroyAllWindows()
                self.launch_game(choice)
                # Return to menu after game
                continue
    
    def launch_game(self, game_choice):
        """
        Launch the selected game
        
        Args:
            game_choice: GameChoice enum
        """
        print(f"\n=== Launching {game_choice.value} ===")
        
        try:
            if game_choice == GameChoice.GAME_1:
                # Rock-Paper-Scissors
                sys.path.insert(0, 'project-1')
                from main import RockPaperScissorsApp
                app = RockPaperScissorsApp()
                app.run()
                app.cleanup()
            
            elif game_choice == GameChoice.GAME_2:
                # Air Drawing
                sys.path.insert(0, 'project-2')
                from main import AirDrawingApp
                app = AirDrawingApp()
                app.run()
                app.cleanup()
            
            elif game_choice == GameChoice.GAME_3:
                # Shooting Game
                sys.path.insert(0, 'project-3')
                from main import ShootingGameApp
                app = ShootingGameApp()
                app.run()
                app.cleanup()
        
        except Exception as e:
            print(f"Error launching game: {e}")
            import traceback
            traceback.print_exc()
            input("Press ENTER to return to menu...")
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        self.camera.release()
        if self.gui_available:
            try:
                cv2.destroyAllWindows()
            except:
                pass
        print("Cleanup complete!")


def main():
    """Main entry point"""
    menu_system = MainMenuSystem()
    
    try:
        menu_system.run_menu()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        menu_system.cleanup()


if __name__ == "__main__":
    main()

