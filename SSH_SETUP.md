# SSH + X11 Forwarding Setup Guide

This guide explains how to run the OAKD Camera Project on a Raspberry Pi 5 without a screen, using SSH with X11 forwarding to display OpenCV windows on your Mac.

## Quick Start

1. **On Mac**: Install XQuartz and enable network connections
2. **Connect**: `ssh -Y pi@raspberrypi.local`
3. **Run**: `python main_menu.py`

## Detailed Setup

### Step 1: Install XQuartz on Mac

```bash
# Install via Homebrew
brew install --cask xquartz

# Or download from: https://www.xquartz.org/
```

### Step 2: Configure XQuartz

1. Open XQuartz (Applications > Utilities > XQuartz)
2. Go to **XQuartz > Preferences > Security**
3. Check **"Allow connections from network clients"**
4. **Restart XQuartz** (important!)

### Step 3: Connect to Raspberry Pi with X11 Forwarding

```bash
# Trusted X11 forwarding (recommended, faster)
ssh -Y pi@raspberrypi.local

# Or untrusted (more secure, may be slower)
ssh -X pi@raspberrypi.local
```

**Note**: Replace `raspberrypi.local` with your Pi's IP address if needed.

### Step 4: Verify X11 Forwarding

Once connected, check if DISPLAY is set:

```bash
echo $DISPLAY
# Should show something like: localhost:10.0
```

### Step 5: Run the Project

```bash
cd OAKD_camera_project
source venv/bin/activate  # If using virtual environment
python main_menu.py
```

OpenCV windows should now appear on your Mac!

## Troubleshooting

### "could not connect to display"

**Causes:**
- XQuartz is not running
- X11 forwarding not enabled in SSH
- DISPLAY variable not set

**Solutions:**
1. Make sure XQuartz is running on Mac
2. Reconnect with `ssh -Y` or `ssh -X`
3. Check DISPLAY: `echo $DISPLAY`
4. Try: `export DISPLAY=:0` (if needed)

### "X11 connection rejected"

**Causes:**
- XQuartz security settings blocking connections

**Solutions:**
1. Open XQuartz Preferences > Security
2. Enable "Allow connections from network clients"
3. Restart XQuartz
4. Reconnect via SSH

### Low FPS or Slow Performance

**Causes:**
- Network latency
- X11 forwarding overhead

**Solutions:**
1. Use `-Y` (trusted) instead of `-X` (untrusted)
2. Use wired network instead of WiFi
3. Reduce camera resolution in code
4. Consider using VNC instead for better performance

### GUI Not Available Warning

This is **normal** if:
- X11 forwarding is not set up
- Running in truly headless mode

**The application will still work!**
- Camera processing continues
- Game logic functions normally
- Only visual display is skipped

## Headless Mode

The project is designed to work **without any GUI**:

- All scripts check GUI availability automatically
- If GUI unavailable, apps continue running
- No crashes, just skips window display
- Perfect for headless servers or testing

## Alternative: VNC

For better performance than X11 forwarding, consider using VNC:

```bash
# On Raspberry Pi
sudo apt install realvnc-vnc-server
# Enable VNC in raspi-config

# On Mac: Use VNC Viewer to connect
```

VNC provides better performance but requires a screen or virtual display on the Pi.

