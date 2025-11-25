# OAKD Camera Projects

This repository contains multiple OpenCV-based projects using the OAKD Lite camera for the Raspberry Pi 5 Donkey Car setup with a 7-inch screen.

## Projects

### Project 1: Rock-Paper-Scissors Game
A real-time rock-paper-scissors game that detects hand gestures (rock, paper, or scissors) and plays against an AI opponent (Donkey Car).

**Location**: `project-1/`

**Features**:
- Hand gesture recognition using MediaPipe
- Real-time game with AI opponent
- Score tracking
- UI optimized for 7-inch screen

**Quick Start**:
```bash
cd project-1
pip install -r requirements-laptop.txt  # For laptop testing
python test_laptop.py  # Test on laptop
python main.py  # Run full game
```

### Project 2: Air Drawing
An air drawing application that tracks your index finger and visualizes the drawing on screen in real-time.

**Location**: `project-2/`

**Features**:
- Index finger tracking
- Real-time drawing visualization
- Multiple colors and brush sizes
- Split-screen display (camera + canvas)

**Quick Start**:
```bash
cd project-2
pip install opencv-python mediapipe numpy  # For laptop testing
python main.py
```

### Project 3: 1v1 Shooting Game - Car as Referee
A gesture-based shooting game where two players face off using "pistol gestures" to shoot each other. The car acts as a referee, detecting shots and determining hits.

**Location**: `project-3/`

**Features**:
- Pistol gesture detection (index finger + thumb up)
- Two-player tracking
- Shooting direction detection
- Hit detection and health system
- Referee display with win announcements

**Quick Start**:
```bash
cd project-3
pip install opencv-python mediapipe numpy  # For laptop testing
python test_laptop.py  # Test pistol detection
python main.py  # Run full game
```

## Hardware Setup

- **Raspberry Pi 5**
- **OAKD Lite Camera** (USB connected)
- **7-inch Display** (800x480 recommended)
- **Donkey Car** setup

## Software Requirements

Both projects require:
- Python 3.8+
- OpenCV
- MediaPipe
- NumPy
- DepthAI (for OAKD camera, optional for laptop testing)

## Testing on Laptop

Both projects can be tested on your laptop using a regular webcam:

1. Install minimal dependencies (no DepthAI needed)
2. Run the test scripts
3. The applications will automatically use your webcam

See individual project READMEs for detailed instructions.

## Project Structure

```
OAKD_camera_project/
├── project-1/          # Rock-Paper-Scissors Game
│   ├── main.py
│   ├── hand_gesture_detector.py
│   ├── game_logic.py
│   ├── oakd_camera.py
│   ├── ui_display.py
│   └── ...
├── project-2/          # Air Drawing
│   ├── main.py
│   ├── finger_tracker.py
│   ├── drawing_canvas.py
│   ├── camera.py
│   ├── ui_display.py
│   └── ...
├── project-3/          # 1v1 Shooting Game
│   ├── main.py
│   ├── pistol_detector.py
│   ├── game_logic.py
│   ├── camera.py
│   ├── ui_display.py
│   └── ...
└── README.md           # This file
```

## License

MIT License - see LICENSE file for details
