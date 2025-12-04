# Rock-Paper-Scissors Game with OAKD Camera

A real-time rock-paper-scissors game that uses the OAKD Lite camera to detect hand gestures and displays the game on a 7-inch screen attached to a Raspberry Pi 5 Donkey Car.

## Features

- **Hand Gesture Recognition**: Uses MediaPipe hand pose detection to detect rock, paper, or scissors gestures
- **Pose-Based Classification**: Determines gestures based on finger keypoints/landmarks (not bounding boxes)
- **Real-time Detection**: Fast and efficient gesture recognition using MediaPipe hand landmarks
- **OAKD Camera Integration**: Captures video from the OAKD Lite camera using DepthAI
- **Game Logic**: Full rock-paper-scissors game with AI opponent (Donkey Car)
- **UI Display**: Beautiful game interface optimized for 7-inch screen (800x480)
- **Score Tracking**: Keeps track of player and AI scores across multiple rounds

## Hardware Requirements

- Raspberry Pi 5
- OAKD Lite camera
- 7-inch touchscreen display (800x480 recommended)
- Donkey Car setup

## Software Requirements

- Python 3.8+
- OpenCV
- MediaPipe (for hand pose detection)
- DepthAI (for OAKD camera)
- NumPy

**Note**: This project uses MediaPipe hand pose detection only. No neural network models are required.

## Installation

### For Raspberry Pi (with OAKD camera):

1. Clone or navigate to this repository:
```bash
cd OAKD_camera_project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure your OAKD Lite camera is connected to the Raspberry Pi via USB.

### For Laptop Testing (without OAKD camera):

1. Navigate to the project directory:
```bash
cd OAKD_camera_project
```

2. Install minimal dependencies (no DepthAI required):
```bash
pip install -r requirements-laptop.txt
```

3. Your laptop webcam will be used automatically.

## Usage

### On Raspberry Pi (with OAKD camera):

Run the main application:
```bash
python main.py
```

### On Laptop (for testing):

**Option 1: Test gesture detection only:**
```bash
python test_laptop.py
```

**Option 2: Test full game with webcam:**
```bash
python test_full_game_laptop.py
```

**Option 3: Run main.py (will automatically use webcam if OAKD not available):**
```bash
python main.py
```

### How to Play

1. **Show your hand**: Position your hand in front of the OAKD camera
2. **Make a gesture**: 
   - **Rock**: Close your fist (all fingers closed)
   - **Paper**: Open your hand (all fingers extended)
   - **Scissors**: Extend index and middle fingers (like a peace sign)
3. **Hold the gesture**: Keep your hand steady for about 1 second
4. **See the result**: The game will display your choice, the Donkey Car's choice, and the winner
5. **Play again**: Show a new gesture to play another round

### Controls

- **'q'**: Quit the game
- **'r'**: Reset the game (scores and round count)

## Project Structure

```
OAKD_camera_project/
├── main.py                    # Main application entry point
├── oakd_camera.py            # OAKD Lite camera interface
├── hand_gesture_detector.py  # Hand gesture recognition using MediaPipe
├── game_logic.py             # Rock-paper-scissors game logic
├── ui_display.py             # UI rendering for 7-inch screen
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## How It Works

1. **Camera Capture**: The `OAKDCamera` class captures RGB frames from the OAKD Lite camera using DepthAI
2. **Hand Pose Detection**: MediaPipe detects hand landmarks (21 keypoints) in real-time
3. **Gesture Classification**: Based on finger keypoint positions, determines if gesture is Rock, Paper, or Scissors:
   - **Rock**: All fingers closed (fist)
   - **Paper**: All 5 fingers extended
   - **Scissors**: Only index and middle fingers extended
4. **Game Logic**: The `RockPaperScissorsGame` class manages game state, AI opponent choices, and result calculation
5. **UI Display**: The `GameUI` class creates a split-screen display showing the camera feed with hand landmarks and game information
6. **Main Loop**: The `RockPaperScissorsApp` coordinates all components in a real-time game loop

## Gesture Detection Method

The system uses **MediaPipe hand pose detection** (not bounding boxes or neural networks):

- **Hand Landmarks**: MediaPipe detects 21 hand keypoints in real-time
- **Pose-Based Classification**: Gestures are determined by analyzing finger keypoint positions
- **No Model Required**: Uses rule-based classification based on finger extension
- **Real-time Performance**: Fast and efficient, no model inference overhead
- **Visualization**: Hand landmarks and connections are drawn on the frame

## Troubleshooting

### Camera not detected
- Ensure the OAKD Lite camera is properly connected via USB
- Check that DepthAI drivers are installed correctly
- Try running with `sudo` if permission issues occur

### Gesture not detected
- Ensure good lighting conditions
- Keep your hand clearly visible in the camera frame
- Hold the gesture steady for at least 1 second
- Make sure only one hand is visible in the frame

### Display issues
- Adjust screen resolution in `ui_display.py` if your screen size differs
- Make sure OpenCV can access your display (may need X11 forwarding if using SSH)

## Future Enhancements

- Add sound effects for wins/losses
- Implement best-of-N rounds mode
- Add gesture calibration for better accuracy
- Support for multiple players
- Save game statistics

## License

MIT License - see LICENSE file for details
