# OAKD Camera HDMI Display

Simple script to display OAKD camera feed on HDMI1 display on Raspberry Pi using framebuffer.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set framebuffer permissions (if needed):
```bash
sudo chmod 666 /dev/fb0
```

3. Run the camera display:
```bash
./run_oakd_hdmi.sh
```

Or directly:
```bash
python3 oakd_to_hdmi.py
```

## Usage

- Press Ctrl+C to quit
- Camera feed will display directly on HDMI1 via framebuffer
- No X11/Qt required - works headless

## Requirements

- Raspberry Pi with OAKD camera connected via USB
- HDMI display connected to HDMI1 port
- Python 3 with OpenCV and DepthAI installed
- Framebuffer access (usually works by default, may need permissions)
