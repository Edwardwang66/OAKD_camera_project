"""
Person Follower Controller
Implements following and approaching logic based on person detection
"""
import numpy as np


class PersonFollower:
    """
    Controller for following and approaching a person
    Implements PID-like control based on person bounding box and distance
    """
    def __init__(self, 
                 target_distance=1.0,
                 max_linear_speed=0.5,
                 max_angular_speed=1.0,
                 k_angle=1.0,
                 k_linear=0.5,
                 angle_threshold=0.1,
                 distance_threshold=0.2):
        """
        Initialize person follower
        
        Args:
            target_distance: Target distance to person in meters
            max_linear_speed: Maximum linear speed in m/s
            max_angular_speed: Maximum angular speed in rad/s
            k_angle: Proportional gain for angular control
            k_linear: Proportional gain for linear control
            angle_threshold: Angle error threshold for "aligned" (rad)
            distance_threshold: Distance error threshold for "close enough" (m)
        """
        self.target_distance = target_distance
        self.max_linear_speed = max_linear_speed
        self.max_angular_speed = max_angular_speed
        self.k_angle = k_angle
        self.k_linear = k_linear
        self.angle_threshold = angle_threshold
        self.distance_threshold = distance_threshold
    
    def compute_control(self, person_bbox, image_width, distance_to_person):
        """
        Compute control commands based on person detection
        
        Args:
            person_bbox: Person bounding box (x_min, y_min, x_max, y_max) or None
            image_width: Width of the image in pixels
            distance_to_person: Distance to person in meters, or None if not detected
            
        Returns:
            dict: Control commands with keys:
                - 'linear': Linear velocity (m/s)
                - 'angular': Angular velocity (rad/s)
                - 'aligned': bool, whether person is centered
                - 'close_enough': bool, whether close enough to target distance
        """
        if person_bbox is None or distance_to_person is None:
            return {
                'linear': 0.0,
                'angular': 0.0,
                'aligned': False,
                'close_enough': False
            }
        
        x_min, y_min, x_max, y_max = person_bbox
        
        # Calculate person center in image
        person_center_x = (x_min + x_max) / 2.0
        image_center_x = image_width / 2.0
        
        # Calculate error (positive = person is to the right, need to turn right)
        error_x = person_center_x - image_center_x
        normalized_error = error_x / (image_width / 2.0)  # Normalize to [-1, 1]
        
        # Angular control: turn towards person
        angular = self.k_angle * normalized_error
        angular = np.clip(angular, -self.max_angular_speed, self.max_angular_speed)
        
        # Check if aligned (person is roughly centered)
        abs_normalized_error = abs(normalized_error)
        aligned = abs_normalized_error < (self.angle_threshold / self.max_angular_speed * 2.0)
        
        # Distance control: move towards/away from person
        distance_error = distance_to_person - self.target_distance
        
        # Only move forward if roughly aligned
        if aligned:
            linear = self.k_linear * distance_error
            linear = np.clip(linear, -self.max_linear_speed, self.max_linear_speed)
            
            # Don't move backwards (only approach, don't retreat)
            if linear < 0:
                linear = 0.0
        else:
            # Not aligned - only rotate, don't move forward
            linear = 0.0
        
        # Check if close enough
        close_enough = abs(distance_error) < self.distance_threshold
        
        return {
            'linear': linear,
            'angular': angular,
            'aligned': aligned,
            'close_enough': close_enough,
            'distance_error': distance_error,
            'angle_error': normalized_error
        }
    
    def is_ready_for_interaction(self, person_bbox, image_width, distance_to_person):
        """
        Check if car is ready for interaction (aligned and at target distance)
        
        Args:
            person_bbox: Person bounding box or None
            image_width: Width of the image
            distance_to_person: Distance to person in meters or None
            
        Returns:
            bool: True if ready for interaction
        """
        if person_bbox is None or distance_to_person is None:
            return False
        
        control = self.compute_control(person_bbox, image_width, distance_to_person)
        return control['aligned'] and control['close_enough']


class SearchController:
    """
    Controller for searching behavior when no person is detected
    """
    def __init__(self, search_angular_speed=0.3):
        """
        Initialize search controller
        
        Args:
            search_angular_speed: Angular speed for searching rotation (rad/s)
        """
        self.search_angular_speed = search_angular_speed
    
    def compute_control(self):
        """
        Compute control for search behavior (slow rotation in place)
        
        Returns:
            dict: Control commands with 'linear' and 'angular'
        """
        return {
            'linear': 0.0,  # No forward movement
            'angular': self.search_angular_speed  # Rotate slowly
        }

