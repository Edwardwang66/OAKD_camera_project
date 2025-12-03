"""
Car Control Interface for Raspberry Pi with DonkeyCar and VESC
Provides velocity control: set_velocity(linear, angular)
"""
import time
import os


class CarController:
    """
    Car control interface for Raspberry Pi
    Supports VESC control via DonkeyCar or direct serial
    """
    def __init__(self, vesc_port=None, use_donkeycar=True, simulation_mode=False):
        """
        Initialize car controller
        
        Args:
            vesc_port: Serial port for VESC (e.g., '/dev/ttyACM0' or '/dev/ttyUSB0')
            use_donkeycar: If True, try to use DonkeyCar VESC interface
            simulation_mode: If True, only prints commands (for testing)
        """
        self.vesc_port = vesc_port
        self.use_donkeycar = use_donkeycar
        self.simulation_mode = simulation_mode
        self.vesc = None
        
        # Current state
        self.current_linear = 0.0  # m/s
        self.current_angular = 0.0  # rad/s
        
        # Car parameters (adjust based on your DonkeyCar setup)
        self.wheelbase = 0.25  # meters (typical DonkeyCar wheelbase)
        self.max_linear_speed = 1.0  # m/s
        self.max_angular_speed = 2.0  # rad/s
        
        if simulation_mode:
            print("[CarController] Running in SIMULATION mode (commands will be printed)")
        else:
            print(f"[CarController] Initializing VESC on {vesc_port or 'auto-detect'}...")
            self._init_vesc()
    
    def _init_vesc(self):
        """Initialize VESC controller"""
        if self.simulation_mode:
            return
        
        # Try to find VESC port if not provided
        if self.vesc_port is None:
            possible_ports = [
                '/dev/ttyACM0',
                '/dev/ttyUSB0',
                '/dev/ttyACM1',
                '/dev/ttyUSB1',
            ]
            
            for port in possible_ports:
                if os.path.exists(port):
                    self.vesc_port = port
                    print(f"[CarController] Found potential VESC port: {port}")
                    break
        
        if self.vesc_port is None:
            print("[CarController] WARNING: VESC port not found. Running in simulation mode.")
            self.simulation_mode = True
            return
        
        # Try to initialize VESC
        if self.use_donkeycar:
            try:
                from donkeycar.parts.actuator import VESC
                self.vesc = VESC(serial_port=self.vesc_port)
                print(f"[CarController] VESC initialized via DonkeyCar on {self.vesc_port}")
                self.simulation_mode = False
            except ImportError:
                print("[CarController] WARNING: DonkeyCar not available. Install with: pip install donkeycar")
                print("[CarController] Falling back to simulation mode")
                self.simulation_mode = True
            except Exception as e:
                print(f"[CarController] WARNING: Could not initialize VESC: {e}")
                print("[CarController] Falling back to simulation mode")
                self.simulation_mode = True
        else:
            # Direct serial communication (not implemented yet)
            print("[CarController] Direct serial VESC control not yet implemented")
            print("[CarController] Falling back to simulation mode")
            self.simulation_mode = True
    
    def set_velocity(self, linear, angular):
        """
        Set car velocity using linear and angular speeds
        
        Args:
            linear: Linear velocity in m/s (forward positive, backward negative)
            angular: Angular velocity in rad/s (counterclockwise positive, clockwise negative)
        """
        # Clamp to max speeds
        linear = max(-self.max_linear_speed, min(self.max_linear_speed, linear))
        angular = max(-self.max_angular_speed, min(self.max_angular_speed, angular))
        
        self.current_linear = linear
        self.current_angular = angular
        
        if self.simulation_mode:
            # Print command
            direction = "STRAIGHT"
            if angular > 0.1:
                direction = "LEFT TURN"
            elif angular < -0.1:
                direction = "RIGHT TURN"
            elif linear > 0.1:
                direction = "FORWARD"
            elif linear < -0.1:
                direction = "BACKWARD"
            else:
                direction = "STOP"
            
            print(f"[SIM] Car Command: {direction} | Linear: {linear:.2f} m/s, Angular: {angular:.2f} rad/s")
        else:
            # Convert linear/angular to left/right motor speeds
            # For differential drive: v = (v_left + v_right) / 2
            #                    w = (v_right - v_left) / wheelbase
            # Solving: v_left = v - w * wheelbase / 2
            #          v_right = v + w * wheelbase / 2
            
            left_speed = linear - angular * self.wheelbase / 2.0
            right_speed = linear + angular * self.wheelbase / 2.0
            
            # Send to VESC
            if self.vesc is not None:
                try:
                    # VESC typically uses normalized values (-1 to 1)
                    # Adjust based on your VESC configuration
                    left_normalized = max(-1.0, min(1.0, left_speed / self.max_linear_speed))
                    right_normalized = max(-1.0, min(1.0, right_speed / self.max_linear_speed))
                    
                    # Send to VESC (adjust based on your VESC interface)
                    # self.vesc.run(left_normalized, right_normalized)
                    # For now, print the values until VESC interface is confirmed
                    print(f"[VESC] Motor: left={left_normalized:.2f}, right={right_normalized:.2f}")
                except Exception as e:
                    print(f"[CarController] Error setting motor speeds: {e}")
    
    def stop(self):
        """Stop the car immediately"""
        self.set_velocity(0.0, 0.0)
        if not self.simulation_mode:
            print("[CarController] Car stopped")
    
    def get_state(self):
        """
        Get current car state
        
        Returns:
            dict: Current velocity
        """
        return {
            'linear': self.current_linear,
            'angular': self.current_angular,
            'simulation': self.simulation_mode
        }
    
    def release(self):
        """Release car controller resources"""
        self.stop()
        if self.vesc is not None:
            # Clean up VESC connection if needed
            try:
                # VESC cleanup code here
                pass
            except:
                pass
        print("[CarController] Released")
