# OAKD Edge AI Usage Guide

This guide explains how to run gesture recognition models on OAKD camera's built-in processing power and use bounding boxes for detection.

## OAKD Camera Built-in Processing Power

OAKD Lite camera has a built-in Myriad X VPU that can run deep learning models on-device, achieving:
- **Reduce host computation burden**
- **Improve real-time performance**
- **Reduce latency**

## Features

1. **Hand Detection with Bounding Box**
   - Uses MediaPipe to detect hands
   - Returns bounding box coordinates (x, y, w, h)
   - Draws bounding box on image

2. **Model Inference Based on Bounding Box**
   - Crops hand region based on bounding box
   - Inputs cropped region to model for classification
   - Improves recognition accuracy

3. **Edge AI Support (Optional)**
   - Convert PyTorch model to Blob format
   - Run inference directly on OAKD camera
   - Fully utilize camera's built-in processing power

## Usage

### 1. Basic Usage (With Bounding Box)

```bash
cd project-1
python main.py
```

The program will automatically:
- Detect hand and draw bounding box
- Crop hand region based on bounding box
- Use model to classify cropped region

### 2. Convert Model to Blob Format (Edge AI)

#### Step 1: Install Dependencies

```bash
pip install openvino blobconverter
```

#### Step 2: Convert Model

```bash
# Method 1: Use conversion script
python convert_model_to_blob.py --model rps_model_improved.pth

# Method 2: Use online converter
# Visit: https://blobconverter.luxonis.com/
# Upload ONNX file for conversion
```

#### Step 3: Use Edge AI Mode

```python
from oakd_edge_ai import OAKDEdgeAICamera

# Initialize Edge AI camera
camera = OAKDEdgeAICamera(
    model_blob_path="rps_model_improved.blob",
    use_hand_detection=True
)

# Get frame with detection results
frame, bboxes, nn_results = camera.get_frame_with_detection()
```

## Code Structure

### Main Files

1. **`oakd_hand_detector.py`**
   - Hand detection with bounding boxes
   - Returns (x, y, w, h) coordinates

2. **`oakd_edge_ai.py`**
   - OAKD Edge AI camera interface
   - Supports running neural networks on camera

3. **`convert_model_to_blob.py`**
   - PyTorch model to Blob format conversion tool
   - Supports ONNX and OpenVINO conversion

4. **`hand_gesture_detector_model.py`**
   - Updated to support bounding box
   - Classifies based on bbox cropped region

## Bounding Box Workflow

```
1. Camera captures frame
   ↓
2. Hand Detector detects hand
   ↓
3. Returns Bounding Box (x, y, w, h)
   ↓
4. Crop hand region based on BBox
   ↓
5. Input cropped region to model
   ↓
6. Model classification (Rock/Paper/Scissors)
   ↓
7. Display result and Bounding Box
```

## Edge AI Workflow

```
1. PyTorch Model (.pth)
   ↓
2. Convert to ONNX format
   ↓
3. Convert to OpenVINO IR
   ↓
4. Convert to Blob format (.blob)
   ↓
5. Deploy to OAKD camera
   ↓
6. Run on Myriad X VPU
```

## Model Conversion Example

```python
# Convert PyTorch model to Blob
python convert_model_to_blob.py \
    --model rps_model_improved.pth \
    --output rps_model.blob \
    --input-size 64 64
```

## Performance Advantages

Advantages of using OAKD Edge AI:

- **Reduced Latency**: Model runs on camera, no need to transfer to host
- **CPU Offload**: Host CPU available for other tasks
- **Real-time Performance**: Higher frame rate and response speed
- **Power Optimization**: Dedicated VPU more efficient than CPU

## Notes

1. **Model Format**: Need to convert PyTorch model to Blob format
2. **Input Size**: Ensure model input size matches (default 64x64)
3. **Compatibility**: Some model architectures may not support Edge AI
4. **Fallback**: If Edge AI unavailable, automatically falls back to CPU inference

## Troubleshooting

### Bounding Box Not Displayed
- Check if hand is in frame
- Ensure adequate lighting
- Adjust MediaPipe detection threshold

### Edge AI Model Loading Failed
- Check Blob file path
- Verify model format is correct
- Check OAKD camera connection status

### Conversion Failed
- Ensure OpenVINO is installed
- Check model architecture compatibility
- Try using online converter

## Reference Resources

- [DepthAI Documentation](https://docs.luxonis.com/)
- [Blob Converter](https://blobconverter.luxonis.com/)
- [OpenVINO Toolkit](https://www.intel.com/content/www/us/en/developer/tools/openvino-toolkit/overview.html)
