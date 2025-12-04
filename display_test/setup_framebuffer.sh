#!/bin/bash
# Setup framebuffer display for Raspberry Pi
# This script sets up the environment for direct framebuffer access

echo "Setting up framebuffer display..."

# Set DISPLAY for local framebuffer
export DISPLAY=:0.0

# Disable Qt backend to avoid crashes
unset QT_QPA_PLATFORM

# Set OpenCV to prefer V4L2 (Video4Linux2) for camera, avoid Qt for display
export OPENCV_VIDEOIO_PRIORITY_LIST=V4L2,FFMPEG

# Check if framebuffer exists
if [ -e /dev/fb0 ]; then
    echo "✓ Framebuffer found: /dev/fb0"
    
    # Get resolution
    if command -v fbset &> /dev/null; then
        RESOLUTION=$(fbset -s | grep geometry | awk '{print $2 "x" $3}')
        echo "✓ Resolution: $RESOLUTION"
    fi
else
    echo "✗ Framebuffer not found"
fi

echo ""
echo "Environment setup complete!"
echo "Run your display test now:"
echo "  python display_check.py"
echo "  python emoji_display.py --emoji smile"

