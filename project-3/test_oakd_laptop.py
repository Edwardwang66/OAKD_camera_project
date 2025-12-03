"""
Test script for Project-3 on Laptop
Uses OAKD camera for input but displays on laptop screen
Perfect for testing OAKD camera when connected to laptop
"""
import cv2
import time
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import is_gui_available, safe_imshow, safe_waitkey, print_gui_warning
from oakd_camera_only import OAKDCameraOnly
from pistol_detector import PistolDetector
from game_logic import ShootingGame, GameState
from ui_display import RefereeUI


class ShootingGameLaptopApp:
    def __init__(self, max_health=3):
        """Initialize the shooting game application for laptop with OAKD camera"""
        print("=" * 60)
        print("1v1 SHOOTING GAME - LAPTOP TEST (OAKD Camera)")
        print("=" * 60)
        print("\nInitializing...")
        print("Note: This script uses OAKD camera but displays on laptop screen")
        
        # Initialize components - Force OAKD camera only (no webcam fallback)
        print("\nConnecting to OAKD camera...")
        try:
            self.camera = OAKDCameraOnly()
            print("✓ OAKD camera connected successfully!")
        except RuntimeError as e:
            print(f"\n✗ ERROR: {e}")
            print("\nThis script requires OAKD camera.")
            print("Please connect OAKD camera via USB and try again.")
            raise
        except Exception as e:
            print(f"\n✗ ERROR: Could not initialize OAKD camera: {e}")
            raise
        
        self.detector = PistolDetector()
        self.game = ShootingGame(max_health=max_health)
        self.ui = RefereeUI(screen_width=800, screen_height=480, max_health=max_health)
        
        # Check GUI availability (should be available on laptop)
        self.gui_available = is_gui_available()
        if not self.gui_available:
            print_gui_warning()
            print("\nNote: GUI not available. Game will run but no windows will display.")
        else:
            print("GUI available - windows will display on laptop screen")
        
        self.running = True
        self.hit_display_time = 0
        self.hit_display_duration = 30  # Frames to show hit message
        
        print("\nInitialization complete!")
        print("\nGame Rules:")
        print("  - Two players face off")
        print("  - Make pistol gesture (index finger + thumb up)")
        print("  - Point at opponent to shoot")
        print("  - First to lose all health loses!")
        print("\nControls:")
        print("  - Press 's' to start game")
        print("  - Press 'r' to reset game")
        print("  - Press 'q' to quit")
        print("\nConfiguration:")
        print("  Camera: OAKD Lite (required, no webcam fallback)")
        print("  Display: Laptop Screen")
        print("  Mode: Full game with referee UI")
    
    def run(self):
        """Main application loop"""
        print("\nWaiting for game to start...")
        print("Make sure OAKD camera is pointing at both players")
        
        frame_count = 0
        
        while self.running:
            # Get frame from OAKD camera
            frame = self.camera.get_frame()
            
            if frame is None:
                time.sleep(0.01)
                continue
            
            # Note: OAKD camera frame - no flip needed unless desired
            # Uncomment below if you want mirror effect:
            # frame = cv2.flip(frame, 1)
            
            # Detect pistol gestures
            players = self.detector.detect_pistol_gestures(frame)
            player_a_state = players['player_a']
            player_b_state = players['player_b']
            annotated_frame = players['annotated_frame']
            
            # Draw visual indicators on frame
            self._draw_shooting_indicators(annotated_frame, player_a_state, player_b_state)
            
            # Update game if playing
            hit_info = None
            if self.game.state == GameState.PLAYING:
                hit_info = self.game.update(player_a_state, player_b_state)
                
                # Update hit display timer
                if hit_info.get('hit_occurred'):
                    self.hit_display_time = self.hit_display_duration
                    # Announce hit
                    hit_player = hit_info.get('hit_player')
                    print(f"\n*** PLAYER {hit_player} HIT! ***")
            
            # Decrease hit display timer
            if self.hit_display_time > 0:
                self.hit_display_time -= 1
                if self.hit_display_time > 0:
                    hit_info = {'hit_occurred': True, 'hit_player': self.game.last_hit_player}
            
            # Check for game end
            if self.game.state in [GameState.PLAYER_A_WINS, GameState.PLAYER_B_WINS]:
                winner = "A" if self.game.state == GameState.PLAYER_A_WINS else "B"
                print(f"\n{'='*60}")
                print(f"!!! PLAYER {winner} WINS !!!")
                print(f"{'='*60}\n")
                self.game.state = GameState.GAME_OVER
            
            # Get health
            health = self.game.get_health()
            
            # Create display
            display = self.ui.create_display(
                camera_frame=annotated_frame,
                player_a_state=player_a_state,
                player_b_state=player_b_state,
                game_state=self.game.state,
                health_a=health['player_a'],
                health_b=health['player_b'],
                hit_info=hit_info
            )
            
            # Show display on laptop screen
            if self.gui_available:
                safe_imshow("1v1 Shooting Game - OAKD Camera (Laptop Display)", display)
            
            # Handle keyboard input
            key = safe_waitkey(1)
            if key == ord('q'):
                self.running = False
            elif key == ord('s') and self.game.state == GameState.WAITING:
                self.game.start_game()
                print("\nGame started! Players ready...")
            elif key == ord('r'):
                self.game.reset_game()
                self.hit_display_time = 0
                print("Game reset!")
            
            frame_count += 1
    
    def _draw_shooting_indicators(self, frame, player_a_state, player_b_state):
        """
        Draw visual indicators on camera frame showing shooting direction
        
        Args:
            frame: Camera frame
            player_a_state: Player A state
            player_b_state: Player B state
        """
        h, w = frame.shape[:2]
        
        # Draw shooting lines if pistol detected
        if player_a_state['has_pistol'] and player_a_state['index_pos']:
            start_pos = player_a_state['index_pos']
            # Draw line showing shooting direction
            if player_a_state['pointing_at'].value == 'right':
                end_pos = (w, start_pos[1])
                cv2.arrowedLine(frame, start_pos, end_pos, (0, 255, 0), 3)
                cv2.putText(frame, "A -> B", (start_pos[0] + 10, start_pos[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        if player_b_state['has_pistol'] and player_b_state['index_pos']:
            start_pos = player_b_state['index_pos']
            # Draw line showing shooting direction
            if player_b_state['pointing_at'].value == 'left':
                end_pos = (0, start_pos[1])
                cv2.arrowedLine(frame, start_pos, end_pos, (0, 0, 255), 3)
                cv2.putText(frame, "B -> A", (start_pos[0] - 60, start_pos[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        self.camera.release()
        self.detector.release()
        if self.gui_available:
            try:
                cv2.destroyAllWindows()
            except:
                pass
        print("Cleanup complete!")


def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("OAKD Camera Test - Shooting Game")
    print("=" * 60)
    print("\nThis script:")
    print("  ✓ Uses OAKD camera for input")
    print("  ✓ Displays on laptop screen")
    print("  ✓ Perfect for testing OAKD camera on laptop")
    print("\nMake sure OAKD camera is connected via USB")
    print("=" * 60 + "\n")
    
    app = ShootingGameLaptopApp(max_health=3)
    
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

