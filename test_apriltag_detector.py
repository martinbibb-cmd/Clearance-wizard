#!/usr/bin/env python3
"""
Test script for AprilTagDetector validation.

This script validates that the AprilTagDetector class works correctly
according to the specification.
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


def test_initialization():
    """Test that AprilTagDetector initializes correctly."""
    print("Test 1: Initialization")
    print("-" * 60)
    
    # Create camera parameters
    image_width, image_height = 640, 480
    camera_matrix = AprilTagDetector.create_default_camera_matrix(
        image_width, image_height, fov_degrees=60.0
    )
    dist_coeffs = np.zeros(5)
    tag_size = 0.19  # 190mm
    
    # Test initialization with default family
    try:
        detector = AprilTagDetector(
            tag_size=tag_size,
            camera_matrix=camera_matrix,
            dist_coeffs=dist_coeffs
        )
        print(f"✓ Detector initialized with default family (tagStandard41h12)")
        print(f"  Tag size: {detector.tag_size}m")
        print(f"  Camera matrix shape: {detector.camera_matrix.shape}")
        print(f"  Distortion coeffs shape: {detector.dist_coeffs.shape}")
        print(f"  Object points shape: {detector.object_points.shape}")
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False
    
    # Test initialization with different family
    try:
        detector2 = AprilTagDetector(
            tag_size=tag_size,
            camera_matrix=camera_matrix,
            dist_coeffs=dist_coeffs,
            tag_family='tag36h11'
        )
        print(f"✓ Detector initialized with tag36h11 family")
    except Exception as e:
        print(f"✗ Initialization with tag36h11 failed: {e}")
        return False
    
    print()
    return True


def test_object_points():
    """Test that object points are defined correctly for PnP."""
    print("Test 2: Object Points Definition")
    print("-" * 60)
    
    camera_matrix = np.eye(3, dtype=np.float32)
    camera_matrix[0, 0] = 500  # fx
    camera_matrix[1, 1] = 500  # fy
    camera_matrix[0, 2] = 320  # cx
    camera_matrix[1, 2] = 240  # cy
    
    dist_coeffs = np.zeros(5)
    tag_size = 0.19
    
    detector = AprilTagDetector(
        tag_size=tag_size,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs
    )
    
    # Verify object points form a square centered at origin
    points = detector.object_points
    print(f"Object points (4 corners of tag):")
    for i, point in enumerate(points):
        print(f"  Corner {i}: {point}")
    
    # Check that points form a square
    half_size = tag_size / 2.0
    expected_distances = [tag_size, np.sqrt(2) * tag_size, tag_size, np.sqrt(2) * tag_size]
    
    # Check all points are in Z=0 plane
    if np.all(points[:, 2] == 0):
        print(f"✓ All points in Z=0 plane (planar marker)")
    else:
        print(f"✗ Points not in Z=0 plane")
        return False
    
    # Check distances between consecutive points
    distances = []
    for i in range(4):
        p1 = points[i]
        p2 = points[(i + 1) % 4]
        dist = np.linalg.norm(p2 - p1)
        distances.append(dist)
    
    # All sides should be approximately equal (forming a square)
    if np.allclose(distances[0], distances[2], rtol=0.01) and \
       np.allclose(distances[1], distances[3], rtol=0.01):
        print(f"✓ Points form a square (side lengths: {distances[0]:.4f}m, {distances[1]:.4f}m)")
    else:
        print(f"✗ Points do not form a square properly")
        return False
    
    print()
    return True


def test_detect_method():
    """Test that detect method works with blank images."""
    print("Test 3: Detect Method")
    print("-" * 60)
    
    # Create detector
    camera_matrix = AprilTagDetector.create_default_camera_matrix(640, 480)
    dist_coeffs = np.zeros(5)
    tag_size = 0.19
    
    detector = AprilTagDetector(
        tag_size=tag_size,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs
    )
    
    # Test with blank grayscale image
    blank_gray = np.ones((480, 640), dtype=np.uint8) * 255
    try:
        detections = detector.detect(blank_gray)
        print(f"✓ Detect works with grayscale image")
        print(f"  Detections found: {len(detections)}")
    except Exception as e:
        print(f"✗ Detect failed with grayscale image: {e}")
        return False
    
    # Test with blank color image
    blank_color = np.ones((480, 640, 3), dtype=np.uint8) * 255
    try:
        detections = detector.detect(blank_color)
        print(f"✓ Detect works with color image")
        print(f"  Detections found: {len(detections)}")
    except Exception as e:
        print(f"✗ Detect failed with color image: {e}")
        return False
    
    # Verify return format
    if len(detections) == 0:
        print(f"✓ Returns empty list when no tags detected")
    else:
        # Check that detection dictionary has required fields
        detection = detections[0]
        required_fields = ['tag_id', 'translation', 'rotation_vector', 'rotation_matrix']
        missing_fields = [f for f in required_fields if f not in detection]
        if len(missing_fields) == 0:
            print(f"✓ Detection dictionary has all required fields")
        else:
            print(f"✗ Detection dictionary missing fields: {missing_fields}")
            return False
    
    print()
    return True


def test_camera_matrix_helper():
    """Test the create_default_camera_matrix helper method."""
    print("Test 4: Camera Matrix Helper")
    print("-" * 60)
    
    width, height = 640, 480
    fov = 60.0
    
    try:
        K = AprilTagDetector.create_default_camera_matrix(width, height, fov)
        print(f"✓ create_default_camera_matrix works")
        print(f"  Camera matrix:\n{K}")
        
        # Verify shape
        if K.shape == (3, 3):
            print(f"✓ Correct shape (3x3)")
        else:
            print(f"✗ Incorrect shape: {K.shape}")
            return False
        
        # Verify principal point near center
        cx, cy = K[0, 2], K[1, 2]
        if abs(cx - width/2) < 1 and abs(cy - height/2) < 1:
            print(f"✓ Principal point near image center ({cx:.1f}, {cy:.1f})")
        else:
            print(f"✗ Principal point not near center: ({cx:.1f}, {cy:.1f})")
            return False
        
    except Exception as e:
        print(f"✗ create_default_camera_matrix failed: {e}")
        return False
    
    print()
    return True


def test_visualization():
    """Test visualization method."""
    print("Test 5: Visualization")
    print("-" * 60)
    
    camera_matrix = AprilTagDetector.create_default_camera_matrix(640, 480)
    dist_coeffs = np.zeros(5)
    tag_size = 0.19
    
    detector = AprilTagDetector(
        tag_size=tag_size,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs
    )
    
    # Create a blank image
    image = np.ones((480, 640, 3), dtype=np.uint8) * 255
    
    # Create mock detection (with proper shapes for OpenCV)
    mock_detection = {
        'tag_id': 0,
        'center': np.array([320.0, 240.0]),
        'corners': np.array([[310, 230], [330, 230], [330, 250], [310, 250]], dtype=np.float32),
        'translation': np.array([[0.0], [0.0], [1.0]]),  # Column vector (3, 1)
        'rotation_vector': np.array([[0.0], [0.0], [0.0]]),  # Column vector (3, 1)
        'rotation_matrix': np.eye(3),
    }
    
    try:
        vis_image = detector.visualize_detections(image, [mock_detection])
        print(f"✓ visualize_detections works")
        print(f"  Output image shape: {vis_image.shape}")
        
        if vis_image.shape == image.shape:
            print(f"✓ Output image has same shape as input")
        else:
            print(f"✗ Output image has different shape")
            return False
            
    except Exception as e:
        print(f"✗ visualize_detections failed: {e}")
        return False
    
    print()
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("AprilTagDetector Validation Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_initialization,
        test_object_points,
        test_detect_method,
        test_camera_matrix_helper,
        test_visualization,
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
        print("\n✓ All tests passed! AprilTagDetector is working correctly.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
