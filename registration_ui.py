"""
User Registration UI
Handles the user registration process with visual feedback
"""
import cv2
import numpy as np


class RegistrationUI:
    def __init__(self, screen_width=800, screen_height=480):
        """
        Initialize registration UI
        
        Args:
            screen_width: Width of display screen
            screen_height: Height of display screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def create_registration_display(self, camera_frame, samples_collected, total_samples, 
                                   user_name=None, status_message=""):
        """
        Create registration display during user registration
        
        Args:
            camera_frame: Frame from camera
            samples_collected: Number of face samples collected
            total_samples: Total samples needed
            user_name: Name being registered
            status_message: Status message to display
            
        Returns:
            numpy.ndarray: Registration display frame
        """
        # Create blank display
        display = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        display.fill(20)  # Dark background
        
        # Layout: Camera feed on left, registration info on right
        camera_width = int(self.screen_width * 0.6)
        info_width = self.screen_width - camera_width
        
        # Resize and place camera frame
        if camera_frame is not None:
            camera_resized = cv2.resize(camera_frame, (camera_width, self.screen_height))
            display[:, :camera_width] = camera_resized
        
        # Draw dividing line
        cv2.line(display, (camera_width, 0), 
                (camera_width, self.screen_height), (100, 100, 100), 2)
        
        # Registration info
        info_x = camera_width + 20
        y_offset = 30
        
        # Title
        cv2.putText(display, "USER REGISTRATION", (info_x, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        y_offset += 50
        
        # User name input
        if user_name:
            cv2.putText(display, f"Name: {user_name}", (info_x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2)
        else:
            cv2.putText(display, "Enter name (type on keyboard):", (info_x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        y_offset += 50
        
        # Progress
        cv2.putText(display, "Face Samples:", (info_x, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        y_offset += 30
        
        # Progress bar
        bar_width = info_width - 40
        bar_height = 20
        progress = samples_collected / total_samples if total_samples > 0 else 0
        
        # Background
        cv2.rectangle(display, (info_x, y_offset), 
                     (info_x + bar_width, y_offset + bar_height), (50, 50, 50), -1)
        
        # Progress fill
        progress_width = int(bar_width * progress)
        cv2.rectangle(display, (info_x, y_offset), 
                     (info_x + progress_width, y_offset + bar_height), (0, 255, 0), -1)
        
        # Progress text
        progress_text = f"{samples_collected}/{total_samples}"
        cv2.putText(display, progress_text, (info_x, y_offset + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        y_offset += 70
        
        # Instructions
        cv2.putText(display, "Instructions:", (info_x, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        y_offset += 25
        instructions = [
            "1. Look at the camera",
            "2. Keep face centered",
            "3. Move slightly for samples",
            "4. Press SPACE to capture",
            "5. Press ENTER when done"
        ]
        
        for instruction in instructions:
            cv2.putText(display, instruction, (info_x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
            y_offset += 20
        
        # Status message
        if status_message:
            y_offset += 20
            cv2.putText(display, status_message, (info_x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        return display

