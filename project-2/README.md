# Project 2: Air Drawing with Index Finger

A real-time air drawing application that tracks your index finger and visualizes the drawing on a 7-inch screen. Perfect for the Raspberry Pi 5 Donkey Car setup with OAKD Lite camera.

## Features

- **Gesture-Based Drawing Control**: 
  - **Index Finger Extended** = Draw (green indicator)
  - **Fist** = Stop drawing / Lift pen (red indicator)
- **Index Finger Tracking**: Uses MediaPipe to track index finger position in real-time
- **Air Drawing**: Draw in the air by moving your index finger
- **Real-time Visualization**: See your drawing appear on the 7-inch screen
- **Drawing Classification**: Automatically detects what you're drawing:
  - **Circle** - Round shapes and ovals
  - **Square** - Four-sided shapes (squares, rectangles)
  - **Triangle** - Three-sided shapes
  - **Line** - Long, thin lines
  - **Heart** - Heart-shaped drawings
  - **Unknown** - Other shapes
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

- **Index Finger Extended**: Draw (green indicator shows)
- **Fist**: Stop drawing / Lift pen (red indicator shows)
- **'c'**: Clear the canvas
- **'d'**: Force detection of current drawing
- **'1'**: Black color
- **'2'**: Red color
- **'3'**: Green color
- **'4'**: Blue color
- **'5'**: Orange color
- **'+' or '='**: Increase brush size
- **'-' or '_'**: Decrease brush size
- **'q'**: Quit application

### What Can Be Detected

The drawing classifier can detect the following shapes:

1. **Circle** (✓)
   - Round shapes with high circularity
   - Ovals and ellipses
   - Detection: Based on contour circularity and vertex count

2. **Square** (✓)
   - Four-sided shapes
   - Squares and rectangles
   - Detection: 4 vertices with square-like aspect ratio

3. **Triangle** (✓)
   - Three-sided shapes
   - Any triangular form
   - Detection: 3 vertices with high solidity

4. **Line** (✓)
   - Long, thin lines
   - Straight or slightly curved lines
   - Detection: High aspect ratio (very long or very tall)

5. **Heart** (✓)
   - Heart-shaped drawings
   - Wider at top, pointed at bottom
   - Detection: Specific geometric properties (wider top, two lobes)

6. **Unknown**
   - Other shapes that don't match above categories
   - Complex drawings or incomplete shapes

## How It Works

1. **Camera Capture**: Captures video from OAKD Lite camera or webcam
2. **Finger Tracking**: MediaPipe detects hand and tracks index finger tip position
3. **Drawing Canvas**: Maps finger position to canvas coordinates and draws lines
4. **UI Display**: Shows camera feed on left, drawing canvas on right
5. **Real-time Updates**: Continuously updates as you move your finger

## Project Structure

```
project-2/
├── main.py                  # Main application entry point
├── camera.py                # Camera interface (OAKD or webcam)
├── finger_tracker.py        # Gesture detection (fist vs index finger)
├── drawing_canvas.py        # Drawing canvas management
├── drawing_classifier.py    # Drawing classification model
├── ui_display.py            # UI rendering for 7-inch screen
├── test_classifier.py       # Test script for classifier
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Testing the Classifier

You can test what shapes the classifier can detect:

```bash
python test_classifier.py
```

This will create test shapes and show what the classifier detects.

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

