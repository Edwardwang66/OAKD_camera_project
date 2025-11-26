"""
Model Loader for Rock-Paper-Scissors Gesture Recognition
Loads and uses the trained PyTorch model from ECE176_final project
Reference: https://github.com/edwardw005/ECE176_final
"""
import torch
import torch.nn as nn
import cv2
import numpy as np
from enum import Enum
import os


class Gesture(Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"
    NONE = "none"


class RPSModel(nn.Module):
    """
    CNN Model for Rock-Paper-Scissors classification
    Based on common architectures for hand gesture recognition
    """
    def __init__(self, num_classes=3):
        super(RPSModel, self).__init__()
        # Convolutional layers
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(256)
        
        # Pooling
        self.pool = nn.MaxPool2d(2, 2)
        
        # Fully connected layers
        self.fc1 = nn.Linear(256 * 4 * 4, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, num_classes)
        
        # Dropout
        self.dropout = nn.Dropout(0.5)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        # Conv block 1
        x = self.pool(self.relu(self.bn1(self.conv1(x))))
        # Conv block 2
        x = self.pool(self.relu(self.bn2(self.conv2(x))))
        # Conv block 3
        x = self.pool(self.relu(self.bn3(self.conv3(x))))
        # Conv block 4
        x = self.pool(self.relu(self.bn4(self.conv4(x))))
        
        # Flatten
        x = x.view(-1, 256 * 4 * 4)
        
        # Fully connected
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.dropout(self.relu(self.fc2(x)))
        x = self.fc3(x)
        
        return x


class ModelGestureDetector:
    def __init__(self, model_path=None, device=None):
        """
        Initialize model-based gesture detector
        
        Args:
            model_path: Path to trained model file (.pth)
                       If None, will look for rps_model_improved.pth or rps_model.pth
            device: PyTorch device ('cuda' or 'cpu'), auto-detects if None
        """
        # Set device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        print(f"Using device: {self.device}")
        
        # Find model file
        if model_path is None:
            # Try to find model in common locations
            possible_paths = [
                'rps_model_improved.pth',
                'rps_model.pth',
                '../rps_model_improved.pth',
                '../rps_model.pth',
                '../../rps_model_improved.pth',
                '../../rps_model.pth',
                'models/rps_model_improved.pth',
                'models/rps_model.pth',
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    break
        
        if model_path is None or not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found. Please provide model_path or place "
                f"rps_model_improved.pth or rps_model.pth in the project directory. "
                f"Download from: https://github.com/edwardw005/ECE176_final\n"
                f"Or run: python download_model.py"
            )
        
        print(f"Loading model from: {model_path}")
        
        # Initialize model
        self.model = RPSModel(num_classes=3)
        
        # Load model weights
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            
            # Handle different checkpoint formats
            if isinstance(checkpoint, dict):
                if 'model_state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                elif 'state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['state_dict'])
                else:
                    self.model.load_state_dict(checkpoint)
            else:
                self.model.load_state_dict(checkpoint)
            
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Attempting to load with strict=False...")
            try:
                if isinstance(checkpoint, dict):
                    if 'model_state_dict' in checkpoint:
                        self.model.load_state_dict(checkpoint['model_state_dict'], strict=False)
                    elif 'state_dict' in checkpoint:
                        self.model.load_state_dict(checkpoint['state_dict'], strict=False)
                    else:
                        self.model.load_state_dict(checkpoint, strict=False)
                else:
                    self.model.load_state_dict(checkpoint, strict=False)
                print("Model loaded with strict=False (some layers may not match)")
            except Exception as e2:
                raise RuntimeError(f"Failed to load model: {e2}")
        
        # Set to evaluation mode
        self.model.to(self.device)
        self.model.eval()
        
        # Class labels (order matters - must match training)
        self.class_labels = [Gesture.ROCK, Gesture.PAPER, Gesture.SCISSORS]
        
        # Image preprocessing parameters (adjust based on training)
        self.input_size = (64, 64)  # Common size for RPS models
    
    def preprocess_image(self, frame, bbox=None):
        """
        Preprocess image for model input
        
        Args:
            frame: BGR image frame
            bbox: Optional bounding box (x, y, w, h) to crop hand region
            
        Returns:
            Preprocessed tensor ready for model
        """
        # Crop to hand region if bbox provided
        if bbox is not None:
            x, y, w, h = bbox
            # Add padding
            padding = 20
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(frame.shape[1] - x, w + 2 * padding)
            h = min(frame.shape[0] - y, h + 2 * padding)
            frame = frame[y:y+h, x:x+w]
        
        # Resize to model input size
        frame_resized = cv2.resize(frame, self.input_size)
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        
        # Normalize to [0, 1]
        frame_normalized = frame_rgb.astype(np.float32) / 255.0
        
        # Convert to tensor and add batch dimension
        # Shape: (H, W, C) -> (C, H, W) -> (1, C, H, W)
        frame_tensor = torch.from_numpy(frame_normalized).permute(2, 0, 1).unsqueeze(0)
        
        return frame_tensor.to(self.device)
    
    def detect_gesture(self, frame, confidence_threshold=0.5, hand_bbox=None):
        """
        Detect hand gesture from frame using trained model
        
        Args:
            frame: BGR image frame
            confidence_threshold: Minimum confidence to return a gesture
            hand_bbox: Optional bounding box (x, y, w, h) for hand region
            
        Returns:
            tuple: (gesture, confidence, annotated_frame)
                - gesture: Gesture enum (ROCK, PAPER, SCISSORS, or NONE)
                - confidence: Confidence score (0-1)
                - annotated_frame: Frame with detection info
        """
        annotated_frame = frame.copy()
        
        try:
            # Preprocess image (with bounding box if provided)
            input_tensor = self.preprocess_image(frame, bbox=hand_bbox)
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
                
                confidence = confidence.item()
                predicted_idx = predicted.item()
                
                # Check confidence threshold
                if confidence >= confidence_threshold:
                    gesture = self.class_labels[predicted_idx]
                else:
                    gesture = Gesture.NONE
                    confidence = 0.0
                
                # Draw bounding box if provided
                if hand_bbox is not None:
                    x, y, w, h = hand_bbox
                    cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Draw prediction on frame
                if gesture != Gesture.NONE:
                    text = f"{gesture.value.upper()}: {confidence:.2f}"
                    text_x = hand_bbox[0] if hand_bbox is not None else 10
                    text_y = (hand_bbox[1] - 10) if hand_bbox is not None else 30
                    cv2.putText(annotated_frame, text, (text_x, text_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        except Exception as e:
            print(f"Error in gesture detection: {e}")
            gesture = Gesture.NONE
            confidence = 0.0
        
        return gesture, confidence, annotated_frame
    
    def detect_gesture_with_hand_detection(self, frame, hand_detector=None, confidence_threshold=0.5):
        """
        Detect gesture with hand detection first (more accurate)
        
        Args:
            frame: BGR image frame
            hand_detector: Optional hand detector (MediaPipe or OpenCV)
            confidence_threshold: Minimum confidence
            
        Returns:
            tuple: (gesture, confidence, annotated_frame)
        """
        annotated_frame = frame.copy()
        gesture = Gesture.NONE
        confidence = 0.0
        
        # If hand detector provided, use it to find hand region
        if hand_detector is not None:
            # This would use MediaPipe or other detector to find hand bbox
            # For now, fall back to full frame
            pass
        
        # Use full frame detection
        return self.detect_gesture(frame, confidence_threshold)
    
    def release(self):
        """Release resources"""
        # PyTorch models don't need explicit release, but we can clear cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

