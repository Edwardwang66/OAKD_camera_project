"""
Main Application for Air Drawing Project
Uses index finger to draw, fist to stop drawing
Detects what is being drawn using a simple classifier
"""
import cv2
import time
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import is_gui_available, safe_imshow, safe_waitkey, print_gui_warning
from camera import Camera
from finger_tracker import FingerTracker, DrawingGesture
from drawing_canvas import DrawingCanvas
from drawing_classifier import DrawingClassifier, DrawingType
from ui_display import DrawingUI


class AirDrawingApp:
    def __init__(self):
        """Initialize the air drawing application"""
        print("Initializing Air Drawing Application...")
        
        # Initialize components
        self.camera = Camera(use_oakd=True)
        self.tracker = FingerTracker()
        self.canvas = DrawingCanvas(width=800, height=480)
        self.classifier = DrawingClassifier(use_heuristic=True)
        self.ui = DrawingUI(screen_width=800, screen_height=480)
        
        # Color presets (BGR format)
        self.colors = {
            '1': (0, 0, 0),      # Black
            '2': (0, 0, 255),    # Red
            '3': (0, 255, 0),    # Green
            '4': (255, 0, 0),    # Blue
            '5': (0, 165, 255),  # Orange
        }
        
        # Drawing detection state
        self.detected_drawing = DrawingType.UNKNOWN
        self.detection_confidence = 0.0
        self.last_detection_time = 0
        self.detection_interval = 30  # Check every 30 frames
        
        # Check GUI availability
        self.gui_available = is_gui_available()
        if not self.gui_available:
            print_gui_warning()
        
        self.running = True
        print("Initialization complete!")
        print("\nControls:")
        print("  - Point index finger to draw")
        print("  - Make a fist to stop drawing (lift pen)")
        print("  - Press 'c' to clear canvas")
        print("  - Press '1'-'5' to change color")
        print("  - Press 'd' to detect what you drew")
        print("  - Press 'q' to quit")
    
    def run(self):
        """Main application loop"""
        print("\nStarting air drawing...")
        
        while self.running:
            # Get frame from camera
            frame = self.camera.get_frame()
            
            if frame is None:
                time.sleep(0.01)
                continue
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Track finger and detect gesture (fist vs index finger)
            x, y, gesture, can_draw, annotated_frame = self.tracker.get_finger_state(frame)
            
            # Add point to drawing (only if can_draw is True)
            self.canvas.add_point(x, y, can_draw)
            
            # Periodically detect what is being drawn
            frame_count = getattr(self, 'frame_count', 0)
            frame_count += 1
            self.frame_count = frame_count
            
            if frame_count % self.detection_interval == 0:
                detected_type, confidence = self.classifier.classify_drawing(self.canvas.get_canvas())
                if confidence > 0.5:  # Only update if confident
                    self.detected_drawing = detected_type
                    self.detection_confidence = confidence
                    self.last_detection_time = frame_count
            
            # Create display
            display = self.ui.create_display(
                camera_frame=annotated_frame,
                drawing_canvas=self.canvas.get_canvas(),
                is_drawing=self.canvas.is_drawing,
                current_color=self.canvas.current_color,
                brush_size=self.canvas.brush_size,
                detected_drawing=self.detected_drawing,
                detection_confidence=self.detection_confidence
            )
            
            # Show display
            if self.gui_available:
                safe_imshow("Air Drawing", display)
            
            # Handle keyboard input
            key = safe_waitkey(1)
            if key == ord('q'):
                self.running = False
            elif key == ord('c'):
                self.canvas.clear()
                self.detected_drawing = DrawingType.UNKNOWN
                self.detection_confidence = 0.0
                print("Canvas cleared!")
            elif key == ord('d'):
                # Force detection
                detected_type, confidence = self.classifier.classify_drawing(self.canvas.get_canvas())
                self.detected_drawing = detected_type
                self.detection_confidence = confidence
                print(f"Detected: {detected_type.value} (confidence: {confidence:.2f})")
            elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
                color_key = chr(key)
                self.canvas.set_color(self.colors[color_key])
                color_names = {'1': 'Black', '2': 'Red', '3': 'Green', '4': 'Blue', '5': 'Orange'}
                print(f"Color changed to: {color_names[color_key]}")
            elif key == ord('+') or key == ord('='):
                self.canvas.set_brush_size(self.canvas.brush_size + 1)
                print(f"Brush size: {self.canvas.brush_size}")
            elif key == ord('-') or key == ord('_'):
                self.canvas.set_brush_size(self.canvas.brush_size - 1)
                print(f"Brush size: {self.canvas.brush_size}")
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        self.camera.release()
        self.tracker.release()
        if self.gui_available:
            try:
                cv2.destroyAllWindows()
            except:
                pass
        print("Cleanup complete!")


def main():
    """Main entry point"""
    app = AirDrawingApp()
    
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

