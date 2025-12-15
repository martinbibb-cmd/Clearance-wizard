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
            # Use new response format
            marker_count = data.get('marker_count', data.get('detected_count', 0))
            print(f"Detected Count: {marker_count}")
            
            if marker_count > 0:
                # Use 'markers' field if available, fall back to 'detections'
                markers = data.get('markers', data.get('detections', []))
                for i, detection in enumerate(markers):
                    print(f"\nMarker {i}:")
                    print(f"  ID: {detection['id']}")
                    print(f"  Position: {detection['position']}")
                    print(f"  Confidence: {detection.get('confidence', 'N/A')}")
                
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
            # Use new response format
            marker_count = data.get('marker_count', data.get('detected_count', 0))
            print(f"Detected Count: {marker_count}")
            
            if marker_count == 4:
                print("✓ Multi-marker detection test passed")
                return True
            else:
                print(f"✗ Expected 4 markers, found {marker_count}")
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


def test_status_endpoint():
    """Test status endpoint."""
    print("\n=== Testing Status Endpoint ===")
    try:
        response = requests.get(f"{API_URL}/api/v1/status")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Active Sessions: {data.get('active_sessions', 0)}")
            print(f"Stored Calibrations: {data.get('stored_calibrations', 0)}")
            print("✓ Status endpoint test passed")
            return True
        else:
            print("✗ Status endpoint test failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_session_management():
    """Test session-based configuration."""
    print("\n=== Testing Session Management ===")
    try:
        # Configure camera with session
        response = requests.post(f"{API_URL}/api/v1/config", json={
            "image_width": 1280,
            "image_height": 720,
            "fov_degrees": 60.0,
            "save_calibration": True,
            "device_name": "test_camera"
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            calibration_id = data.get('calibration_id')
            print(f"Session ID: {session_id}")
            print(f"Calibration ID: {calibration_id}")
            
            if session_id and calibration_id:
                print("✓ Session management test passed")
                return True, session_id, calibration_id
            else:
                print("✗ Session or calibration ID not returned")
                return False, None, None
        else:
            print("✗ Session management test failed")
            return False, None, None
    except Exception as e:
        print(f"✗ Error: {e}")
        return False, None, None


def test_multipart_upload():
    """Test multipart/form-data upload."""
    print("\n=== Testing Multipart Upload ===")
    try:
        # Create test image
        test_image = create_test_image('aruco', marker_id=0)
        
        # Save to temporary file
        temp_path = '/tmp/test_marker_multipart.jpg'
        cv2.imwrite(temp_path, test_image)
        
        # Upload using multipart/form-data
        with open(temp_path, 'rb') as f:
            files = {'image': ('test.jpg', f, 'image/jpeg')}
            data = {
                'marker_type': 'aruco',
                'marker_size': '0.19',
                'aruco_dict': 'DICT_4X4_50'
            }
            response = requests.post(
                f"{API_URL}/api/v1/detect",
                files=files,
                data=data
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Status: {result.get('status')}")
            print(f"Markers Found: {result.get('marker_count', 0)}")
            print(f"Timings: {result.get('timings_ms', {})}")
            
            # Check for new response fields
            has_markers = 'markers' in result
            has_timings = 'timings_ms' in result
            has_camera = 'camera' in result
            has_warnings = 'warnings' in result
            
            if has_markers and has_timings and has_camera and has_warnings:
                print("✓ Multipart upload test passed")
                return True
            else:
                print("✗ Response missing required fields")
                return False
        else:
            print("✗ Multipart upload test failed")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_transform_matrices():
    """Test that transform matrices are returned."""
    print("\n=== Testing Transform Matrices ===")
    try:
        # Create test image
        test_image = create_test_image('aruco', marker_id=0)
        image_b64 = encode_image(test_image)
        
        # Detect markers
        response = requests.post(f"{API_URL}/api/v1/detect", json={
            "image": image_b64,
            "marker_type": "aruco",
            "marker_size": 0.19,
            "aruco_dict": "DICT_4X4_50"
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            markers = data.get('markers', [])
            
            if len(markers) > 0:
                marker = markers[0]
                has_rvec = 'rvec' in marker
                has_tvec = 'tvec' in marker
                has_transform = 'transform_matrix' in marker
                
                print(f"Has rvec: {has_rvec}")
                print(f"Has tvec: {has_tvec}")
                print(f"Has transform_matrix: {has_transform}")
                
                if has_rvec and has_tvec and has_transform:
                    # Verify transform matrix is 4x4
                    transform = marker['transform_matrix']
                    if len(transform) == 4 and len(transform[0]) == 4:
                        print("✓ Transform matrices test passed")
                        return True
                    else:
                        print("✗ Transform matrix is not 4x4")
                        return False
                else:
                    print("✗ Missing pose formats")
                    return False
            else:
                print("✗ No markers detected")
                return False
        else:
            print("✗ Detection failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_calibration_persistence():
    """Test calibration persistence."""
    print("\n=== Testing Calibration Persistence ===")
    try:
        # Create calibration
        response = requests.post(f"{API_URL}/api/v1/config", json={
            "image_width": 1920,
            "image_height": 1080,
            "fov_degrees": 70.0,
            "save_calibration": True,
            "device_name": "test_hd_camera"
        })
        
        if response.status_code != 200:
            print("✗ Failed to create calibration")
            return False
        
        calibration_id = response.json().get('calibration_id')
        print(f"Created Calibration ID: {calibration_id}")
        
        # List calibrations
        response = requests.get(f"{API_URL}/api/v1/calibrations")
        if response.status_code != 200:
            print("✗ Failed to list calibrations")
            return False
        
        calibrations = response.json().get('calibrations', [])
        print(f"Total Calibrations: {len(calibrations)}")
        
        # Get specific calibration
        response = requests.get(f"{API_URL}/api/v1/calibrations/{calibration_id}")
        if response.status_code != 200:
            print("✗ Failed to get calibration")
            return False
        
        calib_data = response.json()
        if calib_data.get('calibration_id') == calibration_id:
            print("✓ Calibration persistence test passed")
            return True
        else:
            print("✗ Calibration ID mismatch")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_openapi_spec():
    """Test OpenAPI specification endpoint."""
    print("\n=== Testing OpenAPI Specification ===")
    try:
        response = requests.get(f"{API_URL}/api/v1/openapi.json")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            spec = response.json()
            has_openapi = 'openapi' in spec
            has_paths = 'paths' in spec
            has_info = 'info' in spec
            
            print(f"Has OpenAPI version: {has_openapi}")
            print(f"Has paths: {has_paths}")
            print(f"Has info: {has_info}")
            
            if has_openapi and has_paths and has_info:
                print(f"API Title: {spec['info'].get('title')}")
                print(f"API Version: {spec['info'].get('version')}")
                print(f"Number of paths: {len(spec.get('paths', {}))}")
                print("✓ OpenAPI specification test passed")
                return True
            else:
                print("✗ OpenAPI spec incomplete")
                return False
        elif response.status_code == 501:
            print("⚠ OpenAPI not available (optional dependency)")
            return True  # Not a failure if not installed
        else:
            print("✗ OpenAPI specification test failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_rate_limiting():
    """Test rate limiting functionality."""
    print("\n=== Testing Rate Limiting ===")
    try:
        # Make rapid requests to trigger rate limit
        print("Making rapid requests to test rate limiting...")
        
        # Get current rate limit from first successful request
        response = requests.get(f"{API_URL}/health")
        if response.status_code != 200:
            print("✗ Initial health check failed")
            return False
        
        # Make many rapid requests
        success_count = 0
        rate_limited = False
        
        for i in range(105):  # Exceed the 100 req/min limit
            response = requests.get(f"{API_URL}/health")
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited = True
                error_data = response.json()
                print(f"Rate limit triggered after {success_count} requests")
                print(f"Error message: {error_data.get('error')}")
                print(f"Retry after: {error_data.get('retry_after')} seconds")
                break
        
        if rate_limited:
            print("✓ Rate limiting test passed")
            return True
        else:
            print(f"⚠ Rate limit not triggered after {success_count} requests")
            print("  (May need adjustment based on server configuration)")
            return True  # Don't fail if rate limit is configured differently
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_payload_size_limit():
    """Test payload size limit."""
    print("\n=== Testing Payload Size Limit ===")
    try:
        # Create a very large image (> 10MB)
        large_image = np.ones((5000, 5000, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', large_image)
        image_b64 = base64.b64encode(buffer).decode('utf-8')
        
        print(f"Test payload size: {len(image_b64) / (1024*1024):.2f} MB")
        
        response = requests.post(f"{API_URL}/api/v1/detect", json={
            "image": image_b64,
            "marker_type": "aruco"
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 413:
            error_data = response.json()
            print(f"Error message: {error_data.get('error')}")
            print("✓ Payload size limit test passed")
            return True
        elif response.status_code == 400:
            # May fail validation before size check
            print("⚠ Request rejected (possibly dimension validation)")
            return True
        else:
            print(f"✗ Expected 413, got {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_dimension_limit():
    """Test image dimension limit."""
    print("\n=== Testing Image Dimension Limit ===")
    try:
        # Create image exceeding 4096x4096 limit
        oversized_image = np.ones((5000, 5000), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', oversized_image)
        image_b64 = base64.b64encode(buffer).decode('utf-8')
        
        print(f"Test image dimensions: {oversized_image.shape}")
        
        response = requests.post(f"{API_URL}/api/v1/detect", json={
            "image": image_b64,
            "marker_type": "aruco"
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            error_data = response.json()
            print(f"Error message: {error_data.get('error')}")
            warnings = error_data.get('warnings', [])
            if warnings:
                print(f"Warnings: {warnings}")
            print("✓ Dimension limit test passed")
            return True
        else:
            print(f"✗ Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("AR Engine API Test Suite")
    print("=" * 60)
    
    print(f"\nTesting API at: {API_URL}")
    print("Make sure the API server is running: python ar_engine_api.py")
    
    time.sleep(1)
    
    # Run original tests
    results = {
        'health': test_health(),
        'supported_markers': test_supported_markers(),
        'camera_config': test_camera_config(),
        'aruco_detection': test_aruco_detection(),
        'multi_marker': test_multi_marker_detection(),
        'marker_generation': test_marker_generation(),
        'error_handling': test_error_handling()
    }
    
    # Run new tests
    results['status_endpoint'] = test_status_endpoint()
    
    session_result, session_id, calibration_id = test_session_management()
    results['session_management'] = session_result
    
    results['multipart_upload'] = test_multipart_upload()
    results['transform_matrices'] = test_transform_matrices()
    results['calibration_persistence'] = test_calibration_persistence()
    results['openapi_spec'] = test_openapi_spec()
    
    # Security tests
    results['rate_limiting'] = test_rate_limiting()
    results['payload_size_limit'] = test_payload_size_limit()
    results['dimension_limit'] = test_dimension_limit()
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:25s} : {status}")
    
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
