"""
Phase 1 Animated Demo
Creates an alternate UI with simple animations while keeping the existing layout untouched.

Usage:
    python phase1_demo_animated.py
"""
import os
import sys
import time
import math
import cv2
import numpy as np

# Ensure we point to the local X server if a bare display value is provided
display_env = os.environ.get("DISPLAY")
if display_env is None or display_env.isdigit():
    os.environ["DISPLAY"] = ":0"

# Add parent directory to path for shared modules and project-1 components
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PARENT_DIR)
PROJECT1_PATH = os.path.join(PARENT_DIR, "project-1")
sys.path.insert(0, PROJECT1_PATH)

from utils import is_gui_available, safe_imshow, safe_waitkey, print_gui_warning
from phase1_oakd_camera import Phase1OAKDCamera
from phase1_person_detector import PersonDetectorFallback
from phase1_demo import SimplePersonDetector  # Reuse lightweight detector
from game_logic import RockPaperScissorsGame, GameResult
from hand_gesture_detector import HandGestureDetector, Gesture


class AnimatedPhase1Demo:
    """
    Alternate UI with animated overlays for Rock-Paper-Scissors.
    """
    def __init__(self):
        print("=" * 60)
        print("Phase 1: Animated UI Demo")
        print("=" * 60)

        # Initialize camera
        print("\n[1/3] Initializing OAK-D camera with depth...")
        self.camera = Phase1OAKDCamera()

        # Person detector (fallback first, then simple)
        print("\n[2/3] Initializing person detector...")
        try:
            self.person_detector = PersonDetectorFallback()
            if not self.person_detector.available:
                raise RuntimeError("Fallback detector unavailable")
        except Exception:
            print("Using simple MediaPipe detector")
            self.person_detector = SimplePersonDetector()

        # RPS game + gesture detector
        print("\n[3/3] Initializing RPS game + gesture detector...")
        self.game = RockPaperScissorsGame()
        self.gesture_detector = HandGestureDetector()

        # GUI
        self.gui_available = is_gui_available()
        if not self.gui_available:
            print_gui_warning()
        else:
            self.window_name = "Phase 1: Animated UI"
            try:
                cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
                cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            except Exception:
                pass

        # State
        self.running = True
        self.person_found = False
        self.person_bbox = None
        self.distance_to_person = None
        self.current_player_gesture = Gesture.NONE
        self.gesture_hold_time = 0
        # Require fewer steady frames to lock gesture so rounds start faster
        self.gesture_hold_threshold = 10
        self.last_result = None
        self.last_display_result = None
        self.last_ai_choice = None
        self.locked_gesture = None
        self.last_completed_gesture = None
        self.waiting_for_new_gesture = False
        self.post_round_cooldown_seconds = 2.0
        self.post_round_cooldown_until = None
        self.countdown_start = None
        # Countdown duration (longer for 3-2-1 pacing)
        self.countdown_duration = 2.0
        self.anim_start = None
        self.anim_duration = 1.2

        print("\nControls: 'q' quit, 'r' reset scores\n")

    def run(self):
        frame_count = 0
        while self.running:
            frame = self.camera.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            depth_frame = self.camera.get_depth_frame()

            # Person detection
            person_found, person_bbox, annotated_frame = self.person_detector.detect_person(frame)
            self.person_found = person_found
            self.person_bbox = person_bbox

            if person_found and person_bbox and depth_frame is not None:
                self.distance_to_person = self.camera.get_distance_from_bbox(person_bbox, depth_frame)
            else:
                self.distance_to_person = None

            # Gesture detection
            gesture, gesture_frame = self.gesture_detector.detect_gesture(frame)
            if gesture != Gesture.NONE:
                if gesture == self.current_player_gesture:
                    self.gesture_hold_time += 1
                else:
                    self.current_player_gesture = gesture
                    self.gesture_hold_time = 1
            else:
                self.current_player_gesture = Gesture.NONE
                self.gesture_hold_time = 0

            hand_detected = gesture != Gesture.NONE

            # Cooldown ticking after a round (time-based)
            cooldown_ready = False
            if self.waiting_for_new_gesture:
                if self.post_round_cooldown_until and time.time() >= self.post_round_cooldown_until:
                    cooldown_ready = True

            # Play round when gesture held steady
            ready_for_new_round = (
                self.gesture_hold_time >= self.gesture_hold_threshold and
                self.current_player_gesture != Gesture.NONE and
                # If we're waiting, require a changed gesture from the last completed round
                (not self.waiting_for_new_gesture or
                 (self.last_completed_gesture is not None and
                 self.current_player_gesture != self.last_completed_gesture) or
                 cooldown_ready)
            )

            if ready_for_new_round and self.game.result is None and self.countdown_start is None:
                # Lock gesture and start countdown
                self.last_display_result = None
                self.last_ai_choice = None
                self.locked_gesture = self.current_player_gesture
                self.waiting_for_new_gesture = False
                self.countdown_start = time.time()
                self.anim_start = None

            # Countdown handling
            countdown_remaining = None
            if self.countdown_start:
                elapsed = time.time() - self.countdown_start
                countdown_remaining = max(0.0, self.countdown_duration - elapsed)
                if countdown_remaining <= 0.0:
                    # Time to play the round
                    self.countdown_start = None
                    self.last_result = self.game.play_round(self.locked_gesture)
                    self.last_display_result = self.last_result
                    self.last_ai_choice = self.game.ai_choice
                    self.anim_start = time.time()

            # Auto-reset round after animation completes and hand released
            if self.last_result and self.anim_start:
                anim_elapsed = time.time() - self.anim_start
                if anim_elapsed > self.anim_duration:
                    self.game.reset_round()
                    # Keep display result for suspense, but require gesture change to restart
                    self.last_result = None
                    self.last_completed_gesture = self.locked_gesture
                    self.waiting_for_new_gesture = True
                    self.post_round_cooldown_until = time.time() + self.post_round_cooldown_seconds
                    # Keep locked gesture and anim_start for continued bobbing
                    self.gesture_hold_time = 0
                    self.current_player_gesture = Gesture.NONE

            display_frame = self._create_animated_ui(
                frame_shape=frame.shape,
                person_found=person_found,
                hand_found=hand_detected,
                distance=self.distance_to_person,
                gesture=self.current_player_gesture,
                result=self.last_display_result,
                locked_gesture=self.locked_gesture,
                ai_choice=self.last_ai_choice,
                countdown_remaining=countdown_remaining,
                player_score=self.game.player_score,
                ai_score=self.game.ai_score,
                round_count=self.game.round_count,
                anim_start=self.anim_start
            )

            if self.gui_available:
                safe_imshow(self.window_name, display_frame)

            key = safe_waitkey(1)
            if key == ord('q'):
                self.running = False
            elif key == ord('r'):
                self.game.reset_game()
                self.last_result = None
                self.gesture_hold_time = 0
                print("Scores reset!")

            frame_count += 1

        print("\nDemo ended.")
        self.cleanup()

    def _create_animated_ui(self, frame_shape, person_found, hand_found, distance,
                            gesture, result, locked_gesture, ai_choice,
                            countdown_remaining,
                            player_score, ai_score, round_count, anim_start):
        """
        Compose an animated UI frame without showing the camera feed.
        """
        h, w = frame_shape[:2]
        # Use a fixed canvas for cleaner UI (no camera feed)
        canvas_w, canvas_h = 1280, 720
        canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)

        # Static background
        canvas[:] = (25, 35, 45)

        # Panel on the right
        panel_w = int(canvas_w * 0.32)
        panel_x = canvas_w - panel_w + 20
        panel_y = 60

        # Centered big score at top
        score_text = f"Player {player_score} : {ai_score} AI"
        score_size, _ = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 1.4, 3)
        cv2.putText(canvas, score_text, (canvas_w // 2 - score_size[0] // 2, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3, cv2.LINE_AA)

        # Title
        cv2.putText(canvas, "ROCK PAPER SCISSORS", (panel_x, panel_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Status
        status_text = "Person: DETECTED" if person_found else "Person: NOT DETECTED"
        status_color = (0, 255, 0) if person_found else (0, 0, 255)
        cv2.putText(canvas, status_text, (panel_x, panel_y + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        hand_text = "Hand: DETECTED" if hand_found else "Hand: NOT DETECTED"
        hand_color = (0, 255, 0) if hand_found else (0, 0, 255)
        cv2.putText(canvas, hand_text, (panel_x, panel_y + 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, hand_color, 2)

        # Minimal status
        cv2.putText(canvas, f"Gesture: {gesture.value.upper() if gesture else 'NONE'}",
                    (panel_x, panel_y + 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (240, 240, 240), 2)

        # Countdown overlay
        if countdown_remaining is not None:
            count_num = int(math.ceil(countdown_remaining))
            alpha = 1.0 - (countdown_remaining - int(countdown_remaining))
            overlay = canvas.copy()
            cv2.putText(overlay, str(max(1, count_num)), (canvas_w // 2 - 40, canvas_h // 2 + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 3.5, (255, 255, 255), 8, cv2.LINE_AA)
            cv2.circle(overlay, (canvas_w // 2, canvas_h // 2 - 10), 110, (0, 200, 255), 12)
            cv2.addWeighted(overlay, 0.7, canvas, 0.3, 0, canvas)
            cv2.addWeighted(overlay, alpha, canvas, 1 - alpha, 0, canvas)
        elif result:
            # Determine if we're ready to show winner box
            show_winner = False
            elapsed = 0.0
            if anim_start:
                elapsed = time.time() - anim_start
                show_winner = elapsed > self.anim_duration + 0.8

            if not show_winner:
                # During transition, flash GO without altering winner box background
                overlay = canvas.copy()
                cv2.putText(overlay, "GO!", (canvas_w // 2 - 60, canvas_h // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 255, 180), 8, cv2.LINE_AA)
                cv2.addWeighted(overlay, 0.4, canvas, 0.6, 0, canvas)

            # Winner popup after animation completes + small delay to show AI choice
            winner_str = "Tie"
            if hasattr(result, "value"):
                if result.value == "player_wins":
                    winner_str = "Player"
                elif result.value == "ai_wins":
                    winner_str = "AI"
            if show_winner:
                popup_text = f"Winner: {winner_str}"
                # Centered solid box (no screen-wide overlay)
                box_w, box_h = 520, 220
                box_x1 = canvas_w // 2 - box_w // 2
                box_y1 = canvas_h // 2 - box_h // 2
                box_x2 = canvas_w // 2 + box_w // 2
                box_y2 = canvas_h // 2 + box_h // 2
                cv2.rectangle(canvas, (box_x1, box_y1),
                              (box_x2, box_y2),
                              (30, 60, 90), -1)
                cv2.rectangle(canvas, (box_x1, box_y1),
                              (box_x2, box_y2),
                              (0, 255, 180), 4)
                # Center the text
                text_size, _ = cv2.getTextSize(popup_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)
                text_x = canvas_w // 2 - text_size[0] // 2
                text_y = canvas_h // 2 + text_size[1] // 2
                cv2.putText(canvas, popup_text, (text_x, text_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)
                # Re-draw score on top
                score_text = f"Player {player_score} : {ai_score} AI"
                score_size, _ = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 1.4, 3)
                score_x = canvas_w // 2 - score_size[0] // 2
                cv2.putText(canvas, score_text, (score_x, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3, cv2.LINE_AA)

        # Hand-vs-hand animation when result is available
        if result and ai_choice and locked_gesture:
            # Keep motion alive even after reveal
            if anim_start:
                elapsed = time.time() - anim_start
                base_progress = min(1.0, elapsed / self.anim_duration)
                if elapsed > self.anim_duration:
                    wobble = 0.5 + 0.5 * (0.5 * (1 + math.sin(time.time() * 2.0)))
                    anim_progress = 0.7 + 0.3 * wobble
                else:
                    anim_progress = base_progress
            else:
                wobble = 0.5 + 0.5 * (0.5 * (1 + math.sin(time.time() * 2.0)))
                anim_progress = 0.7 + 0.3 * wobble
            self._draw_hand_duel(canvas, canvas_w, canvas_h, locked_gesture, ai_choice, anim_progress)

        return canvas

    def _draw_hand_duel(self, canvas, canvas_w, canvas_h, player_choice, ai_choice, progress):
        """
        Draw two stylized ASCII-like hand tiles that bob toward each other, then reveal final choices.
        """
        center_y = canvas_h // 2 + 40
        offset = int(40 * (1 - progress) * math.sin(progress * math.pi))

        # Positions
        player_pos = (int(canvas_w * 0.28), center_y - offset)
        ai_pos = (int(canvas_w * 0.72), center_y + offset)

        # Slot-machine style cycle for AI, steady for player
        throw_cycle = ["ROCK", "PAPER", "SCISSORS"]
        # Player stays on locked choice
        player_label = player_choice.value.upper()
        # AI cycles quickly then slows into final choice
        speed = 10 * (1 - progress) + 2  # fast at start, slower near reveal
        cycle_idx = int(time.time() * speed) % 3
        ai_label = throw_cycle[cycle_idx] if progress < 0.7 else ai_choice.value.upper()

        self._draw_ascii_hand(canvas, player_pos, (90, 200, 255), player_label, label_prefix="YOU")
        self._draw_ascii_hand(canvas, ai_pos, (255, 140, 140), ai_label, label_prefix="AI")

    def _draw_ascii_hand(self, canvas, center, color, choice_label, label_prefix=""):
        """
        Draw a pseudo-3D ASCII hand using text blocks.
        """
        x, y = center
        art = {
            "ROCK": [
                "    _______    ",
                "---'   ____)   ",
                "      (_____)  ",
                "      (_____)  ",
                "      (____)   ",
                "---.__(___)    "
            ],
            "PAPER": [
                "     _______     ",
                "---'    ____)____",
                "           ______)",
                "          _______)",
                "         _______) ",
                "---.__________)   "
            ],
            "SCISSORS": [
                "    _______    ",
                "---'   ____)____",
                "          ______)",
                "       __________)",
                "      (____)     ",
                "---.__(___)      "
            ]
        }
        lines = art.get(choice_label, [""])
        # Default sizing
        font_scale = 0.7
        line_height = 28
        start_y = y - (len(lines) * line_height) // 2

        # Shadow
        for idx, line in enumerate(lines):
            ly = start_y + idx * line_height
            cv2.putText(canvas, line, (x - 80 + 2, ly + 2),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), 3, cv2.LINE_AA)

        # Foreground
        for idx, line in enumerate(lines):
            ly = start_y + idx * line_height
            cv2.putText(canvas, line, (x - 80, ly),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 2, cv2.LINE_AA)

        # Labels
        if label_prefix:
            cv2.putText(canvas, label_prefix, (x - 70, y - 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(canvas, choice_label, (x - 60, y + 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

    def cleanup(self):
        self.running = False
        self.camera.release()
        if hasattr(self.person_detector, "release"):
            self.person_detector.release()
        if hasattr(self.gesture_detector, "release"):
            self.gesture_detector.release()
        if self.gui_available:
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass


def main():
    demo = AnimatedPhase1Demo()
    try:
        demo.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        demo.cleanup()


if __name__ == "__main__":
    main()
