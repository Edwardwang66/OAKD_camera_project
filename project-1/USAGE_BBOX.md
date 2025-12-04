# Bounding Box Usage Instructions

## Feature Overview

Project-1 now supports gesture recognition using bounding boxes:

1. **Hand Detection**: Uses MediaPipe to detect hand position
2. **Bounding Box**: Returns hand bounding box coordinates (x, y, w, h)
3. **Model Inference**: Crops hand region based on bounding box, inputs to model for classification

## Workflow

```
Camera Frame
  ↓
MediaPipe Hand Detection
  ↓
Get Bounding Box (x, y, w, h)
  ↓
Crop Hand Region Based on BBox
  ↓
Resize to Model Input Size (64x64)
  ↓
Model Classification (Rock/Paper/Scissors)
  ↓
Display Result and Bounding Box
```

## Code Examples

### Basic Usage

```python
from oakd_hand_detector import OAKDHandDetector
from hand_gesture_detector_model import HandGestureDetectorModel

# Initialize detectors
hand_detector = OAKDHandDetector()
gesture_detector = HandGestureDetectorModel()

# Detect hand and gesture
frame = camera.get_frame()
bbox, landmarks, annotated = hand_detector.detect_hand_bbox(frame)

if bbox:
    x, y, w, h = bbox
    print(f"Hand detected at: ({x}, {y}), size: {w}x{h}")
    
    # Model will automatically use bbox for recognition
    gesture, result_frame, _ = gesture_detector.detect_gesture(frame)
    print(f"Gesture: {gesture.value}")
```

### Manual Region Cropping

```python
# Get bounding box
bbox, _, _ = hand_detector.detect_hand_bbox(frame)

if bbox:
    # Crop hand region
    hand_region = hand_detector.crop_hand_region(frame, bbox)
    
    # Can save or further process
    cv2.imwrite("hand_region.jpg", hand_region)
```

## Bounding Box Format

Bounding box return format: `(x, y, width, height)`

- `x`: Top-left X coordinate
- `y`: Top-left Y coordinate  
- `width`: Bounding box width
- `height`: Bounding box height

Includes padding (default 20-30 pixels) to ensure complete hand region.

## Visualization

Bounding box is automatically drawn on the image:
- **Green box**: MediaPipe hand detection bounding box
- **Blue box**: Model input region (if any)
- **Hand keypoints**: MediaPipe landmarks

## Advantages

Advantages of using bounding box:

1. **Improved Accuracy**: Only classify relevant regions
2. **Reduced Interference**: Exclude background and other objects
3. **Performance Optimization**: Process smaller image regions
4. **Visualization**: Clearly display detection region

## Using on OAKD Edge AI

If you want to use OAKD's built-in processing power:

1. Convert model to Blob format
2. Use `OAKDEdgeAICamera` class
3. Bounding box detection can run on camera (requires hand detection model)

See `README_OAKD_EDGE_AI.md` for details
