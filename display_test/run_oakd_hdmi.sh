#!/bin/bash
# Run OAKD camera display to HDMI screen
# This script sets environment to avoid Qt issues

cd "$(dirname "$0")"

echo "============================================================"
echo "OAKD Camera to HDMI Display"
echo "============================================================"
echo ""

# Unset DISPLAY to avoid X11/Qt issues
unset DISPLAY
unset QT_QPA_PLATFORM

echo "Environment configured for HDMI display"
echo "Starting camera feed..."
echo ""

# Run the display script
python3 oakd_to_hdmi.py "$@"

