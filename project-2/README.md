# Project 2: Air Drawing with Index Finger

A real-time air drawing application that tracks your index finger and visualizes the drawing on a 7-inch screen. Perfect for the Raspberry Pi 5 Donkey Car setup with OAKD Lite camera.

## Features

- **Index Finger Tracking**: Uses MediaPipe to track index finger position in real-time
- **Air Drawing**: Draw in the air by moving your index finger
- **Real-time Visualization**: See your drawing appear on the 7-inch screen
- **Multiple Colors**: Switch between 5 different colors
- **Adjustable Brush Size**: Increase/decrease brush size
- **Clear Canvas**: Clear the drawing with a single keypress

## Hardware Requirements

- Raspberry Pi 5
- OAKD Lite camera (or webcam for testing)
- 7-inch touchscreen display (800x480 recommended)
- Donkey Car setup

## Software Requirements

- Python 3.8+
- OpenCV
- MediaPipe
- DepthAI (for OAKD camera, optional for laptop testing)
- NumPy

## Installation

### For Raspberry Pi (with OAKD camera):

1. Navigate to project directory:
```bash
cd project-2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure your OAKD Lite camera is connected via USB.

### For Laptop Testing:

1. Navigate to project directory:
```bash
cd project-2
```

2. Install minimal dependencies:
```bash
pip install opencv-python mediapipe numpy
```

3. Your laptop webcam will be used automatically.

## Usage

Run the main application:
```bash
python main.py
```

### Controls

- **Index Finger**: Point and move your index finger to draw
- **'c'**: Clear the canvas
- **'1'**: Black color
- **'2'**: Red color
- **'3'**: Green color
- **'4'**: Blue color
- **'5'**: Orange color
- **'+' or '='**: Increase brush size
- **'-' or '_'**: Decrease brush size
- **'q'**: Quit application

## How It Works

1. **Camera Capture**: Captures video from OAKD Lite camera or webcam
2. **Finger Tracking**: MediaPipe detects hand and tracks index finger tip position
3. **Drawing Canvas**: Maps finger position to canvas coordinates and draws lines
4. **UI Display**: Shows camera feed on left, drawing canvas on right
5. **Real-time Updates**: Continuously updates as you move your finger

## Project Structure

```
project-2/
├── main.py              # Main application entry point
├── camera.py            # Camera interface (OAKD or webcam)
├── finger_tracker.py    # Index finger tracking using MediaPipe
├── drawing_canvas.py    # Drawing canvas management
├── ui_display.py        # UI rendering for 7-inch screen
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Troubleshooting

### Camera not detected
- Ensure the OAKD Lite camera is properly connected via USB
- Check that DepthAI drivers are installed correctly
- The app will automatically fallback to webcam if OAKD is not available

### Finger not detected
- Ensure good lighting conditions
- Keep your hand clearly visible in the camera frame
- Make sure only one hand is visible
- Hold your index finger extended clearly

### Drawing not smooth
- Move your finger slowly for smoother lines
- Ensure consistent lighting
- Keep hand steady while drawing

## Future Enhancements

- Save drawings to file
- Undo/redo functionality
- More color options
- Different brush styles
- Gesture-based controls (e.g., fist to clear)
- Multi-finger drawing modes

## License

MIT License - see LICENSE file for details

