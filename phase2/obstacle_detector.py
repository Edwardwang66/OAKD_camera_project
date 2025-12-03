"""
Obstacle Detection Module for Phase 3
Uses depth map to detect obstacles in front of the car
"""
import numpy as np
import cv2


class ObstacleDetector:
    """
    Detects obstacles in front of the car using depth map
    """
    def __init__(self,
                 front_region_ratio=0.3,
                 depth_threshold=0.5,
                 min_depth_mm=100,
                 max_depth_mm=6000,
                 method='median'):
        """
        Initialize obstacle detector
        
        Args:
            front_region_ratio: Ratio of front region (width and height) to check
                               e.g., 0.3 means 30% of center area
            depth_threshold: Threshold in meters for obstacle detection (default: 0.5m)
            min_depth_mm: Minimum valid depth in mm (default: 100mm = 0.1m)
            max_depth_mm: Maximum valid depth in mm (default: 6000mm = 6m)
            method: 'median' or 'percentile_10' (use 10% minimum value)
        """
        self.front_region_ratio = front_region_ratio
        self.depth_threshold = depth_threshold  # in meters
        self.min_depth_mm = min_depth_mm
        self.max_depth_mm = max_depth_mm
        self.method = method
    
    def detect_obstacle(self, depth_frame):
        """
        Detect if there's an obstacle in front
        
        Args:
            depth_frame: Depth frame from camera (16-bit, in millimeters)
        
        Returns:
            dict: {
                'obstacle_ahead': bool,
                'front_depth': float (in meters, or None),
                'front_region': (x_min, y_min, x_max, y_max),
                'valid_depth_count': int
            }
        """
        if depth_frame is None:
            return {
                'obstacle_ahead': False,
                'front_depth': None,
                'front_region': None,
                'valid_depth_count': 0
            }
        
        h, w = depth_frame.shape[:2]
        
        # Define front region (center rectangle)
        region_w = int(w * self.front_region_ratio)
        region_h = int(h * self.front_region_ratio)
        
        x_min = (w - region_w) // 2
        x_max = x_min + region_w
        y_min = (h - region_h) // 2
        y_max = y_min + region_h
        
        # Extract front region
        front_region = depth_frame[y_min:y_max, x_min:x_max]
        
        # Filter out invalid depth values
        # Depth frame is in millimeters (16-bit)
        valid_mask = (front_region > self.min_depth_mm) & (front_region < self.max_depth_mm)
        valid_depths = front_region[valid_mask]
        
        valid_depth_count = len(valid_depths)
        
        if valid_depth_count == 0:
            # No valid depth data - assume no obstacle (or depth unavailable)
            return {
                'obstacle_ahead': False,
                'front_depth': None,
                'front_region': (x_min, y_min, x_max, y_max),
                'valid_depth_count': 0
            }
        
        # Calculate representative depth value
        if self.method == 'median':
            front_depth_mm = np.median(valid_depths)
        elif self.method == 'percentile_10':
            front_depth_mm = np.percentile(valid_depths, 10)  # 10% minimum
        else:
            front_depth_mm = np.median(valid_depths)  # Default to median
        
        # Convert to meters
        front_depth_m = front_depth_mm / 1000.0
        
        # Check if obstacle ahead
        obstacle_ahead = front_depth_m < self.depth_threshold
        
        return {
            'obstacle_ahead': obstacle_ahead,
            'front_depth': front_depth_m,
            'front_region': (x_min, y_min, x_max, y_max),
            'valid_depth_count': valid_depth_count
        }
    
    def get_side_depths(self, depth_frame):
        """
        Get depth information for left and right sides
        Used for obstacle avoidance decision
        
        Args:
            depth_frame: Depth frame from camera (16-bit, in millimeters)
        
        Returns:
            dict: {
                'left_depth': float (in meters, or None),
                'right_depth': float (in meters, or None),
                'left_valid_count': int,
                'right_valid_count': int
            }
        """
        if depth_frame is None:
            return {
                'left_depth': None,
                'right_depth': None,
                'left_valid_count': 0,
                'right_valid_count': 0
            }
        
        h, w = depth_frame.shape[:2]
        
        # Define side regions (left and right thirds, middle vertical section)
        region_w = w // 3
        region_h = h // 2  # Use middle section vertically
        
        # Left region
        left_x_min = 0
        left_x_max = region_w
        left_y_min = (h - region_h) // 2
        left_y_max = left_y_min + region_h
        
        # Right region
        right_x_min = w - region_w
        right_x_max = w
        right_y_min = (h - region_h) // 2
        right_y_max = right_y_min + region_h
        
        # Extract and process left region
        left_region = depth_frame[left_y_min:left_y_max, left_x_min:left_x_max]
        left_mask = (left_region > self.min_depth_mm) & (left_region < self.max_depth_mm)
        left_depths = left_region[left_mask]
        left_valid_count = len(left_depths)
        left_depth_m = np.median(left_depths) / 1000.0 if left_valid_count > 0 else None
        
        # Extract and process right region
        right_region = depth_frame[right_y_min:right_y_max, right_x_min:right_x_max]
        right_mask = (right_region > self.min_depth_mm) & (right_region < self.max_depth_mm)
        right_depths = right_region[right_mask]
        right_valid_count = len(right_depths)
        right_depth_m = np.median(right_depths) / 1000.0 if right_valid_count > 0 else None
        
        return {
            'left_depth': left_depth_m,
            'right_depth': right_depth_m,
            'left_valid_count': left_valid_count,
            'right_valid_count': right_valid_count
        }
    
    def choose_avoidance_direction(self, depth_frame):
        """
        Choose which direction to turn to avoid obstacle
        
        Args:
            depth_frame: Depth frame from camera
        
        Returns:
            str: 'LEFT', 'RIGHT', or 'UNKNOWN'
        """
        side_depths = self.get_side_depths(depth_frame)
        
        left_depth = side_depths['left_depth']
        right_depth = side_depths['right_depth']
        
        # If both sides are available, choose the one with more space
        if left_depth is not None and right_depth is not None:
            if left_depth > right_depth:
                return 'LEFT'
            else:
                return 'RIGHT'
        
        # If only one side has valid data, choose that side
        if left_depth is not None:
            return 'LEFT'
        if right_depth is not None:
            return 'RIGHT'
        
        # Default: turn left if uncertain
        return 'LEFT'
    
    def visualize_detection(self, frame, detection_result, side_depths=None):
        """
        Draw obstacle detection visualization on frame
        
        Args:
            frame: RGB/BGR frame to draw on
            detection_result: Result from detect_obstacle()
            side_depths: Optional result from get_side_depths()
        
        Returns:
            numpy.ndarray: Frame with visualization
        """
        display_frame = frame.copy()
        
        if detection_result['front_region'] is not None:
            x_min, y_min, x_max, y_max = detection_result['front_region']
            
            # Draw front region
            if detection_result['obstacle_ahead']:
                color = (0, 0, 255)  # Red for obstacle
            else:
                color = (0, 255, 0)  # Green for clear
            
            cv2.rectangle(display_frame, (x_min, y_min), (x_max, y_max), color, 2)
            
            # Draw depth text
            if detection_result['front_depth'] is not None:
                depth_text = f"Front: {detection_result['front_depth']:.2f}m"
                cv2.putText(display_frame, depth_text, (x_min, y_min - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw obstacle warning
            if detection_result['obstacle_ahead']:
                cv2.putText(display_frame, "OBSTACLE!", (x_min, y_max + 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Draw side depths if provided
        if side_depths is not None:
            h, w = frame.shape[:2]
            
            left_text = f"L: {side_depths['left_depth']:.2f}m" if side_depths['left_depth'] else "L: N/A"
            right_text = f"R: {side_depths['right_depth']:.2f}m" if side_depths['right_depth'] else "R: N/A"
            
            cv2.putText(display_frame, left_text, (10, h - 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(display_frame, right_text, (w - 150, h - 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return display_frame

