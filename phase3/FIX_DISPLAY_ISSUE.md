# Fix OpenCV Qt/X11 Display Issues

If you encounter the following error:
```
qt.qpa.xcb: could not connect to display localhost:10.0
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
```

This is caused by OpenCV trying to use the Qt backend which is incompatible with X11 forwarding.

## Quick Fix Methods

### Method 1: Use Environment Variables (Recommended)

Set environment variables before running the program:

```bash
export QT_QPA_PLATFORM=offscreen
export OPENCV_VIDEOIO_PRIORITY_MSMF=0
python phase3_demo.py --simulation
```

Or one-line command:
```bash
QT_QPA_PLATFORM=offscreen OPENCV_VIDEOIO_PRIORITY_MSMF=0 python phase3_demo.py --simulation
```

### Method 2: Use Fix Script

```bash
chmod +x fix_opencv_display.sh
./fix_opencv_display.sh python phase3_demo.py --simulation
```

### Method 3: Add to ~/.bashrc (Permanent Fix)

```bash
echo 'export QT_QPA_PLATFORM=offscreen' >> ~/.bashrc
echo 'export OPENCV_VIDEOIO_PRIORITY_MSMF=0' >> ~/.bashrc
source ~/.bashrc
```

### Method 4: Run in No-GUI Mode

If you don't need a display window, the program can still run normally (control commands will be printed to terminal):

```bash
# Program will automatically detect if GUI is available, if not it will continue running without displaying window
python phase3_demo.py --simulation
```

## Check X11 Forwarding

1. **Confirm XQuartz is running** (on Mac)
2. **Check DISPLAY variable**:
   ```bash
   echo $DISPLAY
   # Should show something like: localhost:10.0
   ```
3. **Reconnect SSH**:
   ```bash
   # Disconnect current connection, then reconnect
   exit
   ssh -Y pi@raspberrypi.local
   ```

## Verify Fix

Run test:
```bash
python -c "import cv2; print('OpenCV version:', cv2.__version__); cv2.namedWindow('test')"
```

If successful, the fix is working. If there are still errors, they will be caught and the program will continue running.

## Notes

- Program will automatically catch Qt errors and continue running
- Even if display fails, all control logic still works normally
- Control commands will be printed to terminal (`[SIM] Car Command: ...`)
- You can monitor program status through terminal output

## If Problem Persists

1. Check if XQuartz is running: Open XQuartz application on Mac
2. Restart XQuartz: Completely exit and reopen
3. Check XQuartz settings: Preferences > Security > "Allow connections from network clients"
4. Try different SSH options:
   ```bash
   ssh -X pi@raspberrypi.local  # Untrusted mode (may be more compatible)
   ```

## Temporary Solution: Ignore Display Errors

The program is already configured to continue running even if display fails. You can:
- Ignore Qt error messages
- Monitor program status through terminal output
- Use `--simulation` mode to see all control commands

Display errors will not affect:
- Camera capture
- Person detection
- Obstacle detection
- Vehicle control commands
