# Phase 2 Docker Setup

This Docker setup allows you to run Phase 2 demo without Qt/X11 display conflicts.

## Quick Start

### Build and Run

```bash
cd phase2
./run_docker.sh
```

Or manually:

```bash
# Build the image
docker-compose build

# Run in simulation mode
docker-compose run --rm phase2 python phase2/phase2_demo.py --simulation
```

## Usage

### Simulation Mode (Recommended for Testing)

```bash
./run_docker.sh --simulation
```

### With Real Car Control

```bash
./run_docker.sh --no-simulation --vesc-port /dev/ttyACM0
```

### Custom Target Distance

```bash
./run_docker.sh --target-distance 1.5
```

## How It Works

The Docker container:
- Uses `opencv-python-headless` to avoid Qt dependencies
- Sets `QT_QPA_PLATFORM=offscreen` to prevent Qt from trying to use X11
- Runs in privileged mode to access USB devices (OAKD camera)
- Mounts USB devices and serial ports for hardware access

## Benefits

✅ **No Qt/X11 Conflicts**: Runs headless, avoiding all display backend issues  
✅ **Isolated Environment**: Dependencies are contained in the container  
✅ **Consistent Setup**: Same environment across different machines  
✅ **Easy Deployment**: Just build and run  

## Display Options

### Option 1: Headless (No Display)
The container runs without GUI by default. All control logic works, commands are printed to terminal.

### Option 2: X11 Forwarding (If Needed)
If you need display, you can mount X11 socket:

```bash
docker-compose run --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  phase2 python phase2/phase2_demo.py --simulation
```

But this is usually not needed - the program works fine without display.

## Troubleshooting

### OAKD Camera Not Detected

1. **Check USB device permissions**:
   ```bash
   ls -l /dev/bus/usb
   ```

2. **Run with privileged mode** (already enabled in docker-compose.yml):
   ```bash
   docker-compose run --rm --privileged phase2 ...
   ```

3. **Check if camera is connected**:
   ```bash
   lsusb | grep -i oak
   ```

### VESC Not Connecting

1. **Check serial port**:
   ```bash
   ls -l /dev/ttyACM* /dev/ttyUSB*
   ```

2. **Update docker-compose.yml** to include your specific port:
   ```yaml
   devices:
     - /dev/ttyACM0:/dev/ttyACM0  # Your VESC port
   ```

### Build Errors

If build fails, try:
```bash
docker-compose build --no-cache
```

## File Structure

```
phase2/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── run_docker.sh          # Convenience script to run
└── DOCKER_README.md       # This file
```

## Environment Variables

The container sets these automatically:
- `QT_QPA_PLATFORM=offscreen` - Prevents Qt from using X11
- `OPENCV_VIDEOIO_PRIORITY_MSMF=0` - Disables Windows Media Foundation
- `PYTHONUNBUFFERED=1` - Real-time Python output

## Notes

- The container uses `opencv-python-headless` which doesn't include GUI support
- All display operations are handled gracefully (no-op if GUI unavailable)
- Control logic works perfectly without display
- Terminal output shows all status information

