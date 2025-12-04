# Human Detection and User Registration

This module handles user registration and recognition using face detection and recognition.

## Features

- **Face Detection**: Detects faces in camera frames using OpenCV's Haar Cascade
- **User Registration**: Registers new users by collecting face samples
- **User Recognition**: Recognizes registered users from camera frames
- **Visual Feedback**: Provides UI for registration process with progress indicators

## Files

- `user_registration.py` - Main user registration and recognition system
- `registration_ui.py` - UI components for registration display
- `user_data/` - Directory storing registered user data
  - `users.json` - User metadata (names, registration dates, etc.)
  - `faces_encodings.pkl` - Face encodings for recognition

## Usage

### Basic Usage

```python
from human_detection.user_registration import UserRegistration
from human_detection.registration_ui import RegistrationUI

# Initialize registration system
registration = UserRegistration()
reg_ui = RegistrationUI(screen_width=800, screen_height=480)

# Detect face in frame
faces, frame_with_faces = registration.detect_face(frame)

# Register a new user
samples = [frame1, frame2, frame3, ...]  # List of face images
success = registration.register_user("John", samples)

# Recognize user
user_name, confidence, annotated_frame = registration.recognize_user(frame)
```

### Registration Process

1. Collect face samples from camera frames
2. Extract face encodings from samples
3. Store user data and encodings
4. Save to `user_data/` directory

### Recognition Process

1. Detect face in current frame
2. Extract face encoding
3. Compare with registered user encodings
4. Return best match if confidence threshold is met

## User Data Storage

User data is stored in the `user_data/` directory:
- `users.json`: Contains user metadata (name, ID, registration date, sample count)
- `faces_encodings.pkl`: Contains face encodings for each registered user

## Integration

This module is integrated into the main menu system (`main_menu.py`) to:
- Recognize users when they approach the camera
- Allow new user registration
- Display user status during interaction

## Dependencies

- OpenCV (`cv2`) - For face detection and image processing
- NumPy - For array operations
- Standard library: `os`, `json`, `pickle`, `datetime`

## Notes

- Uses simplified face encoding (grayscale face region)
- For production use, consider integrating a proper face recognition library (e.g., `face_recognition`)
- Recognition threshold can be adjusted based on testing
- Minimum 3-5 face samples recommended for reliable recognition

