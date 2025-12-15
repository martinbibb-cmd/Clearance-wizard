# AR Engine API v2.0 Migration Guide

## Overview

Version 2.0 of the AR Engine API introduces production-ready features including session management, calibration persistence, multipart uploads, security enhancements, and standardized response schemas. This guide helps you migrate from v1.x to v2.0.

## What's New in v2.0

### 1. Session-Scoped Configuration

**Old (v1.x):** Global configuration affected all requests
```python
# Global configuration - affects all subsequent requests
response = requests.post(f"{API_URL}/api/v1/config", json={
    "image_width": 1280,
    "image_height": 720
})
```

**New (v2.0):** Request-scoped configuration with session management
```python
# Create session-scoped configuration
response = requests.post(f"{API_URL}/api/v1/config", json={
    "image_width": 1280,
    "image_height": 720,
    "save_calibration": True,
    "device_name": "my_camera"
})

session_id = response.json()['session_id']
calibration_id = response.json()['calibration_id']

# Use session_id in subsequent requests
response = requests.post(f"{API_URL}/api/v1/detect", json={
    "image": image_b64,
    "session_id": session_id  # Isolates this request's configuration
})
```

### 2. Multipart/Form-Data Upload Support

**Old (v1.x):** Only base64 JSON uploads
```python
# Only option: base64 encoding
_, buffer = cv2.imencode('.jpg', image)
image_b64 = base64.b64encode(buffer).decode('utf-8')

response = requests.post(f"{API_URL}/api/v1/detect", json={
    "image": image_b64,
    "marker_type": "apriltag"
})
```

**New (v2.0):** Direct file upload with multipart/form-data (faster, more efficient)
```python
# Option 1: Multipart upload (recommended for production)
with open('image.jpg', 'rb') as f:
    files = {'image': ('image.jpg', f, 'image/jpeg')}
    data = {
        'marker_type': 'apriltag',
        'marker_size': '0.19',
        'session_id': session_id
    }
    response = requests.post(f"{API_URL}/api/v1/detect", files=files, data=data)

# Option 2: Base64 JSON (still supported for backward compatibility)
response = requests.post(f"{API_URL}/api/v1/detect", json={
    "image": image_b64,
    "marker_type": "apriltag"
})
```

### 3. Calibration Persistence

**New Feature:** Save and reuse calibrations across sessions
```python
# Create and save calibration
response = requests.post(f"{API_URL}/api/v1/config", json={
    "image_width": 1920,
    "image_height": 1080,
    "fov_degrees": 70.0,
    "save_calibration": True,
    "device_name": "iPhone_15_Pro"
})

calibration_id = response.json()['calibration_id']

# Later, reuse calibration in any session
response = requests.post(f"{API_URL}/api/v1/detect", json={
    "image": image_b64,
    "calibration_id": calibration_id  # Use stored calibration
})

# List all calibrations
response = requests.get(f"{API_URL}/api/v1/calibrations")

# Get specific calibration
response = requests.get(f"{API_URL}/api/v1/calibrations/{calibration_id}")
```

### 4. Standardized Response Schema

**Old (v1.x):** Inconsistent response format
```json
{
  "status": "success",
  "detected_count": 2,
  "detections": [...]
}
```

**New (v2.0):** Consistent, comprehensive response schema
```json
{
  "status": "success",
  "markers": [
    {
      "id": 0,
      "position": {"x": 0.05, "y": -0.02, "z": 0.5},
      "rotation_matrix": [[...], [...], [...]],
      "rvec": [0.1, -0.05, 0.02],
      "tvec": [0.05, -0.02, 0.5],
      "transform_matrix": [[...], [...], [...], [...]],
      "corners": [[...], [...], [...], [...]],
      "confidence": 0.95
    }
  ],
  "marker_count": 2,
  "marker_type": "apriltag",
  "marker_size": 0.19,
  "timings_ms": {
    "image_decode_ms": 15.2,
    "calibration_setup_ms": 0.5,
    "detection_ms": 45.8,
    "total_ms": 61.5
  },
  "camera": {
    "width": 1280,
    "height": 720,
    "calibrated": true,
    "calibration_id": "abc-123-def"
  },
  "warnings": [],
  "session_id": "xyz-789-uvw",
  "calibration_id": "abc-123-def",
  "timestamp": "2025-12-15T10:30:00.000Z"
}
```

### 5. Multiple Pose Formats

**New Feature:** Markers now include multiple pose representations
```python
response = requests.post(f"{API_URL}/api/v1/detect", json={...})
markers = response.json()['markers']

for marker in markers:
    # Rotation vector (3x1)
    rvec = marker['rvec']
    
    # Translation vector (3x1)
    tvec = marker['tvec']
    
    # Rotation matrix (3x3)
    rmat = marker['rotation_matrix']
    
    # 4x4 transformation matrix (NEW!)
    transform = marker['transform_matrix']
    # Can be directly used with graphics engines
```

### 6. Performance Timings

**New Feature:** Detailed performance metrics
```python
response = requests.post(f"{API_URL}/api/v1/detect", json={...})
timings = response.json()['timings_ms']

print(f"Image decode: {timings['image_decode_ms']:.2f}ms")
print(f"Detection: {timings['detection_ms']:.2f}ms")
print(f"Total: {timings['total_ms']:.2f}ms")
```

### 7. Security Enhancements

**New Features:**
- **Rate Limiting:** 100 requests per minute per client
- **Payload Size Limit:** 10 MB maximum
- **Image Dimension Limits:** 4096x4096 maximum

**Handling Rate Limits:**
```python
response = requests.post(f"{API_URL}/api/v1/detect", json={...})

if response.status_code == 429:
    # Rate limit exceeded
    retry_after = response.json()['retry_after']
    print(f"Rate limited. Retry after {retry_after} seconds")
elif response.status_code == 413:
    # Payload too large
    print("Image too large. Resize before uploading")
```

### 8. Status and Health Endpoints

**New Endpoints:**

```python
# Health check with features
response = requests.get(f"{API_URL}/health")
# Returns: status, features (apriltag, aruco, multipart_upload, etc.)

# Detailed status
response = requests.get(f"{API_URL}/api/v1/status")
# Returns: active_sessions, stored_calibrations, features

# Session-specific status
response = requests.get(f"{API_URL}/api/v1/status?session_id={session_id}")
# Returns: session details including calibration_id
```

### 9. OpenAPI/Swagger Documentation

**New Feature:** Auto-generated API documentation

Access Swagger UI at: `http://127.0.0.1:5000/api/docs`

Get OpenAPI spec: `http://127.0.0.1:5000/api/v1/openapi.json`

```python
# Get OpenAPI specification programmatically
response = requests.get(f"{API_URL}/api/v1/openapi.json")
openapi_spec = response.json()
```

## Migration Checklist

### Step 1: Update Response Handling

**Change 1:** `detected_count` → `marker_count`
```python
# Old
count = response.json()['detected_count']

# New (backward compatible)
count = response.json().get('marker_count', response.json().get('detected_count', 0))
```

**Change 2:** `detections` → `markers`
```python
# Old
markers = response.json()['detections']

# New (backward compatible)
markers = response.json().get('markers', response.json().get('detections', []))
```

### Step 2: Implement Session Management

```python
class ARClient:
    def __init__(self, api_url):
        self.api_url = api_url
        self.session_id = None
        self.calibration_id = None
    
    def configure(self, width, height, fov=60.0, save=True):
        """Configure camera and create session."""
        response = requests.post(f"{self.api_url}/api/v1/config", json={
            "image_width": width,
            "image_height": height,
            "fov_degrees": fov,
            "save_calibration": save,
            "device_name": "my_device"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.session_id = data['session_id']
            self.calibration_id = data.get('calibration_id')
            return True
        return False
    
    def detect(self, image_path, marker_type='apriltag', marker_size=0.19):
        """Detect markers using session."""
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {
                'marker_type': marker_type,
                'marker_size': str(marker_size),
                'session_id': self.session_id
            }
            response = requests.post(
                f"{self.api_url}/api/v1/detect",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            return response.json()['markers']
        return []
```

### Step 3: Use Multipart Upload for Production

```python
def detect_markers_efficient(image, marker_type='apriltag'):
    """Use multipart upload for better performance."""
    # Save to temporary buffer
    _, buffer = cv2.imencode('.jpg', image)
    image_bytes = buffer.tobytes()
    
    # Upload using multipart
    files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
    data = {
        'marker_type': marker_type,
        'marker_size': '0.19',
        'session_id': session_id
    }
    
    response = requests.post(
        f"{API_URL}/api/v1/detect",
        files=files,
        data=data
    )
    
    return response.json()
```

### Step 4: Handle New Response Fields

```python
def process_detection_response(response_json):
    """Process v2.0 response with all new fields."""
    markers = response_json['markers']
    timings = response_json['timings_ms']
    camera = response_json['camera']
    warnings = response_json['warnings']
    
    # Log warnings
    for warning in warnings:
        print(f"Warning: {warning}")
    
    # Check performance
    if timings['total_ms'] > 100:
        print(f"Slow detection: {timings['total_ms']:.1f}ms")
    
    # Process markers with new transform matrix
    for marker in markers:
        transform = np.array(marker['transform_matrix'])
        # Use 4x4 transform directly
        apply_transformation(transform)
    
    return markers
```

## Backward Compatibility

Version 2.0 maintains backward compatibility with v1.x:

- **Old response fields still present:** `detected_count`, `detections`, `all_markers_found`
- **Base64 JSON upload still supported:** Use `Content-Type: application/json`
- **Global configuration still works:** If no session_id provided, uses global engine state

However, we recommend migrating to new features for better:
- **Performance:** Multipart uploads are faster
- **Scalability:** Session management prevents conflicts
- **Debugging:** Timing metrics and warnings help identify issues
- **Maintenance:** Calibration persistence reduces setup time

## Configuration Examples

### Development Setup
```python
# Simple setup for testing
response = requests.post(f"{API_URL}/api/v1/config", json={
    "image_width": 640,
    "image_height": 480,
    "fov_degrees": 60.0
})
session_id = response.json()['session_id']
```

### Production Setup
```python
# Production setup with calibration persistence
response = requests.post(f"{API_URL}/api/v1/config", json={
    "image_width": 1920,
    "image_height": 1080,
    "fov_degrees": 70.0,
    "dist_coeffs": [-0.08, 0.12, 0.0, 0.0, -0.05],  # Real distortion coefficients
    "save_calibration": True,
    "device_name": "production_camera_01"
})

calibration_id = response.json()['calibration_id']
# Save calibration_id for reuse across restarts
```

## Error Handling

### v2.0 Error Responses

All errors now include consistent schema:

```json
{
  "error": "Descriptive error message",
  "warnings": ["Optional warning 1", "Optional warning 2"]
}
```

### Error Codes

- `400 Bad Request` - Invalid parameters or image
- `404 Not Found` - Calibration or resource not found
- `413 Payload Too Large` - Image exceeds size limit
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Example Error Handling

```python
def detect_with_error_handling(image_path, session_id):
    """Detect with comprehensive error handling."""
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'session_id': session_id}
            response = requests.post(
                f"{API_URL}/api/v1/detect",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            
            # Check warnings
            if result['warnings']:
                for warning in result['warnings']:
                    logging.warning(f"API Warning: {warning}")
            
            return result['markers']
        
        elif response.status_code == 429:
            # Rate limited
            retry_after = response.json().get('retry_after', 60)
            logging.error(f"Rate limited. Retry after {retry_after}s")
            return None
        
        elif response.status_code == 413:
            # Image too large
            logging.error("Image too large. Resize before uploading")
            return None
        
        else:
            # Other error
            error = response.json().get('error', 'Unknown error')
            logging.error(f"Detection error: {error}")
            return None
    
    except Exception as e:
        logging.error(f"Request failed: {e}")
        return None
```

## Performance Best Practices

1. **Use multipart upload** for images > 1MB
2. **Reuse calibration_id** to avoid repeated configuration
3. **Monitor timings_ms** to identify bottlenecks
4. **Resize images** to appropriate resolution (1280x720 recommended)
5. **Use session_id** for multi-threaded applications
6. **Check warnings** to catch potential issues

## Testing Your Migration

Run the test suite to verify compatibility:

```bash
cd python-dev
python test_ar_engine_api.py
```

All 13 tests should pass, including:
- Health check
- Session management
- Multipart upload
- Transform matrices
- Calibration persistence
- OpenAPI specification

## Support and Documentation

- **OpenAPI Spec:** `http://127.0.0.1:5000/api/v1/openapi.json`
- **Swagger UI:** `http://127.0.0.1:5000/api/docs`
- **API Documentation:** `python-dev/AR_ENGINE_API.md`
- **Test Suite:** `python-dev/test_ar_engine_api.py`

## Summary

Version 2.0 introduces production-ready features while maintaining backward compatibility. Key improvements:

✅ Session-scoped configuration prevents conflicts  
✅ Multipart upload improves performance  
✅ Calibration persistence reduces setup time  
✅ Standardized responses with timings and warnings  
✅ Multiple pose formats for flexibility  
✅ Security guards against abuse  
✅ OpenAPI documentation for easy integration  

Start migrating today to take advantage of these improvements!
