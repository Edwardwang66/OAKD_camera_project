# OAKD Camera Projects

This repository contains multiple OpenCV-based projects using the OAKD Lite camera for the Raspberry Pi 5 Donkey Car setup with a 7-inch screen.

## 🎮 Main Menu System

**Start here!** The main menu system provides user recognition, registration, and game selection.

**Quick Start:**
```bash
python main_menu.py
```

**Features:**
- **User Recognition**: Automatically recognizes registered users
- **User Registration**: Register new users with face samples
- **Personalized Greetings**: 
  - Registered users: "Hello, [Name]!"
  - Strangers: "Hello, Stranger! What game do you want to play?"
- **Game Selection**: Choose from 3 games (1, 2, or 3)

See [README_MAIN_MENU.md](README_MAIN_MENU.md) for detailed documentation.

## Projects

### Project 1: Rock-Paper-Scissors Game
A real-time rock-paper-scissors game that detects hand gestures (rock, paper, or scissors) and plays against an AI opponent (Donkey Car).

**Location**: `project-1/`

**Features**:
- Hand gesture recognition using MediaPipe
- Real-time game with AI opponent
- Score tracking
- UI optimized for 7-inch screen

**Quick Start**:
```bash
cd project-1
pip install -r requirements-laptop.txt  # For laptop testing
python test_laptop.py  # Test on laptop
python main.py  # Run full game
```

### Project 2: Air Drawing
An air drawing application that tracks your index finger and visualizes the drawing on screen in real-time.

**Location**: `project-2/`

**Features**:
- Index finger tracking
- Real-time drawing visualization
- Multiple colors and brush sizes
- Split-screen display (camera + canvas)

**Quick Start**:
```bash
cd project-2
pip install opencv-python mediapipe numpy  # For laptop testing
python main.py
```

### Project 3: 1v1 Shooting Game - Car as Referee
A gesture-based shooting game where two players face off using "pistol gestures" to shoot each other. The car acts as a referee, detecting shots and determining hits.

**Location**: `project-3/`

**Features**:
- Pistol gesture detection (index finger + thumb up)
- Two-player tracking
- Shooting direction detection
- Hit detection and health system
- Referee display with win announcements

**Quick Start**:
```bash
cd project-3
pip install opencv-python mediapipe numpy  # For laptop testing
python test_laptop.py  # Test pistol detection
python main.py  # Run full game
```

## Hardware Setup

- **Raspberry Pi 5**
- **OAKD Lite Camera** (USB connected)
- **7-inch Display** (800x480 recommended, optional)
- **Donkey Car** setup

## Software Requirements

Both projects require:
- Python 3.8+
- OpenCV
- MediaPipe
- NumPy
- DepthAI (for OAKD camera, optional for laptop testing)
- PyTorch (for model-based gesture detection in Project 1)

## Installation on Raspberry Pi 5

### 1. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install OpenCV dependencies
sudo apt install libopencv-dev python3-opencv -y

# Install other dependencies
sudo apt install libusb-1.0-0 libgl1-mesa-glx libglib2.0-0 -y
```

### 2. Install DepthAI for OAKD Lite Camera

```bash
# Install DepthAI
python3 -m pip install depthai

# Verify OAKD camera is detected
python3 -c "import depthai as dai; devices = dai.Device.getAllAvailableDevices(); print(f'Found {len(devices)} device(s)')"
```

### 3. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements-pi.txt

# Note: PyTorch for ARM may need special installation
# For Raspberry Pi, you may need to:
# 1. Use pre-built wheels from: https://github.com/KumaTea/pytorch-aarch64
# 2. Or build from source (takes several hours)
```

### 4. Install PyTorch for Raspberry Pi (ARM)

PyTorch installation on Raspberry Pi requires special handling:

```bash
# Option 1: Use pre-built wheels (recommended)
# Visit: https://github.com/KumaTea/pytorch-aarch64
# Download appropriate wheel for your Python version

# Option 2: Install via pip (if available for your architecture)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Option 3: Build from source (advanced, takes hours)
# Follow: https://pytorch.org/get-started/locally/
```

## Running Without Raspberry Pi Screen (SSH + X11 Forwarding)

If your Raspberry Pi does NOT have a screen attached, you can run the project via SSH with X11 forwarding to display OpenCV windows on your Mac.

### Mac Setup

1. **Install XQuartz**:
   ```bash
   brew install --cask xquartz
   ```

2. **Configure XQuartz**:
   - Open XQuartz (Applications > Utilities > XQuartz)
   - Go to XQuartz > Preferences > Security
   - Check "Allow connections from network clients"
   - Restart XQuartz

3. **Set DISPLAY variable** (if needed):
   ```bash
   export DISPLAY=:0
   ```

### SSH Connection with X11 Forwarding

Connect to your Raspberry Pi with X11 forwarding enabled:

```bash
# Option 1: Trusted X11 forwarding (recommended, faster)
ssh -Y pi@raspberrypi.local

# Option 2: Untrusted X11 forwarding
ssh -X pi@raspberrypi.local
```

**Note**: Replace `raspberrypi.local` with your Pi's IP address or hostname if needed.

### Running the Project

Once connected via SSH with X11 forwarding:

```bash
# Navigate to project directory
cd OAKD_camera_project

# Activate virtual environment (if using one)
source venv/bin/activate

# Run the main menu
python main_menu.py
```

The OpenCV windows will appear on your Mac via X11 forwarding.

### Troubleshooting

**Issue: "could not connect to display" or "No display"**
- **Solution**: Make sure XQuartz is running on your Mac before connecting via SSH
- **Solution**: Verify X11 forwarding is enabled: `echo $DISPLAY` should show a value
- **Solution**: Try restarting XQuartz and reconnecting

**Issue: "X11 connection rejected"**
- **Solution**: In XQuartz, enable "Allow connections from network clients" in Preferences > Security
- **Solution**: Restart XQuartz after changing settings

**Issue: Low FPS or slow performance**
- **Solution**: Reduce camera resolution in camera initialization code
- **Solution**: Use `-X` instead of `-Y` for untrusted forwarding (may be slower but more secure)
- **Solution**: Consider using a wired network connection instead of WiFi

**Issue: GUI not available warning**
- This is normal if X11 forwarding is not set up
- The application will still run and process camera data
- To enable GUI, follow the SSH + X11 setup instructions above

### Headless Mode (No GUI)

The project is designed to work in headless mode. If GUI is not available:
- Camera processing continues normally
- All game logic works
- Only the visual display is skipped
- You'll see a warning message but the app won't crash

## Testing on Laptop

Both projects can be tested on your laptop using a regular webcam:

1. Install minimal dependencies (no DepthAI needed)
2. Run the test scripts
3. The applications will automatically use your webcam

See individual project READMEs for detailed instructions.

## Headless Mode Support

All scripts are designed to work in headless environments (no display):

- **GUI Available**: OpenCV windows display normally
- **GUI Not Available**: Application continues running, skips window display
- **Automatic Detection**: Scripts automatically detect GUI availability
- **No Crashes**: Applications gracefully handle missing GUI

This makes it easy to:
- Run via SSH without X11 forwarding
- Deploy on headless servers
- Test camera functionality without display

## Project Structure

```
OAKD_camera_project/
├── main_menu.py        # Main menu system (START HERE)
├── user_registration.py  # User registration & recognition
├── game_menu.py        # Game selection menu
├── registration_ui.py  # Registration UI
├── camera.py           # Shared camera interface
├── project-1/          # Rock-Paper-Scissors Game
│   ├── main.py
│   ├── hand_gesture_detector.py
│   ├── game_logic.py
│   ├── oakd_camera.py
│   ├── ui_display.py
│   └── ...
├── project-2/          # Air Drawing
│   ├── main.py
│   ├── finger_tracker.py
│   ├── drawing_canvas.py
│   ├── camera.py
│   ├── ui_display.py
│   └── ...
├── project-3/          # 1v1 Shooting Game
│   ├── main.py
│   ├── pistol_detector.py
│   ├── game_logic.py
│   ├── camera.py
│   ├── ui_display.py
│   └── ...
├── user_data/          # User registration data (created automatically)
├── requirements.txt    # Root dependencies
├── README.md           # This file
└── README_MAIN_MENU.md # Main menu documentation
```

## License

MIT License - see LICENSE file for details
