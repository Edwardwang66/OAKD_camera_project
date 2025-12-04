# OAKD Edge AI + Bounding Box Implementation Summary

## ✅ Completed Features

### 1. Bounding Box Detection
- ✅ **Hand Detection**: Uses MediaPipe to detect hands
- ✅ **Bounding Box Return**: Returns (x, y, w, h) coordinates
- ✅ **Visualization**: Draws bounding box on image
- ✅ **Model Input**: Crops hand region based on bounding box for classification

### 2. OAKD Edge AI Support
- ✅ **Edge AI Interface**: Created `OAKDEdgeAICamera` class
- ✅ **Model Conversion Tool**: `convert_model_to_blob.py` for model conversion
- ✅ **Blob Format Support**: Supports running models on OAKD camera

### 3. Code Updates
- ✅ **hand_gesture_detector_model.py**: Updated to support bounding box
- ✅ **main.py**: Integrated bounding box detection and display
- ✅ **oakd_hand_detector.py**: Dedicated hand detector that returns bounding box

## 📁 New Files

1. **`oakd_edge_ai.py`**
   - OAKD Edge AI camera interface
   - Supports running models on camera's built-in VPU

2. **`oakd_hand_detector.py`**
   - Hand detector that returns bounding box
   - Supports cropping hand regions

3. **`convert_model_to_blob.py`**
   - PyTorch model to Blob format conversion tool
   - Supports ONNX and OpenVINO conversion

4. **`README_OAKD_EDGE_AI.md`**
   - Edge AI usage guide

5. **`USAGE_BBOX.md`**
   - Bounding Box usage instructions

## 🔄 Workflow

### Current Implementation (CPU Inference + Bounding Box)

```
Camera Frame (640x480)
  ↓
MediaPipe Hand Detection
  ↓
Get Bounding Box (x, y, w, h)
  ↓
Crop Hand Region Based on BBox
  ↓
Resize to 64x64
  ↓
PyTorch Model Classification (CPU)
  ↓
Return Result and Bounding Box
```

### Edge AI Implementation (OAKD VPU Inference)

```
Camera Frame (OAKD)
  ↓
Hand Detection Model (OAKD VPU) - Optional
  ↓
Get Bounding Box
  ↓
Crop Hand Region
  ↓
Gesture Classification Model (OAKD VPU)
  ↓
Return Result (No need to transfer to host)
```

## 🚀 Usage

### Basic Usage (With Bounding Box)

```bash
cd project-1
python main.py
```

The program will automatically:
1. Detect hand and display bounding box (green box)
2. Crop region based on bounding box
3. Use model to classify cropped region
4. Display recognition result

### Edge AI Usage (Requires Model Conversion)

```bash
# 1. Convert model
python convert_model_to_blob.py --model rps_model_improved.pth

# 2. Use Edge AI mode (requires code modification to use OAKDEdgeAICamera)
```

## 📊 Bounding Box Format

Return format: `(x, y, width, height)`

- **x, y**: Top-left corner coordinates
- **width, height**: Bounding box dimensions
- **Includes padding**: Default 20-30 pixels to ensure complete hand region

## 🎯 Advantages

### Bounding Box Advantages
1. ✅ **Improved Accuracy**: Only classify relevant regions
2. ✅ **Reduced Interference**: Exclude background
3. ✅ **Performance Optimization**: Process smaller regions
4. ✅ **Visualization**: Clearly display detection region

### Edge AI Advantages
1. ✅ **Low Latency**: Model runs on camera
2. ✅ **CPU Offload**: Host CPU available for other tasks
3. ✅ **Real-time Performance**: Higher frame rate
4. ✅ **Power Optimization**: VPU more efficient than CPU

## 📝 Next Steps (Optional)

If you want to fully use OAKD Edge AI:

1. **Convert Model to Blob**
   ```bash
   python convert_model_to_blob.py --model rps_model_improved.pth
   ```

2. **Use Online Converter**
   - Visit: https://blobconverter.luxonis.com/
   - Upload ONNX file
   - Download .blob file

3. **Modify Code to Use Edge AI**
   ```python
   from oakd_edge_ai import OAKDEdgeAICamera
   
   camera = OAKDEdgeAICamera(
       model_blob_path="rps_model_improved.blob",
       use_hand_detection=True
   )
   ```

## ⚠️ Notes

1. **Model Conversion**: Blob format requires specific model architecture support
2. **Input Size**: Ensure model input size matches (default 64x64)
3. **Fallback**: If Edge AI unavailable, automatically falls back to CPU inference
4. **Compatibility**: Some complex models may not support Edge AI

## 📚 Documentation

- **README_OAKD_EDGE_AI.md**: Edge AI detailed guide
- **USAGE_BBOX.md**: Bounding Box usage instructions
- **README.md**: Project main documentation
