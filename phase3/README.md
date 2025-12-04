# Phase 3: Person Following with Obstacle Avoidance

Phase 3 adds depth map-based obstacle avoidance functionality on top of Phase 2, avoiding collisions with obstacles while searching for and approaching people.

**Designed for: Raspberry Pi 5 + OAKD Lite Camera + DonkeyCar/VESC**

## Overview

Phase 3 implements the following features:
- ✅ Person tracking and approach based on Phase 2
- ✅ Front obstacle detection using depth maps
- ✅ Automatic obstacle avoidance mode when obstacles are detected
- ✅ Intelligent direction selection for bypassing (left or right turn)

## Quick Start

### Install Dependencies

```bash
cd phase3
pip install -r requirements.txt
```

### Run Program (No-GUI Mode, Recommended)

```bash
python phase3_demo.py --simulation --no-gui
```

### Install blobconverter (Enable Depth Support)

If depth map support is needed, install:

```bash
pip install blobconverter
```

For detailed instructions, see `INSTALL_BLOBCONVERTER.md`

## File Structure

```
phase3/
├── phase3_demo.py          # Main demo program
├── obstacle_detector.py    # Obstacle detection module
├── obstacle_avoider.py     # Obstacle avoidance control module
├── README.md               # This file
├── README_PHASE3.md        # Detailed documentation
├── QUICK_FIX.md            # Quick fix guide
├── requirements.txt        # Dependencies list
└── ...
```

## State Machine

Phase 3's state machine includes:

1. **SEARCH**: Slowly rotate to find person, detect front obstacles
2. **APPROACH**: Move towards person, detect obstacles before advancing
3. **AVOID_OBSTACLE**: Obstacle avoidance mode (stop, scan, turn)
4. **INTERACT**: Stop at target distance
5. **STOP**: Emergency stop

## Obstacle Avoidance Principle

- **Front detection region**: Middle 30% rectangular area of the frame
- **Depth value processing**: Filter invalid values, use median or 10th percentile minimum
- **Obstacle judgment**: If front depth < threshold (default 0.5m), obstacle detected
- **Avoidance strategy**: Stop → Scan left/right depth → Select direction → Turn → Resume

## Usage

### Basic Run

```bash
# Simulation mode (no GUI)
python phase3_demo.py --simulation --no-gui

# Actual vehicle control
python phase3_demo.py --vesc-port /dev/ttyACM0
```

### Command Line Arguments

- `--target-distance`: Target distance (meters, default: 1.0)
- `--vesc-port`: VESC serial port (e.g., /dev/ttyACM0)
- `--simulation`: Simulation mode (does not actually control vehicle)
- `--depth-threshold`: Obstacle detection threshold (meters, default: 0.5)
- `--no-gui`: Disable GUI display (avoid Qt errors)

## Dependent Modules

Phase 3 depends on shared modules from phase2:
- `oakd_camera.py` - OAKD camera interface (requires depth support)
- `car_controller.py` - Vehicle control interface
- `person_follower.py` - Person tracking control logic

These modules are located in the `../phase2/` directory.

## Troubleshooting

### Qt Display Errors

If you encounter Qt/X11 display errors, use the `--no-gui` option:

```bash
python phase3_demo.py --simulation --no-gui
```

For detailed instructions, see `QUICK_FIX.md` and `RUN_WITHOUT_CRASHING.md`

### Depth Support Unavailable

If depth support is not available, install `blobconverter`:

```bash
pip install blobconverter
```

For detailed instructions, see `INSTALL_BLOBCONVERTER.md`

## Detailed Documentation

- `README_PHASE3.md` - Phase 3 detailed documentation
- `QUICK_FIX.md` - Quick fix guide
- `RUN_WITHOUT_CRASHING.md` - Crash prevention guide
- `INSTALL_BLOBCONVERTER.md` - blobconverter installation guide
- `FIX_DISPLAY_ISSUE.md` - Display issue fixes

## Relationship with Phase 2

Phase 3 is based on Phase 2, adding:
- Depth map acquisition and processing
- Obstacle detection module
- Obstacle avoidance control logic
- AVOID_OBSTACLE state

Phase 2 files are located in the `../phase2/` directory, and Phase 3 will automatically import shared modules from there.

## Next Steps

- [ ] Use depth map to calculate actual distance to person (replace bounding box size)
- [ ] Improve obstacle avoidance strategy (multi-step avoidance, path planning)
- [ ] Add LiDAR support (replace depth map as obstacle detection source)
- [ ] Dynamically adjust obstacle avoidance parameters
