"""
UI Display for Air Drawing Project
Creates the display interface for the 7-inch screen
"""
import cv2
import numpy as np


class DrawingUI:
    def __init__(self, screen_width=800, screen_height=480):
        """
        Initialize the UI display
        
        Args:
            screen_width: Width of the display screen
            screen_height: Height of the display screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def create_display(self, camera_frame, drawing_canvas, is_drawing, 
                      current_color=(0, 0, 0), brush_size=5,
                      detected_drawing=None, detection_confidence=0.0):
        """
        Create the combined display showing camera feed and drawing canvas
        
        Args:
            camera_frame: Frame from camera (will be resized)
            drawing_canvas: Canvas with the drawing
            is_drawing: Whether currently drawing
            current_color: Current drawing color
            brush_size: Current brush size
            detected_drawing: Detected drawing type (DrawingType enum)
            detection_confidence: Confidence of detection (0-1)
            
        Returns:
            numpy.ndarray: Combined display frame
        """
        # Create blank display
        display = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        display.fill(30)  # Dark background
        
        # Layout: Camera feed on left, drawing canvas on right
        camera_width = int(self.screen_width * 0.5)
        canvas_width = self.screen_width - camera_width
        
        # Resize and place camera frame
        if camera_frame is not None:
            camera_resized = cv2.resize(camera_frame, (camera_width, self.screen_height))
            display[:, :camera_width] = camera_resized
        
        # Place drawing canvas
        if drawing_canvas is not None:
            canvas_resized = cv2.resize(drawing_canvas, (canvas_width, self.screen_height))
            display[:, camera_width:] = canvas_resized
        
        # Draw dividing line
        cv2.line(display, (camera_width, 0), 
                (camera_width, self.screen_height), (100, 100, 100), 2)
        
        # Draw status indicators
        status_y = 20
        
        # Drawing status
        status_text = "DRAWING" if is_drawing else "READY"
        status_color = (0, 255, 0) if is_drawing else (100, 100, 100)
        cv2.putText(display, status_text, (camera_width + 10, status_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        # Color indicator
        color_y = status_y + 30
        cv2.putText(display, "Color:", (camera_width + 10, color_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        # Draw color circle
        color_circle_x = camera_width + 80
        color_circle_y = color_y - 10
        cv2.circle(display, (color_circle_x, color_circle_y), 10, current_color, -1)
        cv2.circle(display, (color_circle_x, color_circle_y), 10, (255, 255, 255), 1)
        
        # Brush size
        brush_y = color_y + 25
        cv2.putText(display, f"Brush: {brush_size}px", (camera_width + 10, brush_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Drawing detection result
        detection_y = brush_y + 30
        if detected_drawing is not None and detection_confidence > 0.5:
            detection_text = f"Detected: {detected_drawing.value.upper()}"
            confidence_text = f"({detection_confidence:.0%})"
            cv2.putText(display, detection_text, (camera_width + 10, detection_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            cv2.putText(display, confidence_text, (camera_width + 10, detection_y + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Instructions at bottom
        instructions_y = self.screen_height - 80
        cv2.putText(display, "Index finger = Draw | Fist = Stop", 
                   (camera_width + 10, instructions_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        cv2.putText(display, "Press 'c' to clear | 'd' to detect", 
                   (camera_width + 10, instructions_y + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        cv2.putText(display, "Press '1'-'5' to change color | 'q' to quit", 
                   (camera_width + 10, instructions_y + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        
        return display

