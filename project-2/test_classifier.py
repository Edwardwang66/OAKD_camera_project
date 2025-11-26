"""
Test script to see what the classifier can detect
Creates test shapes and classifies them
"""
import cv2
import numpy as np
from drawing_classifier import DrawingClassifier, DrawingType


def create_test_shape(shape_type, size=200):
    """Create a test shape on a white canvas"""
    canvas = np.ones((size, size, 3), dtype=np.uint8) * 255
    
    center = (size // 2, size // 2)
    color = (0, 0, 0)  # Black
    
    if shape_type == "circle":
        cv2.circle(canvas, center, size // 3, color, 3)
    
    elif shape_type == "square":
        side = size // 2
        top_left = (center[0] - side // 2, center[1] - side // 2)
        bottom_right = (center[0] + side // 2, center[1] + side // 2)
        cv2.rectangle(canvas, top_left, bottom_right, color, 3)
    
    elif shape_type == "triangle":
        pts = np.array([
            [center[0], center[1] - size // 3],
            [center[0] - size // 3, center[1] + size // 3],
            [center[0] + size // 3, center[1] + size // 3]
        ], np.int32)
        cv2.polylines(canvas, [pts], True, color, 3)
    
    elif shape_type == "line":
        start = (size // 4, center[1])
        end = (3 * size // 4, center[1])
        cv2.line(canvas, start, end, color, 3)
    
    elif shape_type == "heart":
        # Simple heart shape
        # Top curves
        cv2.ellipse(canvas, (center[0] - size // 6, center[1] - size // 6), 
                   (size // 6, size // 6), 0, 0, 180, color, 3)
        cv2.ellipse(canvas, (center[0] + size // 6, center[1] - size // 6), 
                   (size // 6, size // 6), 0, 0, 180, color, 3)
        # Bottom point
        pts = np.array([
            [center[0], center[1] + size // 3],
            [center[0] - size // 4, center[1]],
            [center[0] + size // 4, center[1]]
        ], np.int32)
        cv2.polylines(canvas, [pts], True, color, 3)
    
    return canvas


def test_classifier():
    """Test the classifier on different shapes"""
    print("=" * 60)
    print("Testing Drawing Classifier")
    print("=" * 60)
    
    classifier = DrawingClassifier(use_heuristic=True)
    
    test_shapes = ["circle", "square", "triangle", "line", "heart"]
    
    print("\nTesting shapes:")
    print("-" * 60)
    
    for shape in test_shapes:
        # Create test shape
        canvas = create_test_shape(shape)
        
        # Classify
        detected, confidence = classifier.classify_drawing(canvas)
        
        # Show result
        status = "✓" if detected.value == shape else "✗"
        print(f"{status} {shape:10s} -> {detected.value:10s} (confidence: {confidence:.2f})")
        
        # Show image
        cv2.imshow(f"Test: {shape} -> {detected.value}", canvas)
        cv2.waitKey(500)  # Show for 500ms
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    print("\n" + "=" * 60)
    print("Classification complete!")
    print("\nThe classifier can detect:")
    print("  - CIRCLE: Round shapes (high circularity)")
    print("  - SQUARE: Four-sided shapes (rectangles, squares)")
    print("  - TRIANGLE: Three-sided shapes")
    print("  - LINE: Long, thin shapes")
    print("  - HEART: Heart-shaped drawings (wider at top)")
    print("  - UNKNOWN: Other shapes")
    print("=" * 60)


if __name__ == "__main__":
    test_classifier()

