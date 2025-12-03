# Phase 1: OAK-D Desktop Demo

Phase 1 implements person detection, distance estimation, and Rock-Paper-Scissors game functionality using the OAK-D camera on desktop environments (computer/Raspberry Pi).

## Features

### 1. Person Detection
- **Input**: OAK-D color image
- **Output**:
  - `person_found`: True/False
  - `person_bbox`: (x_min, y_min, x_max, y_max)
- **Implementation**: Uses MediaPipe Pose for person detection (can be extended to use OAK-D's mobilenet-ssd model)

### 2. Distance Estimation
- **Input**: OAK-D depth map
- **Output**: `distance_to_person` (unit: meters)
- **Implementation**: Extracts a depth patch from the center region of the person bbox and calculates the average depth value

### 3. Game Module
- **Input**: Hand image/keypoints
- **Output**: rock / paper / scissors
- **Interface**: `result = rps_game.play_round(frame)`

## File Structure

```
phase1_person_detector.py  # Person detection module
phase1_oakd_camera.py      # OAK-D camera interface with depth support
phase1_rps_game.py         # RPS game wrapper class
phase1_demo.py             # Phase 1 main demo program
```

## Installation

```bash
# Basic dependencies
pip install opencv-python numpy mediapipe

# OAK-D camera support
pip install depthai

# RPS model (optional, for more accurate gesture recognition)
# Model file should be placed in ../project-1/ directory
# rps_model_improved.pth or rps_model.pth
```

## Usage

### Basic Run

```bash
# Run from project root directory
cd phase1
python phase1_demo.py
```

### Features

The program displays two modes after startup:

1. **Detection Mode**
   - Shows person detection bounding box
   - Displays distance information
   - Press `'d'` to switch to detection mode

2. **Interaction Mode**
   - After detecting a person, you can play Rock-Paper-Scissors
   - Shows gesture recognition results
   - Displays game score
   - Press `'i'` to switch to interaction mode

### Keyboard Controls

- `'q'` - Quit program
- `'i'` - Switch to interaction mode (RPS game)
- `'d'` - Switch to detection mode (person + distance)
- `'r'` - Reset RPS game

## Completion Criteria

✅ **Phase 1 Completion Criteria**:

1. ✅ Run program on desktop
2. ✅ Can see person detection (bounding box) + distance in the frame
3. ✅ Can play Rock-Paper-Scissors in "interaction mode" with stable results

## Technical Implementation

### Person Detection

Currently uses MediaPipe Pose for person detection. Can be extended to integrate OAK-D's mobilenet-ssd model for better performance:

```python
# Using mobilenet-ssd (requires integration into camera pipeline)
from phase1_person_detector import PersonDetector
detector = PersonDetector(use_separate_pipeline=True)
```

### Distance Estimation

Uses OAK-D's depth camera to calculate distance:

```python
# Get depth frame
depth_frame = camera.get_depth_frame()

# Calculate distance from bbox center
distance = camera.get_distance_from_bbox(person_bbox, depth_frame)
```

### RPS Game

Game module is wrapped as a simple interface:

```python
from phase1_rps_game import Phase1RPSGame

# Initialize game
rps_game = Phase1RPSGame()

# Play a round
result = rps_game.play_round(frame)
# result contains: result, player_gesture, ai_gesture, player_score, ai_score
```

## Troubleshooting

### OAK-D Camera Not Detected

- Ensure OAK-D camera is properly connected
- Check if DepthAI is correctly installed: `python -c "import depthai; print('OK')"`
- If no OAK-D is available, the program will automatically fall back to regular webcam (but without depth support)

### Person Detection Not Working

- Ensure MediaPipe is installed: `pip install mediapipe`
- Check if lighting conditions are adequate
- Try adjusting camera angle

### RPS Game Recognition Not Accurate

- Ensure hand is clearly visible in the frame
- Try using model file (`rps_model_improved.pth`) for better recognition
- Keep gesture stable for at least 1 second

## Next Steps (Phase 2+)

- Integrate mobilenet-ssd into main camera pipeline
- Add more game modes
- Optimize distance estimation accuracy
- Add multi-person detection support

