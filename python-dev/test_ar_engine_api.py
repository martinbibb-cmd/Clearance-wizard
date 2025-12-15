"""
Test suite for AR Engine API

Tests all API endpoints and functionality.
"""

import requests
import cv2
import numpy as np
import base64
import json
import time


# API configuration
API_URL = "http://127.0.0.1:5000"


def create_test_image(marker_type='aruco', marker_id=0, aruco_dict='DICT_4X4_50'):
    """
    Create a test image with a marker.
    
    Parameters
    ----------
    marker_type : str
        'aruco' or 'apriltag'
    marker_id : int
        Marker ID
    aruco_dict : str
        ArUco dictionary name (for ArUco markers)
    
    Returns
    -------
    np.ndarray
        Test image with marker
    """
    if marker_type == 'aruco':
        # Generate ArUco marker
        aruco_dict_cv = cv2.aruco.getPredefinedDictionary(
            getattr(cv2.aruco, aruco_dict)
        )
        marker_image = cv2.aruco.generateImageMarker(aruco_dict_cv, marker_id, 400)
        
        # Add white border
        test_image = cv2.copyMakeBorder(
            marker_image, 150, 150, 150, 150,
            cv2.BORDER_CONSTANT, value=255
        )
    else:
        # For AprilTag, create a placeholder (would need apriltag library to generate)
        test_image = np.ones((700, 700), dtype=np.uint8) * 255
        cv2.putText(
            test_image, f"AprilTag {marker_id}", (200, 350),
            cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 2
        )
    
    return test_image


def encode_image(image):
    """
    Encode image to base64.
    
    Parameters
    ----------
    image : np.ndarray
        Input image
    
    Returns
    -------
    str
        Base64-encoded image
    """
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')


def test_health():
    """Test health check endpoint."""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data['status']}")
            print(f"Features: {json.dumps(data['features'], indent=2)}")
            print("✓ Health check passed")
            return True
        else:
            print("✗ Health check failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_supported_markers():
    """Test supported markers endpoint."""
    print("\n=== Testing Supported Markers ===")
    try:
        response = requests.get(f"{API_URL}/api/v1/supported_markers")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Marker Types: {json.dumps(data['marker_types'], indent=2)}")
            print("✓ Supported markers test passed")
            return True
        else:
            print("✗ Supported markers test failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_camera_config():
    """Test camera configuration endpoint."""
    print("\n=== Testing Camera Configuration ===")
    try:
        response = requests.post(f"{API_URL}/api/v1/config", json={
            "image_width": 1280,
            "image_height": 720,
            "fov_degrees": 60.0,
            "dist_coeffs": [0, 0, 0, 0, 0]
        })
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data['status']}")
            print(f"Camera Matrix: {data['camera_matrix']}")
            print("✓ Camera configuration test passed")
            return True
        else:
            print("✗ Camera configuration test failed")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_aruco_detection():
    """Test ArUco marker detection."""
    print("\n=== Testing ArUco Detection ===")
    try:
        # Create test image
        test_image = create_test_image('aruco', marker_id=0)
        image_b64 = encode_image(test_image)
        
        # Configure camera
        height, width = test_image.shape[:2]
        requests.post(f"{API_URL}/api/v1/config", json={
            "image_width": width,
            "image_height": height,
            "fov_degrees": 60.0
        })
        
        # Detect markers
        response = requests.post(f"{API_URL}/api/v1/detect", json={
            "image": image_b64,
            "marker_type": "aruco",
            "marker_size": 0.19,
            "marker_count": 1,
            "aruco_dict": "DICT_4X4_50"
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data['status']}")
            print(f"Marker Type: {data['marker_type']}")
            print(f"Detected Count: {data['detected_count']}")
            print(f"All Markers Found: {data['all_markers_found']}")
            
            if data['detected_count'] > 0:
                for i, detection in enumerate(data['detections']):
                    print(f"\nMarker {i}:")
                    print(f"  ID: {detection['id']}")
                    print(f"  Position: {detection['position']}")
                    print(f"  Confidence: {detection['confidence']}")
                
                print("✓ ArUco detection test passed")
                return True
            else:
                print("✗ No markers detected")
                return False
        else:
            print("✗ ArUco detection test failed")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_multi_marker_detection():
    """Test multi-marker detection."""
    print("\n=== Testing Multi-Marker Detection ===")
    try:
        # Create test image with 4 markers
        test_image = np.ones((1000, 1000), dtype=np.uint8) * 255
        
        # Place 4 markers in a grid
        positions = [(100, 100), (600, 100), (100, 600), (600, 600)]
        for i, (x, y) in enumerate(positions):
            aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
            marker = cv2.aruco.generateImageMarker(aruco_dict, i, 300)
            test_image[y:y+300, x:x+300] = marker
        
        image_b64 = encode_image(test_image)
        
        # Configure camera
        height, width = test_image.shape[:2]
        requests.post(f"{API_URL}/api/v1/config", json={
            "image_width": width,
            "image_height": height,
            "fov_degrees": 60.0
        })
        
        # Detect markers
        response = requests.post(f"{API_URL}/api/v1/detect", json={
            "image": image_b64,
            "marker_type": "aruco",
            "marker_size": 0.09,  # 90mm
            "marker_count": 4,
            "aruco_dict": "DICT_4X4_50"
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data['status']}")
            print(f"Detected Count: {data['detected_count']}")
            print(f"Expected Count: {data['expected_count']}")
            print(f"All Markers Found: {data['all_markers_found']}")
            
            if data['detected_count'] == 4:
                print("✓ Multi-marker detection test passed")
                return True
            else:
                print(f"✗ Expected 4 markers, found {data['detected_count']}")
                return False
        else:
            print("✗ Multi-marker detection test failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_marker_generation():
    """Test marker generation endpoint."""
    print("\n=== Testing Marker Generation ===")
    try:
        response = requests.post(f"{API_URL}/api/v1/generate_marker", json={
            "marker_type": "aruco",
            "marker_id": 5,
            "size_pixels": 400,
            "aruco_dict": "DICT_4X4_50"
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Save generated marker
            with open('/tmp/test_marker.png', 'wb') as f:
                f.write(response.content)
            print("✓ Marker generation test passed")
            print("  Generated marker saved to /tmp/test_marker.png")
            return True
        else:
            print("✗ Marker generation test failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_error_handling():
    """Test error handling."""
    print("\n=== Testing Error Handling ===")
    
    # Test missing image
    try:
        response = requests.post(f"{API_URL}/api/v1/detect", json={
            "marker_type": "aruco"
        })
        
        if response.status_code == 400:
            print("✓ Missing image error handled correctly")
        else:
            print("✗ Missing image error not handled correctly")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test invalid marker type
    try:
        test_image = create_test_image('aruco', marker_id=0)
        image_b64 = encode_image(test_image)
        
        response = requests.post(f"{API_URL}/api/v1/detect", json={
            "image": image_b64,
            "marker_type": "invalid_type"
        })
        
        if response.status_code == 400:
            print("✓ Invalid marker type error handled correctly")
        else:
            print("✗ Invalid marker type error not handled correctly")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    print("✓ Error handling tests passed")
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("AR Engine API Test Suite")
    print("=" * 60)
    
    print(f"\nTesting API at: {API_URL}")
    print("Make sure the API server is running: python ar_engine_api.py")
    
    time.sleep(1)
    
    results = {
        'health': test_health(),
        'supported_markers': test_supported_markers(),
        'camera_config': test_camera_config(),
        'aruco_detection': test_aruco_detection(),
        'multi_marker': test_multi_marker_detection(),
        'marker_generation': test_marker_generation(),
        'error_handling': test_error_handling()
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20s} : {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print("\n" + "=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == '__main__':
    import sys
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
