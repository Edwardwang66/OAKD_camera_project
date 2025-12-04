# Quick Fix Guide

## 🚨 Immediate Solution (Recommended)

**Use `--no-gui` option to avoid all display issues**:

```bash
cd phase3
python phase3_demo.py --simulation --no-gui
```

This will:
- ✅ Run all functionality normally
- ✅ All output displayed in terminal
- ✅ Control commands will be printed (`[SIM] Car Command: ...`)
- ✅ Will not crash due to Qt errors
- ❌ No OpenCV window display (but all functionality is normal)

---

## Problem 1: Qt Display Error Causing Program Crash

If you see:
```
qt.qpa.plugin: Could not find the Qt platform plugin "offscreen"
Aborted
```

### Solution: Disable GUI (Simplest)

Use the `--no-gui` parameter to run the program, completely skipping display:

```bash
python phase3_demo.py --simulation --no-gui
```

This will:
- ✅ Run all functionality normally (person detection, obstacle detection, vehicle control)
- ✅ All output displayed in terminal
- ✅ Control commands will be printed (`[SIM] Car Command: ...`)
- ❌ No OpenCV window display (but all functionality is normal)

### Or Use Script

```bash
chmod +x run_phase3_no_gui.sh
./run_phase3_no_gui.sh --simulation
```

## Problem 2: Missing blobconverter (Depth Map Unavailable)

If you see:
```
Warning: blobconverter not available
[OAKDCamera] Depth support: DISABLED
```

### Solution: Install blobconverter

```bash
pip install blobconverter
```

Or if in a virtual environment:
```bash
source env/bin/activate
pip install blobconverter
```

After installation, rerun the program and you should see depth support enabled.

## Quick Start Commands

### No-GUI Mode (Recommended, Avoids All Display Issues)

```bash
cd phase3
python phase3_demo.py --simulation --no-gui
```

### With GUI Mode (If Display Works Normally)

```bash
cd phase3
python phase3_demo.py --simulation
```

## Program Output Description

Even without GUI, the program will still:

1. **Detect person** - Terminal will show status
2. **Detect obstacles** - Terminal will show depth information
3. **Control vehicle** - Control commands will be printed to terminal:
   ```
   [SIM] Car Command: LEFT TURN | Linear: 0.00 m/s, Angular: 0.30 rad/s
   [SIM] Car Command: FORWARD | Linear: 0.50 m/s, Angular: 0.00 rad/s
   ```

4. **Status updates** - Status information printed every 2 seconds

## View Detailed Documentation

- Install blobconverter: `cat INSTALL_BLOBCONVERTER.md`
- Display issue fixes: `cat FIX_DISPLAY_ISSUE.md`
- Phase 3 usage instructions: `cat README_PHASE3.md`
