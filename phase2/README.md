# Phase 2: Person Following and Approaching

Phase 2 implements autonomous car control to search for a person, approach them, and stop at a target distance.

**Designed for Raspberry Pi 5 with OAKD Lite camera and DonkeyCar/VESC**

## Overview

The car operates autonomously with three main states:
- **SEARCH**: Rotates slowly to find a person
- **APPROACH**: Moves towards person (LEFT/RIGHT/STRAIGHT based on person position)
- **INTERACT**: Stops in front of person at target distance

## Hardware Requirements

- **Raspberry Pi 5** (or Raspberry Pi 4)
- **OAKD Lite Camera** (connected via USB)
- **DonkeyCar** with VESC motor controller
- **Mac** (for X11 forwarding display via XQuartz)

## Setup

### 1. Raspberry Pi Setup

#### Install Dependencies

```bash
cd phase2
pip install -r requirements.txt
```

#### OAKD Camera Setup

1. **Connect OAKD Lite Camera**: Plug in via USB
2. **Set Permissions**:
   ```bash
   sudo usermod -a -G dialout $USER
   # Log out and log back in for changes to take effect
   ```
3. **Verify Connection**:
   ```bash
   python test_oakd_simple.py
   ```

#### VESC Setup (for actual car control)

1. **Install DonkeyCar** (follow official guide):
   ```bash
   # Follow: https://docs.donkeycar.com/
   ```

2. **Find VESC Port**:
   ```bash
   ls -l /dev/ttyACM* /dev/ttyUSB*
   ```

3. **Set Permissions**:
   ```bash
   sudo chmod 666 /dev/ttyACM0  # Replace with your port
   # Or add user to dialout group (already done above)
   ```

### 2. Mac Setup (for X11 Display)

#### Install XQuartz

```bash
brew install --cask xquartz
```

#### Configure XQuartz

1. Open XQuartz (Applications > Utilities > XQuartz)
2. Go to **XQuartz > Preferences > Security**
3. Check **"Allow connections from network clients"**
4. **Restart XQuartz** (important!)

### 3. Connect via SSH with X11 Forwarding

```bash
# From Mac, connect to Raspberry Pi
ssh -Y pi@raspberrypi.local

# Or with IP address
ssh -Y pi@192.168.1.XXX

# Verify X11 forwarding
echo $DISPLAY
# Should show: localhost:10.0 or similar
```

## Usage

### Basic Run (Simulation Mode)

Test without actual car control:

```bash
cd phase2
python phase2_demo.py --simulation
```

This will:
- Initialize OAKD camera with person detection
- Run in simulation mode (prints car commands)
- Display video via X11 forwarding on your Mac
- Show LEFT/RIGHT/STRAIGHT/STOP commands based on person position

### With Real Car Control

```bash
# Auto-detect VESC port
python phase2_demo.py

# Specify VESC port
python phase2_demo.py --vesc-port /dev/ttyACM0

# Adjust target distance
python phase2_demo.py --target-distance 1.5
```

### Command Line Arguments

- `--target-distance`: Target distance to person in meters (default: 1.0)
- `--vesc-port`: VESC serial port (e.g., /dev/ttyACM0), None for auto-detect
- `--simulation`: Run in simulation mode (no actual car control)

## State Machine

The car operates in a state machine with 4 states:

1. **SEARCH**: 
   - Rotates slowly in place (angular speed: 0.3 rad/s)
   - Switches to APPROACH when person detected

2. **APPROACH**:
   - Turns towards person (angular control based on person position)
   - Moves forward when aligned (linear control)
   - Outputs: LEFT TURN, RIGHT TURN, or STRAIGHT
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
angular = k_angle * normalized_error * max_angular_speed
```

- If `normalized_error > threshold` → RIGHT TURN
- If `normalized_error < -threshold` → LEFT TURN
- If `abs(normalized_error) < threshold` → STRAIGHT

### Distance Control

Currently uses bounding box size as heuristic (larger box = closer person).
For Part 2 with depth, will use:

```
distance_error = distance_to_person - TARGET_DISTANCE
linear = k_linear * distance_error  (only if aligned)
```

### Ready for Interaction

Car is ready when:
- Person bounding box is large enough (close enough)
- `abs(error_x) < threshold` (aligned)

## Controls

- `'q'` - Quit and stop car
- `'s'` - Emergency stop
- `'r'` - Reset to SEARCH state

## File Structure

```
phase2/
├── car_controller.py      # Car control interface (VESC/DonkeyCar)
├── oakd_camera.py         # OAKD camera with person detection
├── person_follower.py     # Following and approaching control logic
├── phase2_demo.py         # Main demo program with state machine
├── test_oakd_simple.py    # Simple OAKD camera test
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Configuration

You can adjust control parameters in `person_follower.py`:

```python
follower = PersonFollower(
    target_distance=1.0,      # Target distance (m)
    max_linear_speed=0.5,     # Max forward speed (m/s)
    max_angular_speed=1.0,    # Max rotation speed (rad/s)
    k_angle=1.0,              # Angular control gain
    k_linear=0.5,             # Linear control gain
    angle_threshold=0.1,       # Alignment threshold (normalized)
    distance_threshold=0.2    # Distance threshold (m)
)
```

## Troubleshooting

### OAKD Camera Not Detected

1. **Check USB Connection**: Ensure OAKD Lite is connected via USB
2. **Check Permissions**: 
   ```bash
   ls -l /dev/ttyACM*
   sudo usermod -a -G dialout $USER
   # Log out and log back in
   ```
3. **Test Camera**:
   ```bash
   python test_oakd_simple.py
   ```

### X11 Display Not Working

1. **Check XQuartz is Running**: On Mac, make sure XQuartz is open
2. **Check DISPLAY Variable**:
   ```bash
   echo $DISPLAY
   # Should show: localhost:10.0 or similar
   ```
3. **Reconnect with X11 Forwarding**:
   ```bash
   ssh -Y pi@raspberrypi.local
   ```

### VESC Not Connecting

1. **Check VESC Port**:
   ```bash
   ls -l /dev/ttyACM* /dev/ttyUSB*
   ```

2. **Check Permissions**:
   ```bash
   sudo chmod 666 /dev/ttyACM0  # Replace with your port
   ```

3. **Test DonkeyCar**:
   ```bash
   # Verify DonkeyCar is installed
   python -c "import donkeycar; print('OK')"
   ```

4. **Run in Simulation Mode First**:
   ```bash
   python phase2_demo.py --simulation
   ```

### Person Not Detected

- Ensure good lighting
- Check camera angle
- Verify blobconverter is installed: `pip install blobconverter`
- Person detection uses MobileNet-SSD (class 15 in COCO dataset)

## Safety

⚠️ **IMPORTANT**: 
- Always test in simulation mode first: `--simulation`
- Have emergency stop ready (press 's' key)
- Test in safe, open area
- Start with low speeds
- Monitor car behavior closely
- Make sure car can be stopped manually

## Next Steps

- [ ] Add depth-based distance control (OAKD depth support)
- [ ] Obstacle avoidance
- [ ] Multiple person tracking
- [ ] Advanced control algorithms (PID, MPC)
- [ ] Logging and data collection

## X11 Forwarding Performance

If X11 forwarding is slow:
- Use wired network instead of WiFi
- Reduce camera resolution in code
- Consider using VNC instead for better performance

## Notes

- The demo is designed to work with or without X11 forwarding
- If DISPLAY is not set, processing continues but no windows appear
- All control logic works regardless of display availability
- Terminal output shows status every 2 seconds
