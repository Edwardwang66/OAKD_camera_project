# How to Avoid Qt Errors Causing Program Crashes

## Problem

Qt errors cause the program to crash immediately (Aborted), and cannot be resolved with simple error handling.

## Best Solution: Use --no-gui Option

The simplest and most reliable method is to use the `--no-gui` option to completely skip GUI-related code:

```bash
python phase3_demo.py --simulation --no-gui
```

This will:
- ✅ Program will not crash
- ✅ All functionality works normally
- ✅ Control commands output to terminal
- ✅ No display window (but all logic works normally)

## Quick Start Command

```bash
cd phase3

# No-GUI mode (recommended, avoids all Qt issues)
python phase3_demo.py --simulation --no-gui
```

## Install blobconverter (Enable Depth Support)

If you also want to enable depth map support, install:

```bash
pip install blobconverter
```

Then rerun the program.

## Program Output Example

When using `--no-gui`, you'll see output like this:

```
[SIM] Car Command: LEFT TURN | Linear: 0.00 m/s, Angular: 0.30 rad/s

--- Status (State: SEARCH) ---
Person detected: False
Obstacle ahead: False
Car: linear=0.00 m/s, angular=0.30 rad/s
Mode: SIMULATION
----------------------------------------
```

All functionality is running, just without a graphical window.

## If GUI is Required

If you really need GUI display, you can try:

1. **Use headless mode environment variables** (may not work):
   ```bash
   unset QT_QPA_PLATFORM
   export OPENCV_VIDEOIO_PRIORITY_MSMF=0
   python phase3_demo.py --simulation
   ```

2. **Check X11 connection**:
   ```bash
   echo $DISPLAY
   # Should show something like: localhost:10.0
   ```

3. **Reconnect SSH**:
   ```bash
   exit
   ssh -Y pi@raspberrypi.local
   ```

4. **Confirm XQuartz is running** (on Mac)

But the most reliable method is still to use `--no-gui`.
