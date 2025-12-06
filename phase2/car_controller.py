"""
Car Control Interface for Raspberry Pi with DonkeyCar and VESC
Provides velocity control: set_velocity(linear, angular)
"""
import time
import os
import inspect


class CarController:
    """
    Car control interface for Raspberry Pi
    Supports VESC control via DonkeyCar or direct serial
    """
    def __init__(
        self,
        vesc_port=None,
        use_donkeycar=True,
        simulation_mode=False,
        steering_inverted=False,
        steering_offset=0.0,
        steering_scale=1.0,
        vesc_start_heartbeat=False,
        servo_center=0.5,
        servo_range=0.45,
        throttle_scale=0.8,
        vesc_duty_percent=0.5,
    ):
        """
        Initialize car controller
        
        Args:
            vesc_port: Serial port for VESC (e.g., '/dev/ttyACM0' or '/dev/ttyUSB0')
            use_donkeycar: If True, try to use DonkeyCar VESC interface
            simulation_mode: If True, only prints commands (for testing)
            steering_inverted: If True, flip steering direction (useful if servo wired backwards)
            steering_offset: Offset added to steering command (-1..1) to straighten wheels
            steering_scale: Scale steering command (0..1) to limit throw
            vesc_start_heartbeat: If True, let pyvesc send heartbeat thread (can throw if port is flaky)
            servo_center: Center pulse (0-1) for steering servo (0.5 is typical center)
            servo_range: Range from center for steering (-range..+range mapped into 0-1)
            throttle_scale: Multiplier on normalized throttle before sending to VESC
            vesc_duty_percent: Duty cycle cap passed into DonkeyCar VESC (default 0.4 = 40%)
        """
        self.vesc_port = vesc_port
        self.use_donkeycar = use_donkeycar
        self.simulation_mode = simulation_mode
        self.vesc = None
        self._vesc_run_args = 0  # Number of args the VESC.run method expects
        self._last_command_log = 0.0
        self._last_error_log = 0.0
        self._vesc_error_count = 0
        self.steering_inverted = steering_inverted
        self.steering_offset = steering_offset
        self.steering_scale = steering_scale
        self.vesc_start_heartbeat = vesc_start_heartbeat
        self.servo_center = servo_center
        self.servo_range = servo_range
        self.throttle_scale = throttle_scale
        self.vesc_duty_percent = vesc_duty_percent
        
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
                # Disable heartbeat by default; a flaky port can crash the heartbeat thread
                self.vesc = VESC(
                    serial_port=self.vesc_port,
                    start_heartbeat=self.vesc_start_heartbeat,
                    percent=self.vesc_duty_percent,
                )
                self._vesc_run_args = self._introspect_vesc_run(self.vesc)
                print(f"[CarController] VESC initialized via DonkeyCar on {self.vesc_port} (run args: {self._vesc_run_args})")
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

    def _introspect_vesc_run(self, vesc):
        """
        Determine how many positional args the VESC.run method accepts.
        This varies slightly across DonkeyCar versions.
        """
        try:
            sig = inspect.signature(vesc.run)
            return len(sig.parameters)
        except Exception as e:
            print(f"[CarController] WARNING: Could not inspect VESC.run signature: {e}")
            return 0
    
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

        # Convert to normalized throttle/steering for VESC (DonkeyCar expects -1..1)
        throttle = max(-1.0, min(1.0, linear / self.max_linear_speed))
        throttle = max(-1.0, min(1.0, throttle * self.throttle_scale))
        steering = max(-1.0, min(1.0, angular / self.max_angular_speed))

        # Apply steering calibration
        if self.steering_inverted:
            steering = -steering
        steering = steering * self.steering_scale + self.steering_offset
        steering = max(-1.0, min(1.0, steering))

        # Map normalized steering to servo pulse range (0..1)
        servo_cmd = self.servo_center + steering * self.servo_range
        servo_cmd = max(0.0, min(1.0, servo_cmd))
        
        if self.simulation_mode or self.vesc is None:
            # Print command for debugging when not actually driving hardware
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
            return

        # Convert linear/angular to left/right motor speeds (for logging only)
        left_speed = linear - angular * self.wheelbase / 2.0
        right_speed = linear + angular * self.wheelbase / 2.0

        try:
            # DonkeyCar's VESC API expects (angle, throttle)
            if self._vesc_run_args >= 2:
                self.vesc.run(servo_cmd, throttle)
            elif self._vesc_run_args == 1:
                # Some older donkeycar versions only take throttle; try to set steering separately
                self.vesc.run(throttle)
                if hasattr(self.vesc, "set_steering"):
                    self.vesc.set_steering(servo_cmd)
            else:
                # Fallback to common alt methods if signature introspection failed
                if hasattr(self.vesc, "set_throttle"):
                    self.vesc.set_throttle(throttle)
                if hasattr(self.vesc, "set_steering"):
                    self.vesc.set_steering(servo_cmd)

            now = time.time()
            if now - self._last_command_log > 1.0:
                print(f"[VESC] throttle={throttle:.2f}, steering(norm)={steering:.2f}, servo={servo_cmd:.2f} | left={left_speed:.2f} m/s, right={right_speed:.2f} m/s")
                self._last_command_log = now
        except Exception as e:
            print(f"[CarController] Error setting motor speeds: {e}")
            self._handle_vesc_error(e)
    
    def stop(self):
        """Stop the car immediately"""
        try:
            self.set_velocity(0.0, 0.0)
        except Exception as e:
            self._handle_vesc_error(e)
        if not self.simulation_mode:
            print("[CarController] Car stopped")

    def _handle_vesc_error(self, error):
        """Handle VESC communication errors with limited logging and optional reinit"""
        now = time.time()
        if now - self._last_error_log > 1.0:
            print(f"[CarController] Keeping current mode; please check VESC connection. ({error})")
            self._last_error_log = now
        self._vesc_error_count += 1

        # Try one re-init after an error burst
        if self._vesc_error_count == 1:
            try:
                print("[CarController] Attempting VESC reconnect...")
                self._init_vesc()
                # If re-init succeeds, clear error count
                if not self.simulation_mode and self.vesc is not None:
                    print("[CarController] VESC reconnected.")
                    self._vesc_error_count = 0
            except Exception as e:
                print(f"[CarController] VESC reconnect failed: {e}")

    
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
