# Using the Trained Model for Rock-Paper-Scissors

This project now supports using the trained PyTorch model from the [ECE176_final repository](https://github.com/edwardw005/ECE176_final) instead of MediaPipe for gesture recognition.

## Setup

### 1. Download the Model

You have two options:

**Option A: Automatic Download**
```bash
cd project-1
python download_model.py
```

**Option B: Manual Download**
1. Go to https://github.com/edwardw005/ECE176_final
2. Download `rps_model_improved.pth` or `rps_model.pth`
3. Place it in the `project-1/` directory

### 2. Install PyTorch

```bash
pip install torch torchvision
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Usage

### Using the Trained Model (Default)

The application will automatically use the model if available:

```bash
python main.py
```

### Using MediaPipe (Fallback)

If the model is not found, the application will automatically fall back to MediaPipe:

```bash
python main.py
```

### Explicitly Choose Detector

You can modify `main.py` to explicitly choose:

```python
# Use model
app = RockPaperScissorsApp(use_model=True)

# Use MediaPipe
app = RockPaperScissorsApp(use_model=False)
```

## Model Architecture

The model uses a CNN architecture with:
- 4 convolutional blocks with batch normalization
- Max pooling layers
- Fully connected layers with dropout
- Output: 3 classes (Rock, Paper, Scissors)

## Model Input

- **Size**: 64x64 pixels
- **Format**: RGB (normalized to 0-1)
- **Preprocessing**: Automatic resizing and normalization

## Advantages of Using the Model

1. **Better Accuracy**: Trained specifically on rock-paper-scissors gestures
2. **Consistent Results**: More reliable than rule-based MediaPipe detection
3. **Custom Training**: Can be retrained with your own data

## Troubleshooting

### Model Not Found
- Run `python download_model.py` to download
- Or manually download from GitHub and place in `project-1/`

### PyTorch Not Installed
```bash
pip install torch torchvision
```

### CUDA/GPU Issues
- The model will automatically use CPU if CUDA is not available
- For Raspberry Pi, CPU is recommended

### Model Architecture Mismatch
- If you get shape errors, the model architecture might differ
- Check the original training notebook for the exact architecture
- You may need to adjust `model_loader.py` to match your model

## Reference

- Original Repository: https://github.com/edwardw005/ECE176_final
- Model Files: `rps_model_improved.pth` or `rps_model.pth`

