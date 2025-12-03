# Phase 2: Car Following and Approaching

Phase 2 implements autonomous car control to search for a person, approach them, and stop at a target distance.

## Features

### 1. Minimal Car Control Interface
- **Velocity Control**: `set_velocity(linear, angular)` - Control car with linear and angular speeds
- **Motor Control**: `set_motor(left_speed, right_speed)` - Direct motor control
- **VESC Support**: Integration with DonkeyCar VESC controller
- **Simulation Mode**: Test without actual car hardware

### 2. Person Following Control
- **Angular Control**: Turns towards person based on bounding box center
- **Distance Control**: Approaches person to target distance
- **Alignment Check**: Verifies person is centered before moving forward
- **Proximity Check**: Stops when close enough and aligned

### 3. Search Behavior
- **SEARCH State**: Rotates slowly in place when no person detected
- **APPROACH State**: Moves towards person when detected
- **INTERACT State**: Stops at target distance and waits
- **STOP State**: Emergency stop

## File Structure

```
car_controller.py      # Minimal car control interface (VESC/DonkeyCar)
person_follower.py     # Following and approaching control logic
phase2_demo.py         # Main demo program with state machine
```

## Installation

### 1. Install Dependencies

```bash
cd phase2
pip install -r requirements.txt
```

### 2. DonkeyCar Setup (for actual car control)

If you want to control a real car, you need DonkeyCar installed:

```bash
# Follow DonkeyCar installation guide
# https://docs.donkeycar.com/

# Or install with pip (if available)
pip install donkeycar
```

### 3. VESC Configuration

1. **Update VESC Firmware**: Follow VESC setup guide
2. **Calibrate VESC**: Use VESC Tool to calibrate
3. **Find Serial Port**: Usually `/dev/ttyACM0` or `/dev/ttyUSB0`
4. **Set Permissions**: 
   ```bash
   sudo chmod 666 /dev/ttyACM0
   # Or add user to dialout group
   sudo usermod -a -G dialout $USER
   ```

## Usage

### Basic Run (Simulation Mode)

```bash
cd phase2
python phase2_demo.py
```

This will run in simulation mode (no actual car control).

### With Real Car

```bash
# Specify VESC port if needed
python phase2_demo.py --vesc-port /dev/ttyACM0

# Adjust target distance
python phase2_demo.py --target-distance 1.5
```

### Command Line Arguments

- `--target-distance`: Target distance to person in meters (default: 1.0)
- `--vesc-port`: VESC serial port (e.g., /dev/ttyACM0)

## State Machine

The car operates in a state machine with 4 states:

1. **SEARCH**: 
   - Rotates slowly in place (angular speed: 0.3 rad/s)
   - Switches to APPROACH when person detected

2. **APPROACH**:
   - Turns towards person (angular control)
   - Moves forward when aligned (linear control)
   - Switches to INTERACT when close enough and aligned
   - Switches to SEARCH if person lost

3. **INTERACT**:
   - Stops and waits
   - Switches to APPROACH if person moves away
   - Switches to SEARCH if person lost

4. **STOP**:
   - Emergency stop
   - Car stops immediately

## Control Logic

### Angular Control

```
error_x = person_center_x - image_center_x
normalized_error = error_x / (image_width / 2)
angular = k_angle * normalized_error
```

### Distance Control

```
distance_error = distance_to_person - TARGET_DISTANCE
linear = k_linear * distance_error  (only if aligned)
```

### Ready for Interaction

Car is ready when:
- `abs(distance_error) < 0.2m`
- `abs(angle_error) < threshold`

## Controls

### Keyboard (OpenCV Window)
- `'q'` - Quit
- `'s'` - Emergency stop

### Terminal Commands
- `'q'` or `'quit'` - Quit
- `'s'` or `'stop'` - Emergency stop
- `'r'` or `'reset'` - Reset to SEARCH state

## Configuration

You can adjust control parameters in `person_follower.py`:

```python
follower = PersonFollower(
    target_distance=1.0,      # Target distance (m)
    max_linear_speed=0.5,     # Max forward speed (m/s)
    max_angular_speed=1.0,    # Max rotation speed (rad/s)
    k_angle=1.0,              # Angular control gain
    k_linear=0.5,             # Linear control gain
    angle_threshold=0.1,       # Alignment threshold (rad)
    distance_threshold=0.2    # Distance threshold (m)
)
```

## Troubleshooting

### Car Not Moving

1. **Check VESC Connection**:
   ```bash
   ls -l /dev/ttyACM*
   ```

2. **Check Permissions**:
   ```bash
   sudo chmod 666 /dev/ttyACM0
   ```

3. **Test VESC**: Use VESC Tool to verify connection

4. **Check DonkeyCar**: Verify DonkeyCar is installed and configured

### Person Not Detected

- Ensure good lighting
- Check camera angle
- Verify MediaPipe is working

### Car Moves Erratically

- Adjust control gains (`k_angle`, `k_linear`)
- Reduce max speeds
- Check camera frame rate

## Safety

⚠️ **IMPORTANT**: 
- Always test in simulation mode first
- Have emergency stop ready
- Test in safe, open area
- Start with low speeds
- Monitor car behavior closely

## Next Steps (Phase 3+)

- Obstacle avoidance
- Multiple person tracking
- Path planning
- Advanced control algorithms (PID, MPC)

