"""
User Registration System
Handles user registration and recognition using face recognition
"""
import cv2
import numpy as np
import os
import json
import pickle
from datetime import datetime


class UserRegistration:
    def __init__(self, data_dir=None):
        """
        Initialize user registration system
        
        Args:
            data_dir: Directory to store user data (default: user_data in module directory)
        """
        if data_dir is None:
            # Use user_data directory relative to this module
            module_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(module_dir, "user_data")
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.faces_file = os.path.join(data_dir, "faces_encodings.pkl")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing users
        self.users = self._load_users()
        self.face_encodings = self._load_face_encodings()
        
        # Initialize face detector
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def _load_users(self):
        """Load registered users from file"""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_users(self):
        """Save registered users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _load_face_encodings(self):
        """Load face encodings from file"""
        if os.path.exists(self.faces_file):
            with open(self.faces_file, 'rb') as f:
                return pickle.load(f)
        return {}
    
    def _save_face_encodings(self):
        """Save face encodings to file"""
        with open(self.faces_file, 'wb') as f:
            pickle.dump(self.face_encodings, f)
    
    def detect_face(self, frame):
        """
        Detect face in frame
        
        Args:
            frame: BGR image frame
            
        Returns:
            tuple: (faces, frame_with_rectangles)
                - faces: List of detected face rectangles
                - frame_with_rectangles: Frame with rectangles drawn
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )
        
        frame_with_rectangles = frame.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(frame_with_rectangles, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        return faces, frame_with_rectangles
    
    def register_user(self, name, face_images):
        """
        Register a new user with face images
        
        Args:
            name: User's name
            face_images: List of face image arrays (BGR format)
            
        Returns:
            bool: True if registration successful
        """
        if name in self.users:
            return False  # User already exists
        
        if len(face_images) == 0:
            return False
        
        # Extract face encodings (simplified - using face region as encoding)
        # In production, you'd use a proper face recognition library
        user_id = len(self.users)
        encodings = []
        
        for img in face_images:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )
            
            if len(faces) > 0:
                # Use first detected face
                x, y, w, h = faces[0]
                face_roi = gray[y:y+h, x:x+w]
                # Resize to standard size for encoding
                face_roi = cv2.resize(face_roi, (100, 100))
                encodings.append(face_roi.flatten())
        
        if len(encodings) == 0:
            return False
        
        # Store user data
        self.users[name] = {
            'id': user_id,
            'registered_date': datetime.now().isoformat(),
            'num_samples': len(encodings)
        }
        
        # Store face encodings
        self.face_encodings[name] = encodings
        
        # Save to files
        self._save_users()
        self._save_face_encodings()
        
        return True
    
    def recognize_user(self, frame):
        """
        Recognize user from frame
        
        Args:
            frame: BGR image frame
            
        Returns:
            tuple: (user_name, confidence, frame_with_info)
                - user_name: Name of recognized user or None
                - confidence: Confidence score (0-1)
                - frame_with_info: Frame with recognition info drawn
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )
        
        frame_with_info = frame.copy()
        recognized_name = None
        confidence = 0.0
        
        if len(faces) > 0:
            # Use first detected face
            x, y, w, h = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))
            face_encoding = face_roi.flatten()
            
            # Compare with registered users
            best_match = None
            best_score = float('inf')
            
            for name, encodings in self.face_encodings.items():
                for encoding in encodings:
                    # Calculate distance (simplified L2 distance)
                    distance = np.linalg.norm(face_encoding - encoding)
                    if distance < best_score:
                        best_score = distance
                        best_match = name
            
            # Threshold for recognition (adjust based on testing)
            threshold = 5000  # Lower is better match
            if best_match and best_score < threshold:
                recognized_name = best_match
                confidence = max(0, 1 - (best_score / threshold))
            
            # Draw recognition info
            cv2.rectangle(frame_with_info, (x, y), (x+w, y+h), (0, 255, 0), 2)
            if recognized_name:
                label = f"{recognized_name} ({confidence:.2f})"
                color = (0, 255, 0)
            else:
                label = "Stranger"
                color = (0, 0, 255)
            
            cv2.putText(frame_with_info, label, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        return recognized_name, confidence, frame_with_info
    
    def get_registered_users(self):
        """Get list of registered user names"""
        return list(self.users.keys())
    
    def delete_user(self, name):
        """Delete a registered user"""
        if name in self.users:
            del self.users[name]
            if name in self.face_encodings:
                del self.face_encodings[name]
            self._save_users()
            self._save_face_encodings()
            return True
        return False

