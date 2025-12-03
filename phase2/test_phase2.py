"""
Test script for Phase 2 components
Tests car controller and follower logic
"""
import sys
import os

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    try:
        from car_controller import CarController
        print("✓ car_controller imported")
    except Exception as e:
        print(f"✗ car_controller import failed: {e}")
        return False
    
    try:
        from person_follower import PersonFollower, SearchController
        print("✓ person_follower imported")
    except Exception as e:
        print(f"✗ person_follower import failed: {e}")
        return False
    
    try:
        from phase2_demo import Phase2Demo
        print("✓ phase2_demo imported")
    except Exception as e:
        print(f"✗ phase2_demo import failed: {e}")
        return False
    
    return True


def test_car_controller():
    """Test car controller"""
    print("\nTesting car controller...")
    try:
        from car_controller import CarController
        car = CarController(use_donkeycar=False)  # Use simulation mode
        print("✓ Car controller initialized (simulation mode)")
        
        # Test velocity control
        car.set_velocity(0.5, 0.3)
        print("✓ Velocity control test passed")
        
        # Test motor control
        car.set_motor(0.3, 0.3)
        print("✓ Motor control test passed")
        
        # Test stop
        car.stop()
        print("✓ Stop test passed")
        
        car.release()
        return True
    except Exception as e:
        print(f"✗ Car controller test failed: {e}")
        return False


def test_person_follower():
    """Test person follower logic"""
    print("\nTesting person follower...")
    try:
        from person_follower import PersonFollower, SearchController
        
        follower = PersonFollower(target_distance=1.0)
        print("✓ Person follower initialized")
        
        # Test with person detected
        person_bbox = (100, 100, 300, 400)  # (x_min, y_min, x_max, y_max)
        image_width = 640
        distance = 2.0
        
        control = follower.compute_control(person_bbox, image_width, distance)
        print(f"✓ Control computed: linear={control['linear']:.2f}, angular={control['angular']:.2f}")
        
        # Test search controller
        searcher = SearchController()
        search_control = searcher.compute_control()
        print(f"✓ Search control: linear={search_control['linear']:.2f}, angular={search_control['angular']:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Person follower test failed: {e}")
        return False


def test_state_machine():
    """Test state machine logic"""
    print("\nTesting state machine...")
    try:
        from person_follower import PersonFollower
        
        follower = PersonFollower(target_distance=1.0)
        
        # Test ready for interaction
        person_bbox = (300, 100, 340, 400)  # Centered
        image_width = 640
        distance = 1.0  # At target distance
        
        ready = follower.is_ready_for_interaction(person_bbox, image_width, distance)
        print(f"✓ Ready check: {ready}")
        
        return True
    except Exception as e:
        print(f"✗ State machine test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Phase 2 Component Tests")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test car controller
    results.append(("Car Controller", test_car_controller()))
    
    # Test person follower
    results.append(("Person Follower", test_person_follower()))
    
    # Test state machine
    results.append(("State Machine", test_state_machine()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n✓ All tests passed! Phase 2 is ready to use.")
        print("Run: python phase2_demo.py")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

