"""
Simple Drawing Classifier
Uses a lightweight CNN model to classify what is being drawn
"""
import torch
import torch.nn as nn
import cv2
import numpy as np
from enum import Enum


class DrawingType(Enum):
    CIRCLE = "circle"
    LINE = "line"
    SQUARE = "square"
    TRIANGLE = "triangle"
    HEART = "heart"
    UNKNOWN = "unknown"


class SimpleDrawingClassifier(nn.Module):
    """
    Lightweight CNN for drawing classification
    """
    def __init__(self, num_classes=6):
        super(SimpleDrawingClassifier, self).__init__()
        # Small CNN architecture
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.3)
        
        # Calculate flattened size (assuming 64x64 input -> 8x8 after 3 pools)
        self.fc1 = nn.Linear(64 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, num_classes)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = self.pool(self.relu(self.conv3(x)))
        
        x = x.view(-1, 64 * 8 * 8)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.fc2(x)
        return x


class DrawingClassifier:
    def __init__(self, model_path=None, use_heuristic=True):
        """
        Initialize drawing classifier
        
        Args:
            model_path: Path to trained model (optional)
            use_heuristic: If True, use heuristic-based detection when model not available
        """
        self.use_heuristic = use_heuristic
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        
        if model_path:
            try:
                self.model = SimpleDrawingClassifier(num_classes=6)
                checkpoint = torch.load(model_path, map_location=self.device)
                if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    self.model.load_state_dict(checkpoint)
                self.model.to(self.device)
                self.model.eval()
                print("Drawing classifier model loaded!")
            except Exception as e:
                print(f"Could not load model: {e}, using heuristic method")
                self.model = None
                self.use_heuristic = True
    
    def classify_drawing(self, canvas):
        """
        Classify what is drawn on the canvas
        
        Args:
            canvas: Canvas image (BGR format)
            
        Returns:
            tuple: (drawing_type, confidence)
        """
        if self.model is not None:
            return self._classify_with_model(canvas)
        elif self.use_heuristic:
            return self._classify_with_heuristic(canvas)
        else:
            return DrawingType.UNKNOWN, 0.0
    
    def _classify_with_model(self, canvas):
        """Classify using trained model"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
            
            # Resize to 64x64
            resized = cv2.resize(gray, (64, 64))
            
            # Normalize
            normalized = resized.astype(np.float32) / 255.0
            
            # Convert to tensor
            tensor = torch.from_numpy(normalized).unsqueeze(0).unsqueeze(0).to(self.device)
            
            # Predict
            with torch.no_grad():
                outputs = self.model(tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
                
                class_idx = predicted.item()
                confidence = confidence.item()
                
                # Map to enum
                classes = [
                    DrawingType.CIRCLE,
                    DrawingType.LINE,
                    DrawingType.SQUARE,
                    DrawingType.TRIANGLE,
                    DrawingType.HEART,
                    DrawingType.UNKNOWN
                ]
                
                if class_idx < len(classes):
                    return classes[class_idx], confidence
                else:
                    return DrawingType.UNKNOWN, confidence
        except Exception as e:
            print(f"Model classification error: {e}")
            return self._classify_with_heuristic(canvas)
    
    def _classify_with_heuristic(self, canvas):
        """
        Heuristic-based drawing classification
        Uses contour analysis and geometric properties
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
            
            # Threshold to get drawing (non-white pixels)
            _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) == 0:
                return DrawingType.UNKNOWN, 0.0
            
            # Get largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            if area < 100:  # Too small
                return DrawingType.UNKNOWN, 0.0
            
            # Approximate contour
            epsilon = 0.02 * cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, epsilon, True)
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(largest_contour)
            aspect_ratio = float(w) / h if h > 0 else 0
            
            # Get convex hull
            hull = cv2.convexHull(largest_contour)
            hull_area = cv2.contourArea(hull)
            solidity = float(area) / hull_area if hull_area > 0 else 0
            
            # Classification logic - check in order of specificity
            num_vertices = len(approx)
            perimeter = cv2.arcLength(largest_contour, True)
            
            # Line detection (most specific - check first)
            if num_vertices == 2 or (aspect_ratio > 5 or aspect_ratio < 0.2):
                # Additional check: very elongated shape
                if perimeter > 0:
                    extent = area / (w * h) if (w * h) > 0 else 0
                    if extent < 0.3:  # Line is thin
                        return DrawingType.LINE, 0.8
                return DrawingType.LINE, 0.7
            
            # Triangle detection (very specific - 3 vertices)
            if num_vertices == 3:
                # Check if it's actually triangular (not just 3 points)
                if solidity > 0.85:
                    return DrawingType.TRIANGLE, 0.85
            
            # Square detection (4 vertices)
            if num_vertices == 4:
                # Check if roughly square
                if 0.8 < aspect_ratio < 1.2 and solidity > 0.9:
                    return DrawingType.SQUARE, 0.85
                # Could be rectangle
                elif 0.5 < aspect_ratio < 2.0 and solidity > 0.85:
                    return DrawingType.SQUARE, 0.7  # Treat rectangle as square variant
            
            # Circle detection (many vertices, high circularity)
            if num_vertices >= 8:
                # Check circularity
                circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                if circularity > 0.75:
                    return DrawingType.CIRCLE, 0.85
                elif circularity > 0.6:
                    return DrawingType.CIRCLE, 0.7  # Oval/ellipse
            
            # Heart detection (more specific checks)
            if num_vertices >= 6 and num_vertices <= 12:
                # Heart has specific characteristics:
                # 1. Wider at top than bottom
                # 2. Two rounded lobes at top
                # 3. Pointed at bottom
                moments = cv2.moments(largest_contour)
                if moments['m00'] != 0:
                    cx = int(moments['m10'] / moments['m00'])
                    cy = int(moments['m01'] / moments['m00'])
                    
                    # Split contour into top and bottom halves
                    top_points = [pt[0] for pt in largest_contour if pt[0][1] < cy]
                    bottom_points = [pt[0] for pt in largest_contour if pt[0][1] > cy]
                    
                    if len(top_points) > 3 and len(bottom_points) > 3:
                        top_width = max([p[0] for p in top_points]) - min([p[0] for p in top_points])
                        bottom_width = max([p[0] for p in bottom_points]) - min([p[0] for p in bottom_points])
                        
                        # Heart should be wider at top
                        if top_width > bottom_width * 1.5:
                            # Check for two peaks at top (heart characteristic)
                            top_y_coords = [p[1] for p in top_points]
                            if len(top_y_coords) > 0:
                                min_top_y = min(top_y_coords)
                                # Count peaks (local minima in y)
                                peaks = 0
                                sorted_top = sorted(top_points, key=lambda p: p[0])
                                for i in range(1, len(sorted_top) - 1):
                                    if sorted_top[i][1] < sorted_top[i-1][1] and sorted_top[i][1] < sorted_top[i+1][1]:
                                        peaks += 1
                                
                                # Heart typically has 2 peaks at top
                                if peaks >= 1:  # At least one peak
                                    return DrawingType.HEART, 0.65
            
            # If nothing matches, return unknown
            return DrawingType.UNKNOWN, 0.3
        
        except Exception as e:
            print(f"Heuristic classification error: {e}")
            return DrawingType.UNKNOWN, 0.0

