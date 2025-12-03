"""
Car Controller - Minimal Control Interface for DonkeyCar with VESC
Provides simple velocity and motor control interfaces
"""
import time
import os

# Try to import donkeycar parts
try:
    from donkeycar.parts.actuator import VESC
    DONKEYCAR_AVAILABLE = True
except ImportError:
    DONKEYCAR_AVAILABLE = False
    print("Warning: DonkeyCar not available. Using simulation mode.")


class CarController:
    """
    Minimal car control interface
    Supports both velocity control and direct motor control
    """
    def __init__(self, use_donkeycar=True, vesc_port=None):
        """
        Initialize car controller
        
        Args:
            use_donkeycar: If True, try to use DonkeyCar VESC interface
            vesc_port: Serial port for VESC (e.g., '/dev/ttyACM0')
        """
        self.vesc = None
        self.use_donkeycar = use_donkeycar
        self.vesc_port = vesc_port
        self.simulation_mode = False
        
        if use_donkeycar and DONKEYCAR_AVAILABLE:
            try:
                self._init_vesc()
            except Exception as e:
                print(f"Warning: Could not initialize VESC: {e}")
                print("Falling back to simulation mode")
                self.simulation_mode = True
        else:
            print("Running in simulation mode (no actual car control)")
            self.simulation_mode = True
        
        # Current state
        self.current_linear = 0.0
        self.current_angular = 0.0
        self.current_left_speed = 0.0
        self.current_right_speed = 0.0
        
        print(f"Car controller initialized ({'VESC' if not self.simulation_mode else 'Simulation'} mode)")
    
    def _init_vesc(self):
        """Initialize VESC controller"""
        if not DONKEYCAR_AVAILABLE:
            raise RuntimeError("DonkeyCar not available")
        
        # Try to find VESC port if not provided
        if self.vesc_port is None:
            # Common VESC ports
            possible_ports = [
                '/dev/ttyACM0',
                '/dev/ttyUSB0',
                '/dev/ttyACM1',
                '/dev/ttyUSB1',
            ]
            
            for port in possible_ports:
                if os.path.exists(port):
                    self.vesc_port = port
                    print(f"Found potential VESC port: {port}")
                    break
        
        if self.vesc_port is None:
            raise RuntimeError("VESC port not found. Please specify vesc_port.")
        
        # Initialize VESC
        # Note: VESC initialization may vary based on your setup
        # This is a basic example - adjust based on your VESC configuration
        try:
            self.vesc = VESC(serial_port=self.vesc_port)
            print(f"VESC initialized on {self.vesc_port}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize VESC: {e}")
    
    def set_velocity(self, linear, angular):
        """
        Set car velocity using linear and angular speeds
        
        Args:
            linear: Linear velocity in m/s (forward positive)
            angular: Angular velocity in rad/s (counterclockwise positive)
        """
        self.current_linear = linear
        self.current_angular = angular
        
        # Convert to left/right motor speeds
        # For differential drive: v = (v_left + v_right) / 2
        #                    w = (v_right - v_left) / wheelbase
        # Solving: v_left = v - w * wheelbase / 2
        #          v_right = v + w * wheelbase / 2
        
        # Typical wheelbase for DonkeyCar is around 0.2-0.3m
        wheelbase = 0.25  # Adjust based on your car
        
        left_speed = linear - angular * wheelbase / 2.0
        right_speed = linear + angular * wheelbase / 2.0
        
        if self.simulation_mode:
            print(f"[SIM] Velocity: linear={linear:.2f} m/s, angular={angular:.2f} rad/s")
            # Update motor speeds even in simulation mode for state tracking
            self.current_left_speed = left_speed
            self.current_right_speed = right_speed
            return
        
        self.set_motor(left_speed, right_speed)
    
    def set_motor(self, left_speed, right_speed):
        """
        Set left and right motor speeds directly
        
        Args:
            left_speed: Left motor speed (m/s or normalized -1 to 1)
            right_speed: Right motor speed (m/s or normalized -1 to 1)
        """
        self.current_left_speed = left_speed
        self.current_right_speed = right_speed
        
        if self.simulation_mode:
            print(f"[SIM] Motor: left={left_speed:.2f}, right={right_speed:.2f}")
            return
        
        # Send commands to VESC
        if self.vesc is None:
            print("Warning: VESC not initialized")
            return
        
        try:
            # VESC typically uses normalized values (-1 to 1) or duty cycle
            # Adjust based on your VESC configuration
            # This is a placeholder - you may need to adjust based on your setup
            
            # Example: If VESC expects normalized values
            left_normalized = max(-1.0, min(1.0, left_speed))
            right_normalized = max(-1.0, min(1.0, right_speed))
            
            # Send to VESC (adjust based on your VESC interface)
            # self.vesc.run(left_normalized, right_normalized)
            
            # For now, print the values
            print(f"[VESC] Motor: left={left_normalized:.2f}, right={right_normalized:.2f}")
            
        except Exception as e:
            print(f"Error setting motor speeds: {e}")
    
    def stop(self):
        """Stop the car immediately"""
        self.set_velocity(0.0, 0.0)
        print("[Car] Stopped")
    
    def get_state(self):
        """
        Get current car state
        
        Returns:
            dict: Current velocity and motor speeds
        """
        return {
            'linear': self.current_linear,
            'angular': self.current_angular,
            'left_speed': self.current_left_speed,
            'right_speed': self.current_right_speed,
            'simulation': self.simulation_mode
        }
    
    def release(self):
        """Release car controller resources"""
        self.stop()
        if self.vesc is not None:
            try:
                # Clean up VESC connection if needed
                pass
            except:
                pass
        print("Car controller released")


# Alternative: Direct VESC control (if not using DonkeyCar)
class SimpleVESCController:
    """
    Simple VESC controller without DonkeyCar dependency
    For direct serial communication with VESC
    """
    def __init__(self, port='/dev/ttyACM0', baudrate=115200):
        """
        Initialize simple VESC controller
        
        Args:
            port: Serial port for VESC
            baudrate: Serial baudrate
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        
        try:
            import serial
            self.serial = serial.Serial(port, baudrate, timeout=1)
            print(f"VESC connected on {port}")
        except ImportError:
            print("Warning: pyserial not available. Install with: pip install pyserial")
        except Exception as e:
            print(f"Warning: Could not connect to VESC: {e}")
            print("Running in simulation mode")
    
    def set_motor(self, left_speed, right_speed):
        """
        Set motor speeds
        
        Args:
            left_speed: Left motor speed (-1 to 1)
            right_speed: Right motor speed (-1 to 1)
        """
        if self.serial is None:
            print(f"[SIM] Motor: left={left_speed:.2f}, right={right_speed:.2f}")
            return
        
        # Send VESC commands (this is a placeholder - adjust based on VESC protocol)
        # VESC typically uses a specific protocol - you may need to use a VESC library
        try:
            # Placeholder for VESC command
            # You would need to implement proper VESC protocol here
            pass
        except Exception as e:
            print(f"Error sending VESC command: {e}")
    
    def stop(self):
        """Stop motors"""
        self.set_motor(0.0, 0.0)
    
    def release(self):
        """Release resources"""
        self.stop()
        if self.serial:
            self.serial.close()

