# Quick Start Guide - Testing on Your Laptop

This guide will help you test the rock-paper-scissors game on your laptop before deploying to the Raspberry Pi.

## Step 1: Install Dependencies

Install the required packages (DepthAI is optional for laptop testing):

```bash
pip install -r requirements-laptop.txt
```

Or install the full requirements (DepthAI will fail gracefully if not available):

```bash
pip install opencv-python mediapipe numpy
```

## Step 2: Test Gesture Detection

Run the simple gesture detection test:

```bash
python test_laptop.py
```

**What to expect:**
- A window will open showing your webcam feed
- Show your hand to the camera
- Try making these gestures:
  - **ROCK**: Close your fist (all fingers closed)
  - **PAPER**: Open your hand (all fingers extended)
  - **SCISSORS**: Extend index and middle fingers (like a peace sign)
- The detected gesture will be displayed on screen
- Press 'q' to quit

## Step 3: Test Full Game

Once gesture detection works, test the complete game:

```bash
python test_full_game_laptop.py
```

**What to expect:**
- A window will open with the game interface
- Show your hand to the camera
- **Hold your gesture steady for about 1 second** to play a round
- The game will show:
  - Your choice
  - Donkey Car's (AI) choice
  - The winner
- Scores are tracked at the top
- Press 'q' to quit, 'r' to reset scores

## Troubleshooting

### Webcam not working?
- Make sure no other application is using your webcam
- Try changing the camera ID in the script (0, 1, or 2)
- On macOS, you may need to grant camera permissions

### Gesture not detected?
- Ensure good lighting
- Keep your hand clearly visible
- Make sure only one hand is in the frame
- Hold the gesture steady

### Import errors?
- Make sure you've installed the dependencies: `pip install opencv-python mediapipe numpy`
- Check your Python version (3.8+ required)

## Next Steps

Once everything works on your laptop:
1. Transfer the code to your Raspberry Pi
2. Install full requirements including DepthAI
3. Connect the OAKD camera
4. Run `python main.py` on the Pi

