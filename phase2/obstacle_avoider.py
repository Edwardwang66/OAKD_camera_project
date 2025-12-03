"""
Obstacle Avoidance Controller
Implements avoidance behavior when obstacles are detected
"""
import time


class ObstacleAvoider:
    """
    Controller for obstacle avoidance behavior
    """
    def __init__(self,
                 turn_duration=1.0,
                 turn_angular_speed=0.5,
                 scan_duration=0.5):
        """
        Initialize obstacle avoider
        
        Args:
            turn_duration: Duration to turn in one direction (seconds)
            turn_angular_speed: Angular speed for turning (rad/s)
            scan_duration: Duration to scan/check depth before deciding (seconds)
        """
        self.turn_duration = turn_duration
        self.turn_angular_speed = turn_angular_speed
        self.scan_duration = scan_duration
        
        # State tracking
        self.avoidance_start_time = None
        self.avoidance_phase = "STOP"  # STOP, SCAN, TURN
        self.avoidance_direction = None  # LEFT or RIGHT
    
    def start_avoidance(self):
        """Start obstacle avoidance sequence"""
        self.avoidance_start_time = time.time()
        self.avoidance_phase = "STOP"
        self.avoidance_direction = None
    
    def compute_control(self, obstacle_detector, depth_frame):
        """
        Compute control for obstacle avoidance
        
        Args:
            obstacle_detector: ObstacleDetector instance
            depth_frame: Current depth frame
        
        Returns:
            dict: {
                'linear': float,
                'angular': float,
                'direction': str,
                'phase': str
            }
        """
        if self.avoidance_start_time is None:
            self.start_avoidance()
        
        current_time = time.time()
        elapsed = current_time - self.avoidance_start_time
        
        # Phase 1: Stop briefly
        if self.avoidance_phase == "STOP":
            if elapsed < 0.3:  # Stop for 0.3 seconds
                return {
                    'linear': 0.0,
                    'angular': 0.0,
                    'direction': 'STOP',
                    'phase': 'STOP'
                }
            else:
                # Move to scan phase
                self.avoidance_phase = "SCAN"
                self.avoidance_start_time = current_time
                elapsed = 0.0
        
        # Phase 2: Scan to decide direction
        if self.avoidance_phase == "SCAN":
            if elapsed < self.scan_duration:
                # Stay stopped and scan
                return {
                    'linear': 0.0,
                    'angular': 0.0,
                    'direction': 'SCAN',
                    'phase': 'SCAN'
                }
            else:
                # Decide direction based on side depths
                self.avoidance_direction = obstacle_detector.choose_avoidance_direction(depth_frame)
                self.avoidance_phase = "TURN"
                self.avoidance_start_time = current_time
                elapsed = 0.0
        
        # Phase 3: Turn away from obstacle
        if self.avoidance_phase == "TURN":
            if elapsed < self.turn_duration:
                # Turn in chosen direction
                angular = self.turn_angular_speed
                if self.avoidance_direction == "RIGHT":
                    angular = -angular  # Right turn is negative angular
                
                return {
                    'linear': 0.0,
                    'angular': angular,
                    'direction': f'TURN {self.avoidance_direction}',
                    'phase': 'TURN'
                }
            else:
                # Turn complete - reset
                self.avoidance_phase = None
                self.avoidance_start_time = None
                return {
                    'linear': 0.0,
                    'angular': 0.0,
                    'direction': 'AVOIDANCE_COMPLETE',
                    'phase': 'COMPLETE'
                }
        
        # Default: stop
        return {
            'linear': 0.0,
            'angular': 0.0,
            'direction': 'STOP',
            'phase': 'UNKNOWN'
        }
    
    def is_avoiding(self):
        """Check if currently in avoidance mode"""
        return self.avoidance_start_time is not None
    
    def reset(self):
        """Reset avoidance state"""
        self.avoidance_start_time = None
        self.avoidance_phase = "STOP"
        self.avoidance_direction = None

