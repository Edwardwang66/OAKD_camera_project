#!/bin/bash
# Run emoji display with proper environment variables
# This script sets environment before Python imports OpenCV

# Unset DISPLAY to force OpenCV to use framebuffer instead of X11
unset DISPLAY

# Disable Qt completely
export QT_QPA_PLATFORM=offscreen
unset QT_QPA_PLATFORM

# Prevent Qt from loading
export QT_LOGGING_RULES="*.debug=false"

# Set OpenCV to avoid Qt
export OPENCV_VIDEOIO_PRIORITY_LIST=V4L2,FFMPEG
export OPENCV_VIDEOIO_PRIORITY_MSMF=0

echo "Environment configured for framebuffer display"
echo "Running emoji display..."

# Run the Python script with environment variables
python emoji_display_framebuffer.py "$@"

