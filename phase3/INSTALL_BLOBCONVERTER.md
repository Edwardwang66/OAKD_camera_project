# Install blobconverter to Enable Person Detection and Depth Support

## Problem

If you see the following error:
```
Warning: blobconverter not available. Install with: pip install blobconverter
Person detection will be disabled.
[OAKDCamera] Error setting up DepthAI detection: blobconverter required for person detection
```

This means you need to install `blobconverter` to use the OAKD camera's edge AI person detection functionality.

## Solution

### Install blobconverter

On Raspberry Pi, run:

```bash
pip install blobconverter
```

If in a virtual environment:

```bash
# Activate virtual environment
source env/bin/activate  # or your virtual environment path

# Install blobconverter
pip install blobconverter
```

### Verify Installation

```bash
python -c "import blobconverter; print('blobconverter installed successfully')"
```

## After Installation

Rerun phase3_demo.py, and you should see:

```
[OAKDCamera] Camera initialized successfully with DepthAI person detection and depth support
```

Instead of:

```
[OAKDCamera] Camera initialized with MediaPipe person detection fallback (no depth)
```

## About Depth Support

OAKD Lite uses stereo vision to obtain depth maps. After installing `blobconverter`, depth support should be automatically enabled (if the camera supports stereo depth).

If depth support is still not available, it may be because:
1. The camera model doesn't support stereo depth (some models only have RGB)
2. Need to check the camera's actual hardware configuration

## Temporary Solution

If blobconverter is not installed, the program will fall back to MediaPipe person detection (running on Raspberry Pi CPU), but will lose:
- Edge AI performance advantage (detection runs on camera VPU)
- Depth map support (requires DepthAI pipeline)

The program can still run, just with slightly worse performance.
