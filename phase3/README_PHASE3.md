# Phase 3: Person Following with Obstacle Avoidance

Phase 3 adds depth map-based obstacle avoidance functionality on top of Phase 2, avoiding collisions with obstacles while searching for and approaching people.

**Designed for: Raspberry Pi 5 + OAKD Lite Camera + DonkeyCar/VESC**

## Feature Overview

Phase 3 implements the following features:
- ✅ Person tracking and approach based on Phase 2
- ✅ Front obstacle detection using depth maps
- ✅ Automatic obstacle avoidance mode when obstacles are detected
- ✅ Intelligent direction selection for bypassing (left or right turn)

## State Machine

Phase 3's state machine adds the `AVOID_OBSTACLE` state on top of Phase 2:

1. **SEARCH**: 
   - Slowly rotate to find person
   - Detect front obstacles
   - Switch to `AVOID_OBSTACLE` when obstacle detected

2. **APPROACH**:
   - Move towards person (turn left/right/straight based on position)
   - **Detect front obstacles before advancing**
   - Switch to `AVOID_OBSTACLE` when obstacle detected
   - Switch to `INTERACT` when person is ready

3. **AVOID_OBSTACLE** (New):
   - Stop advancing
   - Scan depth information on left and right sides
   - Choose side with greater depth to turn
   - Turn for a period then return to original state (SEARCH or APPROACH)

4. **INTERACT**:
   - Stop at target distance
   - Maintain interaction with person

5. **STOP**:
   - Emergency stop

## Obstacle Avoidance Principle

### Depth Detection Region

- **Front detection region**: Middle 30% rectangular area of the frame (configurable)
- **Depth value processing**: 
  - Filter out 0 values and invalid values (< 100mm or > 6000mm)
  - Use median or 10th percentile minimum as representative depth

### Obstacle Judgment

```
if front_depth < depth_threshold (default 0.5m):
    obstacle_ahead = True
else:
    obstacle_ahead = False
```

### Obstacle Avoidance Strategy

When obstacle is detected:
1. **Stop**: Stop for 0.3 seconds first
2. **Scan**: Stop for 0.5 seconds, scan left and right depth
3. **Turn**: Choose direction based on left/right depth, turn for 1 second
4. **Resume**: Return to original state to continue task

## Hardware Requirements

- **Raspberry Pi 5** (or Raspberry Pi 4)
- **OAKD Lite Camera** (needs stereo depth support, connected via USB)
- **DonkeyCar** with VESC motor controller
- **Mac** (for X11 forwarding display via XQuartz)

## Installation

### 1. Install Dependencies

```bash
cd phase3
pip install -r requirements.txt
```

### 2. OAKD Camera Depth Support

OAKD Lite uses stereo vision to obtain depth maps. Ensure the camera is properly connected, Phase 3 will automatically detect depth support.

**Verify depth support**:
```bash
python -c "from phase2.oakd_camera import OAKDCamera; cam = OAKDCamera(); print('Depth:', cam.has_depth)"
```

## Usage

### Basic Run (Simulation Mode)

Test obstacle avoidance functionality without controlling actual vehicle:

```bash
cd phase3
python phase3_demo.py --simulation
```

### Adjust Obstacle Avoidance Threshold

```bash
# Set obstacle detection threshold to 0.3 meters
python phase3_demo.py --simulation --depth-threshold 0.3

# Set obstacle detection threshold to 0.8 meters
python phase3_demo.py --simulation --depth-threshold 0.8
```

### Actual Vehicle Control

```bash
# Auto-detect VESC port
python phase3_demo.py

# Specify VESC port
python phase3_demo.py --vesc-port /dev/ttyACM0

# Adjust target distance
python phase3_demo.py --target-distance 1.5 --depth-threshold 0.5
```

### Command Line Arguments

- `--target-distance`: Target distance (meters, default: 1.0)
- `--vesc-port`: VESC serial port (e.g., /dev/ttyACM0), None means auto-detect
- `--simulation`: Simulation mode (does not actually control vehicle)
- `--depth-threshold`: Obstacle detection threshold (meters, default: 0.5)

## File Structure

```
phase3/
├── phase3_demo.py          # Phase 3 demo (with obstacle avoidance)
├── obstacle_detector.py    # Obstacle detection module (new)
├── obstacle_avoider.py     # Obstacle avoidance control module (new)
└── README_PHASE3.md        # This document

phase2/
├── oakd_camera.py          # OAKD camera interface (depth support added)
├── car_controller.py       # Vehicle control interface
├── person_follower.py      # Person tracking control logic
└── phase2_demo.py          # Phase 2 demo (original version)
```

## Configuration Parameters

### Obstacle Detector (`ObstacleDetector`)

Initialized in `phase3_demo.py`:

```python
self.obstacle_detector = ObstacleDetector(
    front_region_ratio=0.3,      # Front detection region ratio (30%)
    depth_threshold=0.5,          # Obstacle threshold (meters)
    min_depth_mm=100,            # Minimum valid depth (millimeters)
    max_depth_mm=6000,           # Maximum valid depth (millimeters)
    method='median'              # 'median' or 'percentile_10'
)
```

### Obstacle Avoider (`ObstacleAvoider`)

Initialized in `phase3_demo.py`:

```python
self.obstacle_avoider = ObstacleAvoider(
    turn_duration=1.0,          # Turn duration (seconds)
    turn_angular_speed=0.5,      # Turn angular speed (rad/s)
    scan_duration=0.5            # Scan duration (seconds)
)
```

## How It Works

### Depth Map Acquisition

OAKD Lite uses stereo vision:
- Left and right monocular cameras (MonoCamera)
- Stereo depth node (StereoDepth) calculates depth map
- Depth values in millimeters (16-bit)

### Obstacle Detection Process

1. **Get depth map**: Get current depth frame from camera
2. **Extract front region**: Extract middle 30% region of frame
3. **Filter invalid values**: Remove 0 values and out-of-range values
4. **Calculate representative depth**: Use median or 10th percentile minimum
5. **Judge obstacle**: Compare representative depth with threshold

### Obstacle Avoidance Decision Process

```
Detect obstacle
    ↓
Enter AVOID_OBSTACLE state
    ↓
Stop for 0.3 seconds
    ↓
Scan left/right depth for 0.5 seconds
    ↓
Choose side with greater depth
    ↓
Turn for 1 second
    ↓
Return to original state (SEARCH or APPROACH)
```

## Troubleshooting

### Depth Map Unavailable

If it shows "Depth: DISABLED":

1. **Check camera model**: Confirm it's OAKD Lite (supports stereo depth)
2. **Check connection**: Ensure camera is properly connected
3. **Check logs**: Look at error messages during initialization

```
[OAKDCamera] Warning: Could not initialize depth cameras: ...
[OAKDCamera] Depth support disabled (camera may not have stereo)
```

### Obstacle Detection Inaccurate

- **Adjust threshold**: Try different `--depth-threshold` values
- **Adjust detection region**: Modify `front_region_ratio` parameter
- **Check lighting**: Ensure adequate lighting (stereo vision needs good lighting)
- **Check depth range**: Adjust `min_depth_mm` and `max_depth_mm`

### Obstacle Avoidance Behavior Abnormal

- **Adjust turn speed**: Modify `turn_angular_speed`
- **Adjust turn time**: Modify `turn_duration`
- **Check depth quality**: View depth map visualization

## Safety Notes

⚠️ **Important**:
- Always test in simulation mode first: `--simulation`
- Prepare emergency stop (press 's' key)
- Test in safe, open area
- Start testing at low speed
- Closely monitor vehicle behavior
- Ensure you can manually stop the vehicle

## Future Improvements

- [ ] Use depth map to calculate actual distance to person (replace bounding box size)
- [ ] Improve obstacle avoidance strategy (multi-step avoidance, path planning)
- [ ] Add LiDAR support (replace depth map as obstacle detection source)
- [ ] Dynamically adjust obstacle avoidance parameters
- [ ] Record and replay obstacle avoidance data

## LiDAR Integration (Future)

Current implementation uses depth maps for obstacle detection. If LiDAR is to be used in the future, only need to replace the obstacle detection input source:

```python
# Current: Use depth map
depth_frame = camera.get_depth_frame()
obstacle_result = obstacle_detector.detect_obstacle(depth_frame)

# Future: Use LiDAR
lidar_data = lidar.get_scan()
obstacle_result = obstacle_detector.detect_obstacle_from_lidar(lidar_data)
```

Obstacle avoidance logic and state machine remain unchanged.

## References

- Phase 2 README: `../phase2/README.md`
- OAKD Lite depth support: Refer to `../phase1/phase1_oakd_camera.py`
- DepthAI documentation: https://docs.luxonis.com/
