"""
Main Application for Air Drawing Project
Uses index finger to draw in the air, visualized on screen
"""
import cv2
import time
from camera import Camera
from finger_tracker import FingerTracker
from drawing_canvas import DrawingCanvas
from ui_display import DrawingUI


class AirDrawingApp:
    def __init__(self):
        """Initialize the air drawing application"""
        print("Initializing Air Drawing Application...")
        
        # Initialize components
        self.camera = Camera(use_oakd=True)
        self.tracker = FingerTracker()
        self.canvas = DrawingCanvas(width=800, height=480)
        self.ui = DrawingUI(screen_width=800, screen_height=480)
        
        # Color presets (BGR format)
        self.colors = {
            '1': (0, 0, 0),      # Black
            '2': (0, 0, 255),    # Red
            '3': (0, 255, 0),    # Green
            '4': (255, 0, 0),    # Blue
            '5': (0, 165, 255),  # Orange
        }
        
        self.running = True
        print("Initialization complete!")
        print("\nControls:")
        print("  - Point index finger to draw")
        print("  - Press 'c' to clear canvas")
        print("  - Press '1'-'5' to change color")
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
            
            # Track index finger
            x, y, is_detected, annotated_frame = self.tracker.get_index_finger_position(frame)
            
            # Add point to drawing
            self.canvas.add_point(x, y, is_detected)
            
            # Create display
            display = self.ui.create_display(
                camera_frame=annotated_frame,
                drawing_canvas=self.canvas.get_canvas(),
                is_drawing=self.canvas.is_drawing,
                current_color=self.canvas.current_color,
                brush_size=self.canvas.brush_size
            )
            
            # Show display
            cv2.imshow("Air Drawing", display)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.running = False
            elif key == ord('c'):
                self.canvas.clear()
                print("Canvas cleared!")
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
        cv2.destroyAllWindows()
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

