#!/usr/bin/env python3
"""
Test script for AprilTag stability features.

This script validates the pose estimation stability improvements.
"""

import numpy as np
import sys

try:
    import cv2
except ImportError:
    print("Error: OpenCV not installed. Install with: pip install opencv-python")
    sys.exit(1)

try:
    import apriltag
except ImportError:
    print("Error: apriltag not installed. Install with: pip install apriltag")
    sys.exit(1)

from vio import AprilTagDetector


def test_minimum_distance_enforcement():
    """Test that minimum distance is enforced correctly."""
    print("Test 1: Minimum Distance Enforcement")
    print("-" * 60)
    
    camera_matrix = AprilTagDetector.create_default_camera_matrix(640, 480)
    dist_coeffs = np.zeros(5)
    
    # Test default minimum distance (2 × tag_size)
    tag_size = 0.10  # 100mm
    detector = AprilTagDetector(
        tag_size=tag_size,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs
    )
    
    expected_min = 2.0 * tag_size
    if abs(detector.min_distance - expected_min) < 0.001:
        print(f"✓ Default min_distance = 2 × tag_size ({expected_min:.3f}m)")
    else:
        print(f"✗ Expected {expected_min:.3f}m, got {detector.min_distance:.3f}m")
        return False
    
    # Test custom minimum distance
    custom_min = 0.30  # 300mm
    detector2 = AprilTagDetector(
        tag_size=tag_size,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs,
        min_distance=custom_min
    )
    
    if abs(detector2.min_distance - custom_min) < 0.001:
        print(f"✓ Custom min_distance set correctly ({custom_min:.3f}m)")
    else:
        print(f"✗ Expected {custom_min:.3f}m, got {detector2.min_distance:.3f}m")
        return False
    
    print()
    return True


def test_stability_parameters():
    """Test that all stability parameters are stored correctly."""
    print("Test 2: Stability Parameters Storage")
    print("-" * 60)
    
    camera_matrix = AprilTagDetector.create_default_camera_matrix(640, 480)
    dist_coeffs = np.zeros(5)
    
    # Test with custom parameters
    detector = AprilTagDetector(
        tag_size=0.19,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs,
        min_distance=0.40,
        max_reprojection_error=7.5,
        smoothing_alpha=0.25,
        lost_timeout_frames=8
    )
    
    tests = [
        (detector.min_distance, 0.40, "min_distance"),
        (detector.max_reprojection_error, 7.5, "max_reprojection_error"),
        (detector.smoothing_alpha, 0.25, "smoothing_alpha"),
        (detector.lost_timeout_frames, 8, "lost_timeout_frames"),
    ]
    
    all_passed = True
    for actual, expected, name in tests:
        if abs(actual - expected) < 0.001:
            print(f"✓ {name} = {expected}")
        else:
            print(f"✗ {name}: expected {expected}, got {actual}")
            all_passed = False
    
    print()
    return all_passed


def test_tracking_state_initialization():
    """Test that tracking state is initialized correctly."""
    print("Test 3: Tracking State Initialization")
    print("-" * 60)
    
    camera_matrix = AprilTagDetector.create_default_camera_matrix(640, 480)
    dist_coeffs = np.zeros(5)
    
    detector = AprilTagDetector(
        tag_size=0.19,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs
    )
    
    # Check tracking dictionaries are initialized
    if isinstance(detector.previous_poses, dict):
        print("✓ previous_poses initialized as dict")
    else:
        print("✗ previous_poses not a dict")
        return False
    
    if isinstance(detector.tracking_state, dict):
        print("✓ tracking_state initialized as dict")
    else:
        print("✗ tracking_state not a dict")
        return False
    
    # Check they're empty
    if len(detector.previous_poses) == 0:
        print("✓ previous_poses starts empty")
    else:
        print("✗ previous_poses should start empty")
        return False
    
    if len(detector.tracking_state) == 0:
        print("✓ tracking_state starts empty")
    else:
        print("✗ tracking_state should start empty")
        return False
    
    print()
    return True


def test_reset_tracking():
    """Test tracking reset functionality."""
    print("Test 4: Reset Tracking")
    print("-" * 60)
    
    camera_matrix = AprilTagDetector.create_default_camera_matrix(640, 480)
    dist_coeffs = np.zeros(5)
    
    detector = AprilTagDetector(
        tag_size=0.19,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs
    )
    
    # Manually add some tracking data
    detector.previous_poses[42] = (np.array([[0], [0], [1]]), np.array([[0], [0], [0]]))
    detector.previous_poses[99] = (np.array([[1], [0], [1]]), np.array([[0], [0], [0]]))
    detector.tracking_state[42] = 0
    detector.tracking_state[99] = 0
    
    # Test single tag reset
    detector.reset_tracking(tag_id=42)
    
    if 42 not in detector.previous_poses and 42 not in detector.tracking_state:
        print("✓ Single tag reset works (tag 42 removed)")
    else:
        print("✗ Single tag reset failed")
        return False
    
    if 99 in detector.previous_poses and 99 in detector.tracking_state:
        print("✓ Other tags preserved (tag 99 still present)")
    else:
        print("✗ Other tags incorrectly removed")
        return False
    
    # Test full reset
    detector.reset_tracking()
    
    if len(detector.previous_poses) == 0 and len(detector.tracking_state) == 0:
        print("✓ Full reset clears all tracking data")
    else:
        print("✗ Full reset failed")
        return False
    
    print()
    return True


def test_detection_output_format():
    """Test that detections include new stability fields."""
    print("Test 5: Detection Output Format")
    print("-" * 60)
    
    camera_matrix = AprilTagDetector.create_default_camera_matrix(640, 480)
    dist_coeffs = np.zeros(5)
    
    detector = AprilTagDetector(
        tag_size=0.19,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs
    )
    
    # Test with blank image (no detections expected)
    blank_image = np.ones((480, 640, 3), dtype=np.uint8) * 255
    detections = detector.detect(blank_image)
    
    if len(detections) == 0:
        print("✓ Returns empty list for blank image (expected)")
        print("  (Cannot test output format without real AprilTag)")
        print("  Expected fields in detection dict:")
        print("    - tracking_status: str")
        print("    - reprojection_error: float")
        print("  Plus all standard fields from original implementation")
    else:
        # If we somehow got a detection, check the format
        detection = detections[0]
        required_new_fields = ['tracking_status', 'reprojection_error']
        missing = [f for f in required_new_fields if f not in detection]
        
        if len(missing) == 0:
            print("✓ Detection includes new stability fields")
        else:
            print(f"✗ Detection missing fields: {missing}")
            return False
    
    print()
    return True


def test_helper_methods():
    """Test helper methods for stability features."""
    print("Test 6: Helper Methods")
    print("-" * 60)
    
    camera_matrix = AprilTagDetector.create_default_camera_matrix(640, 480)
    dist_coeffs = np.zeros(5)
    
    detector = AprilTagDetector(
        tag_size=0.19,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs
    )
    
    # Test _smooth_pose
    prev_tvec = np.array([[0.0], [0.0], [1.0]])
    new_tvec = np.array([[0.1], [0.0], [1.0]])
    smoothed = detector._smooth_pose(prev_tvec, new_tvec)
    
    # With alpha=0.3, result should be 0.3*new + 0.7*prev
    expected = 0.3 * new_tvec + 0.7 * prev_tvec
    if np.allclose(smoothed, expected):
        print("✓ _smooth_pose applies exponential smoothing correctly")
    else:
        print("✗ _smooth_pose calculation incorrect")
        return False
    
    # Test _smooth_rotation
    prev_rvec = np.array([[0.0], [0.0], [0.0]])
    new_rvec = np.array([[0.1], [0.0], [0.0]])
    smoothed_rot = detector._smooth_rotation(prev_rvec, new_rvec)
    
    expected_rot = 0.3 * new_rvec + 0.7 * prev_rvec
    if np.allclose(smoothed_rot, expected_rot):
        print("✓ _smooth_rotation applies smoothing correctly")
    else:
        print("✗ _smooth_rotation calculation incorrect")
        return False
    
    # Test _rotation_distance
    rvec1 = np.array([[0.0], [0.0], [0.0]])
    rvec2 = np.array([[0.0], [0.0], [0.0]])
    distance = detector._rotation_distance(rvec1, rvec2)
    
    if abs(distance) < 0.001:
        print("✓ _rotation_distance returns 0 for identical rotations")
    else:
        print(f"✗ _rotation_distance should be 0, got {distance}")
        return False
    
    print()
    return True


def test_backward_compatibility():
    """Test that existing API still works (backward compatibility)."""
    print("Test 7: Backward Compatibility")
    print("-" * 60)
    
    camera_matrix = AprilTagDetector.create_default_camera_matrix(640, 480)
    dist_coeffs = np.zeros(5)
    
    # Test initialization without stability parameters (should use defaults)
    try:
        detector = AprilTagDetector(
            tag_size=0.19,
            camera_matrix=camera_matrix,
            dist_coeffs=dist_coeffs
        )
        print("✓ Can initialize without stability parameters")
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False
    
    # Test detect method
    image = np.ones((480, 640, 3), dtype=np.uint8) * 255
    try:
        detections = detector.detect(image)
        print("✓ detect() method works")
    except Exception as e:
        print(f"✗ detect() failed: {e}")
        return False
    
    # Test existing helper methods
    try:
        pose = detector.get_pose_from_tag_id(detections, 42)
        print("✓ get_pose_from_tag_id() still works")
    except Exception as e:
        print(f"✗ get_pose_from_tag_id() failed: {e}")
        return False
    
    # Test visualization
    try:
        vis_image = detector.visualize_detections(image, detections)
        print("✓ visualize_detections() still works")
    except Exception as e:
        print(f"✗ visualize_detections() failed: {e}")
        return False
    
    print()
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("AprilTag Stability Features Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_minimum_distance_enforcement,
        test_stability_parameters,
        test_tracking_state_initialization,
        test_reset_tracking,
        test_detection_output_format,
        test_helper_methods,
        test_backward_compatibility,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All stability features tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
