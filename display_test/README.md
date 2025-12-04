# OAKD Camera HDMI Display

Simple script to display OAKD camera feed on HDMI1 display on Raspberry Pi.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the camera display:
```bash
./run_oakd_hdmi.sh
```

Or directly:
```bash
python3 oakd_to_hdmi.py
```

## Usage

- Press 'q' to quit
- Camera feed will display in fullscreen on HDMI1

## Requirements

- Raspberry Pi with OAKD camera connected via USB
- HDMI display connected to HDMI1 port
- Python 3 with OpenCV and DepthAI installed
