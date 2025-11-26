# Project 3: 1v1 Shooting Game - Car as Referee

A gesture-based shooting game where two players face off using "pistol gestures" to shoot each other. The car acts as a referee, detecting shots and determining hits.

## Features

- **Pistol Gesture Detection**: Recognizes pistol/gun pointing gestures (index finger extended, thumb up)
- **Two-Player Detection**: Tracks both players simultaneously
- **Shooting Direction Detection**: Determines which player is being targeted
- **Hit Detection**: Automatically detects when a player is hit
- **Health System**: Each player starts with 3 health points
- **Referee Display**: Shows game state, health bars, and hit announcements on 7-inch screen
- **Win Detection**: Automatically determines and announces the winner

## How It Works

1. **Pistol Gesture**: Players make a pistol gesture (index finger extended, thumb up, other fingers closed)
2. **Shooting**: Point the pistol at your opponent (left for Player A, right for Player B)
3. **Hit Detection**: The car detects when:
   - Player A's pistol points right → "Player B hit!"
   - Player B's pistol points left → "Player A hit!"
4. **Health System**: Each hit reduces health by 1
5. **Winner**: First player to lose all health loses, opponent wins!

## Hardware Requirements

- Raspberry Pi 5
- OAKD Lite camera (or webcam for testing)
- 7-inch touchscreen display (800x480 recommended, optional)
- Donkey Car setup

**Note**: The project can run headless via SSH with X11 forwarding. See main README for SSH setup instructions.

## Software Requirements

- Python 3.8+
- OpenCV
- MediaPipe
- DepthAI (for OAKD camera, optional for laptop testing)
- NumPy

## Installation

### For Raspberry Pi (with OAKD camera):

1. Navigate to project directory:
```bash
cd project-3
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure your OAKD Lite camera is connected via USB.

### For Laptop Testing:

1. Navigate to project directory:
```bash
cd project-3
```

2. Install minimal dependencies:
```bash
pip install opencv-python mediapipe numpy
```

3. Your laptop webcam will be used automatically.

## Usage

Run the main application:
```bash
python main.py
```

### Controls

- **'s'**: Start game (when in waiting state)
- **'r'**: Reset game
- **'q'**: Quit application

### How to Play

1. **Position**: Two players stand side by side in front of the camera
   - Player A should be on the left side
   - Player B should be on the right side

2. **Pistol Gesture**: Make a pistol with your hand:
   - Extend your index finger (like pointing)
   - Extend your thumb upward
   - Keep other fingers (middle, ring, pinky) closed

3. **Shoot**: Point your pistol at your opponent:
   - Player A: Point right (toward Player B)
   - Player B: Point left (toward Player A)

4. **Win**: First player to reduce opponent's health to 0 wins!

## Project Structure

```
project-3/
├── main.py              # Main application entry point
├── camera.py            # Camera interface (OAKD or webcam)
├── pistol_detector.py   # Pistol gesture detection and direction
├── game_logic.py        # Game state, health, hits, win conditions
├── ui_display.py        # Referee UI for 7-inch screen
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Game Rules

- Each player starts with 3 health points
- Making a pistol gesture and pointing at opponent causes a hit
- Hit cooldown prevents rapid-fire (must wait between shots)
- First player to lose all health loses
- The car announces: "Player X wins!!!"

## Running on Raspberry Pi via SSH

### Setup X11 Forwarding

1. **On Mac**: Install and configure XQuartz (see main README)
2. **Connect**: `ssh -Y pi@raspberrypi.local`
3. **Run**: `python main.py`

The OpenCV windows will display on your Mac via X11 forwarding.

### Headless Mode

The application automatically detects if GUI is available:
- **GUI Available**: Windows display normally
- **GUI Not Available**: Application continues running, skips window display
- **No Crashes**: Gracefully handles missing GUI

## Troubleshooting

### Pistol gesture not detected
- Ensure good lighting
- Make sure your hand is clearly visible
- Index finger must be extended
- Thumb must be up
- Other fingers must be closed

### Players not detected correctly
- Stand clearly on left (Player A) and right (Player B) sides
- Make sure both players are visible in frame
- Ensure sufficient space between players

### Hits not registering
- Make sure you're pointing in the correct direction
- Player A must point right
- Player B must point left
- Wait for cooldown between shots

### GUI not available warning
- This is normal if X11 forwarding is not set up
- The game will still work, just without visual display
- To enable GUI, follow SSH + X11 setup in main README

## Future Enhancements

- Sound effects for shots and hits
- Text-to-speech announcements ("Player 1 wins!!!")
- Different game modes (time limit, first to X hits)
- Power-ups and special abilities
- Replay system
- Score tracking across multiple rounds

## License

MIT License - see LICENSE file for details

