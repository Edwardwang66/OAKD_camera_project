"""
Drawing Canvas for Air Drawing
Manages the drawing state and canvas
"""
import numpy as np
import cv2


class DrawingCanvas:
    def __init__(self, width=800, height=480):
        """
        Initialize the drawing canvas
        
        Args:
            width: Canvas width
            height: Canvas height
        """
        self.width = width
        self.height = height
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.canvas.fill(255)  # White background
        
        # Drawing state
        self.drawing_points = []  # List of (x, y) points
        self.current_color = (0, 0, 0)  # BGR color, default black
        self.brush_size = 5
        self.is_drawing = False
        self.last_point = None
    
    def add_point(self, x, y, is_detected):
        """
        Add a point to the drawing
        
        Args:
            x: X coordinate
            y: Y coordinate
            is_detected: Whether finger is detected
        """
        if is_detected and x is not None and y is not None:
            # Map camera coordinates to canvas coordinates
            # Assuming camera is 640x480, map to canvas
            canvas_x = int((x / 640) * self.width)
            canvas_y = int((y / 480) * self.height)
            
            # Clamp to canvas bounds
            canvas_x = max(0, min(canvas_x, self.width - 1))
            canvas_y = max(0, min(canvas_y, self.height - 1))
            
            if self.last_point is not None:
                # Draw line from last point to current point
                cv2.line(self.canvas, self.last_point, (canvas_x, canvas_y), 
                        self.current_color, self.brush_size)
            
            self.last_point = (canvas_x, canvas_y)
            self.is_drawing = True
        else:
            # Finger not detected, stop drawing
            self.last_point = None
            self.is_drawing = False
    
    def clear(self):
        """Clear the canvas"""
        self.canvas.fill(255)  # White background
        self.drawing_points = []
        self.last_point = None
        self.is_drawing = False
    
    def set_color(self, color):
        """
        Set the drawing color
        
        Args:
            color: BGR color tuple (B, G, R)
        """
        self.current_color = color
    
    def set_brush_size(self, size):
        """
        Set the brush size
        
        Args:
            size: Brush size in pixels
        """
        self.brush_size = max(1, min(size, 20))
    
    def get_canvas(self):
        """
        Get the current canvas
        
        Returns:
            numpy.ndarray: Canvas image
        """
        return self.canvas.copy()

