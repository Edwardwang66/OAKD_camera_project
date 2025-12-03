#!/bin/bash
# Fix OpenCV Qt/X11 display issues for X11 forwarding
# This script sets environment variables to prevent Qt backend errors

export QT_QPA_PLATFORM=offscreen
export OPENCV_VIDEOIO_PRIORITY_MSMF=0

# If DISPLAY is set, try to use it with GTK backend
if [ -n "$DISPLAY" ]; then
    export GDK_BACKEND=x11
fi

# Run the command passed as arguments
exec "$@"

