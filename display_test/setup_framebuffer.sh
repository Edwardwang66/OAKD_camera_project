#!/bin/bash
# Setup script to detect and configure framebuffer for HDMI display

echo "============================================================"
echo "Framebuffer Setup for HDMI Display"
echo "============================================================"
echo ""

# Find all framebuffer devices
echo "Scanning for framebuffer devices..."
FB_DEVICES=$(ls /dev/fb* 2>/dev/null)

if [ -z "$FB_DEVICES" ]; then
    echo "❌ No framebuffer devices found!"
    echo "Make sure HDMI is connected."
    exit 1
fi

echo "Found framebuffer devices:"
for dev in $FB_DEVICES; do
    echo "  - $dev"
    
    # Try to get info about this device
    if command -v fbset &> /dev/null; then
        RESOLUTION=$(fbset -i -fb "$dev" 2>/dev/null | grep -i geometry | head -1)
        if [ ! -z "$RESOLUTION" ]; then
            echo "    Resolution: $RESOLUTION"
        fi
    fi
done

echo ""
echo "Setting permissions on framebuffer devices..."

# Set permissions on all framebuffer devices
for dev in $FB_DEVICES; do
    echo "Setting permissions on $dev..."
    sudo chmod 666 "$dev" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "  ✓ $dev permissions set"
    else
        echo "  ✗ Failed to set permissions on $dev"
    fi
done

echo ""
echo "Checking permissions..."
for dev in $FB_DEVICES; do
    if [ -r "$dev" ] && [ -w "$dev" ]; then
        echo "  ✓ $dev is readable and writable"
    else
        echo "  ✗ $dev is NOT accessible (may need sudo)"
    fi
done

echo ""
echo "============================================================"
echo "Setup complete!"
echo "============================================================"
echo ""
echo "To test, run:"
echo "  python3 oakd_to_hdmi.py"
echo ""

