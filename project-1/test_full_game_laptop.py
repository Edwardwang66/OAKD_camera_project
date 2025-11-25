"""
Full game test for laptop (uses webcam, no OAKD required)
Test the complete rock-paper-scissors game on your laptop
"""
import cv2
from hand_gesture_detector import HandGestureDetector, Gesture
from game_logic import RockPaperScissorsGame, GameResult
from ui_display import GameUI


def test_full_game_laptop():
    """Test the full game on laptop with webcam"""
    print("=" * 50)
    print("Full Game Test - Rock Paper Scissors")
    print("=" * 50)
    print("\nInstructions:")
    print("1. Show your hand to the camera")
    print("2. Hold your gesture steady for ~1 second to play")
    print("3. The game will show your choice vs Donkey Car's choice")
    print("4. Press 'q' to quit, 'r' to reset scores\n")
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Could not open webcam!")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Initialize components
    detector = HandGestureDetector()
    game = RockPaperScissorsGame()
    ui = GameUI(screen_width=800, screen_height=480)
    
    # Game state
    current_gesture = Gesture.NONE
    gesture_hold_time = 0
    gesture_hold_threshold = 30  # Frames to hold gesture
    last_result = None
    
    print("Game started! Show your hand to play...\n")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame horizontally
            frame = cv2.flip(frame, 1)
            
            # Detect gesture
            gesture, annotated_frame = detector.detect_gesture(frame)
            
            # Update current gesture
            if gesture != Gesture.NONE:
                if gesture == current_gesture:
                    gesture_hold_time += 1
                else:
                    current_gesture = gesture
                    gesture_hold_time = 1
            else:
                current_gesture = Gesture.NONE
                gesture_hold_time = 0
            
            # Play round if gesture held long enough
            if (gesture_hold_time >= gesture_hold_threshold and 
                current_gesture != Gesture.NONE and
                game.result is None):
                # Play the round
                last_result = game.play_round(current_gesture)
                print(f"Round {game.round_count}: "
                      f"Player: {current_gesture.value}, "
                      f"AI: {game.ai_choice.value}, "
                      f"Result: {last_result.value}")
            
            # Reset round after showing result
            if last_result and gesture_hold_time < 10:
                game.reset_round()
                last_result = None
            
            # Create display
            display = ui.create_display(
                camera_frame=annotated_frame,
                player_gesture=current_gesture,
                ai_gesture=game.ai_choice,
                game_result=last_result,
                player_score=game.player_score,
                ai_score=game.ai_score,
                round_count=game.round_count
            )
            
            # Show display
            cv2.imshow("Rock Paper Scissors - Laptop Test", display)
            
            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                game.reset_game()
                print("Game reset!")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cap.release()
        detector.release()
        cv2.destroyAllWindows()
        print("\nFinal Score - Player: {}, Donkey Car: {}".format(
            game.player_score, game.ai_score))
        print("Test complete!")


if __name__ == "__main__":
    test_full_game_laptop()

