"""
Simple test script for Phase 1 components
Tests each module individually
"""
import sys
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    try:
        import mediapipe
    except ImportError:
        missing.append("mediapipe")
    
    try:
        import six
    except ImportError:
        missing.append("six")
    
    try:
        import depthai
    except ImportError:
        missing.append("depthai (optional)")
    
    if missing:
        print("\n⚠ Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nTo install dependencies:")
        print("  pip install --user -r requirements.txt")
        print("  or")
        print("  pip install --break-system-packages -r requirements.txt")
        print("  or use a virtual environment (recommended)")
        return False
    
    return True

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    try:
        from phase1_oakd_camera import Phase1OAKDCamera
        print("✓ phase1_oakd_camera imported")
    except Exception as e:
        print(f"✗ phase1_oakd_camera import failed: {e}")
        return False
    
    try:
        from phase1_person_detector import PersonDetector, PersonDetectorFallback
        print("✓ phase1_person_detector imported")
    except Exception as e:
        print(f"✗ phase1_person_detector import failed: {e}")
        return False
    
    try:
        from phase1_rps_game import Phase1RPSGame
        print("✓ phase1_rps_game imported")
    except Exception as e:
        print(f"✗ phase1_rps_game import failed: {e}")
        return False
    
    try:
        from phase1_demo import Phase1Demo
        print("✓ phase1_demo imported")
    except Exception as e:
        print(f"✗ phase1_demo import failed: {e}")
        return False
    
    return True


def test_camera():
    """Test camera initialization"""
    print("\nTesting camera...")
    try:
        from phase1_oakd_camera import Phase1OAKDCamera
        camera = Phase1OAKDCamera()
        print("✓ Camera initialized")
        
        # Try to get a frame
        frame = camera.get_frame()
        if frame is not None:
            print(f"✓ Got frame: {frame.shape}")
        else:
            print("⚠ No frame available (camera may not be connected)")
        
        camera.release()
        return True
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False


def test_person_detector():
    """Test person detector"""
    print("\nTesting person detector...")
    try:
        from phase1_demo import SimplePersonDetector
        detector = SimplePersonDetector()
        print("✓ Person detector initialized")
        detector.release()
        return True
    except Exception as e:
        print(f"✗ Person detector test failed: {e}")
        return False


def test_rps_game():
    """Test RPS game"""
    print("\nTesting RPS game...")
    try:
        from phase1_rps_game import Phase1RPSGame
        # Try with model first, fallback to MediaPipe
        try:
            game = Phase1RPSGame(use_model=True)
            print("✓ RPS game initialized (with model)")
        except:
            game = Phase1RPSGame(use_model=False)
            print("✓ RPS game initialized (MediaPipe fallback)")
        
        game.release()
        return True
    except Exception as e:
        print(f"✗ RPS game test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Phase 1 Component Tests")
    print("=" * 60)
    
    # Check dependencies first
    print("\nChecking dependencies...")
    if not check_dependencies():
        print("\n⚠ Please install missing dependencies before running tests.")
        print("See README.md for installation instructions.")
        return False
    
    print("✓ All dependencies available")
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test camera
    results.append(("Camera", test_camera()))
    
    # Test person detector
    results.append(("Person Detector", test_person_detector()))
    
    # Test RPS game
    results.append(("RPS Game", test_rps_game()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n✓ All tests passed! Phase 1 is ready to use.")
        print("Run: python phase1_demo.py")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        print("\nIf you see 'No module named' errors, install dependencies:")
        print("  pip install --user -r requirements.txt")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

