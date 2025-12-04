# OAKD Camera HDMI Display

Simple script to display OAKD camera feed on HDMI1 display on Raspberry Pi using framebuffer.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Setup framebuffer (detects and sets permissions automatically):
```bash
chmod +x setup_framebuffer.sh
./setup_framebuffer.sh
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
- Script automatically detects framebuffer device and sets permissions

## Manual Setup (if auto-setup fails)

If the setup script doesn't work, manually set permissions:
```bash
# Find framebuffer devices
ls -l /dev/fb*

# Set permissions (usually /dev/fb0 for HDMI1)
sudo chmod 666 /dev/fb0

# Or specify a different device
python3 oakd_to_hdmi.py --fb /dev/fb1
```

## Troubleshooting

### Camera Communication Error (X_LINK_ERROR)

If you see `X_LINK_ERROR` or `Communication exception`:

1. **Check USB connection:**
   ```bash
   lsusb | grep -i oak
   ```
   If no device found, try unplugging and replugging the USB cable.

2. **Try a different USB port** - Some ports may not provide enough power

3. **Check USB permissions:**
   ```bash
   sudo usermod -a -G dialout $USER
   # Log out and log back in
   ```

4. **Reset the device:**
   - Unplug the OAKD camera
   - Wait 5 seconds
   - Plug it back in
   - Wait for device to initialize (5-10 seconds)
   - Try running the script again

5. **Check if device is busy:**
   ```bash
   # Check if another process is using the camera
   lsof | grep -i usb
   ```

The script will automatically retry on communication errors up to 10 times before exiting.

## Requirements

- Raspberry Pi with OAKD camera connected via USB
- HDMI display connected to HDMI1 port
- Python 3 with OpenCV and DepthAI installed
- Framebuffer access (script will try to set permissions automatically)
