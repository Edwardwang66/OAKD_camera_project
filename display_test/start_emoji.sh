#!/bin/bash
# Start emoji display with proper environment to avoid Qt errors
# This script MUST be run from the display_test directory

cd "$(dirname "$0")"

echo "============================================================"
echo "Starting Emoji Display (Framebuffer Mode)"
echo "============================================================"
echo ""

# Unset DISPLAY completely to avoid X11/Qt issues
unset DISPLAY

# Remove Qt platform variable
unset QT_QPA_PLATFORM

# Set OpenCV to use minimal backend
export OPENCV_VIDEOIO_PRIORITY_LIST=V4L2,FFMPEG
export OPENCV_VIDEOIO_PRIORITY_MSMF=0

# Disable Qt completely
export QT_QPA_PLATFORM=offscreen
unset QT_QPA_PLATFORM

echo "Environment configured:"
echo "  DISPLAY: (unset)"
echo "  QT_QPA_PLATFORM: (unset)"
echo ""
echo "Running emoji display..."
echo "Press 'q' to quit"
echo "============================================================"
echo ""

# Use the simple version that avoids Qt
python3 emoji_simple.py "$@"

