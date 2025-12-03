"""
Person Follower Controller
Implements following and approaching logic based on person detection
Based on person bounding box position to determine left/right/straight commands
"""
import numpy as np


class PersonFollower:
    """
    Controller for following and approaching a person
    Computes left/right/straight commands based on person position
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
            angle_threshold: Angle error threshold for "aligned" (normalized, 0-1)
            distance_threshold: Distance error threshold for "close enough" (m)
        """
        self.target_distance = target_distance
        self.max_linear_speed = max_linear_speed
        self.max_angular_speed = max_angular_speed
        self.k_angle = k_angle
        self.k_linear = k_linear
        self.angle_threshold = angle_threshold
        self.distance_threshold = distance_threshold
    
    def compute_control(self, person_bbox, image_width, distance_to_person=None):
        """
        Compute control commands based on person detection
        
        Args:
            person_bbox: Person bounding box (x_min, y_min, x_max, y_max) or None
            image_width: Width of the image in pixels
            distance_to_person: Distance to person in meters, or None if not available
            
        Returns:
            dict: Control commands with keys:
                - 'linear': Linear velocity (m/s)
                - 'angular': Angular velocity (rad/s)
                - 'direction': 'LEFT', 'RIGHT', 'STRAIGHT', or 'STOP'
                - 'aligned': bool, whether person is centered
                - 'close_enough': bool, whether close enough to target distance
        """
        if person_bbox is None:
            return {
                'linear': 0.0,
                'angular': 0.0,
                'direction': 'STOP',
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
        angular = self.k_angle * normalized_error * self.max_angular_speed
        angular = np.clip(angular, -self.max_angular_speed, self.max_angular_speed)
        
        # Determine direction
        if abs(normalized_error) < self.angle_threshold:
            direction = 'STRAIGHT'
            aligned = True
        elif normalized_error > 0:
            direction = 'RIGHT TURN'
            aligned = False
        else:
            direction = 'LEFT TURN'
            aligned = False
        
        # Distance control: move towards/away from person
        # For Part 1, we don't have depth, so we'll use a simple heuristic
        # based on bounding box size (larger box = closer person)
        if distance_to_person is not None:
            distance_error = distance_to_person - self.target_distance
            close_enough = abs(distance_error) < self.distance_threshold
            
            # Only move forward if roughly aligned
            if aligned and not close_enough:
                linear = self.k_linear * distance_error
                linear = np.clip(linear, 0, self.max_linear_speed)  # Don't move backwards
            else:
                linear = 0.0
        else:
            # No depth info - use bounding box size as heuristic
            bbox_width = x_max - x_min
            bbox_height = y_max - y_min
            bbox_area = bbox_width * bbox_height
            image_area = image_width * (y_max - y_min)  # Approximate
            
            # If person takes up significant portion of image, assume close enough
            area_ratio = bbox_area / (image_width * image_width)  # Normalize
            
            close_enough = area_ratio > 0.15  # Threshold (adjust based on testing)
            
            # Move forward if aligned and not close enough
            if aligned and not close_enough:
                linear = self.max_linear_speed * 0.5  # Moderate speed
            else:
                linear = 0.0
        
        # If close enough and aligned, stop
        if aligned and close_enough:
            direction = 'STOP'
            linear = 0.0
            angular = 0.0
        
        return {
            'linear': linear,
            'angular': angular,
            'direction': direction,
            'aligned': aligned,
            'close_enough': close_enough,
            'error_x': normalized_error
        }
    
    def is_ready_for_interaction(self, person_bbox, image_width, distance_to_person=None):
        """
        Check if car is ready for interaction (aligned and at target distance)
        
        Args:
            person_bbox: Person bounding box or None
            image_width: Width of the image
            distance_to_person: Distance to person in meters or None
            
        Returns:
            bool: True if ready for interaction
        """
        if person_bbox is None:
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
            dict: Control commands with 'linear', 'angular', and 'direction'
        """
        return {
            'linear': 0.0,  # No forward movement
            'angular': self.search_angular_speed,  # Rotate slowly
            'direction': 'SEARCH (ROTATE)'
        }

