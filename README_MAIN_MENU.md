# Main Menu System - User Registration & Game Selection

The main menu system provides user recognition, registration, and game selection functionality. It acts as the entry point for all three games.

## Features

- **User Recognition**: Automatically recognizes registered users by face
- **User Registration**: Register new users with face samples
- **Stranger Detection**: Identifies unregistered users
- **Personalized Greetings**: 
  - Registered users: "Hello, [Name]!"
  - Strangers: "Hello, Stranger!"
- **Game Selection Menu**: Choose from 3 games
- **Seamless Game Launch**: Launches selected game and returns to menu after

## How It Works

1. **User Detection**: Continuously scans for faces in camera feed
2. **Recognition**: Compares detected face with registered users
3. **Greeting**: 
   - If registered: Displays "Hello, [Name]!"
   - If stranger: Displays "Hello, Stranger!"
4. **Game Selection**: User selects game (1, 2, or 3)
5. **Game Launch**: Selected game launches automatically

## Usage

### Starting the Main Menu

```bash
python main_menu.py
```

### Registering a New User

1. When you see "Hello, Stranger!", press **'r'** to register
2. Enter your name when prompted
3. Look at the camera
4. Press **SPACE** to capture face samples (need at least 5)
5. Press **ENTER** when done
6. You're now registered!

### Selecting a Game

- **'1'**: Rock-Paper-Scissors Game
- **'2'**: Air Drawing
- **'3'**: 1v1 Shooting Game
- **'r'**: Register new user (only shown for strangers)
- **'q'**: Quit

## User Data Storage

- User data is stored in `user_data/` directory
- `users.json`: User information (name, registration date, etc.)
- `faces_encodings.pkl`: Face encodings for recognition

## Recognition System

The system uses OpenCV's Haar Cascade for face detection and a simplified face encoding system for recognition. For production use, consider upgrading to:
- `face_recognition` library (dlib-based)
- Deep learning face recognition models

## Troubleshooting

### Face not detected during registration
- Ensure good lighting
- Face the camera directly
- Remove obstructions (glasses, masks, etc.)
- Keep face centered in frame

### User not recognized
- Make sure you're registered
- Try re-registering with better lighting
- Ensure face is clearly visible
- Recognition works best with consistent lighting conditions

### Games not launching
- Make sure all project directories exist (project-1, project-2, project-3)
- Check that game dependencies are installed
- Verify camera is working

## Future Enhancements

- Voice greetings ("Hello, [Name]!" spoken aloud)
- Multiple user profiles
- User statistics and game history
- Improved face recognition accuracy
- Touch screen support for game selection
- User authentication with passwords

