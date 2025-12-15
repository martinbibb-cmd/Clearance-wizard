# AR Engine API v2.0 Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Installation

```bash
cd python-dev
pip install -r requirements.txt
```

### Start Server

```bash
python ar_engine_api.py --host 127.0.0.1 --port 5000
```

Server starts at `http://127.0.0.1:5000`

### View Documentation

Open in browser: `http://127.0.0.1:5000/api/docs`

## 📋 Basic Usage

### 1. Check Health

```python
import requests

response = requests.get('http://127.0.0.1:5000/health')
print(response.json())
```

### 2. Configure Camera (Create Session)

```python
response = requests.post('http://127.0.0.1:5000/api/v1/config', json={
    "image_width": 1280,
    "image_height": 720,
    "fov_degrees": 60.0,
    "save_calibration": True,
    "device_name": "my_camera"
})

session_id = response.json()['session_id']
calibration_id = response.json()['calibration_id']
```

### 3. Detect Markers (Multipart Upload - Recommended)

```python
with open('image.jpg', 'rb') as f:
    files = {'image': ('image.jpg', f, 'image/jpeg')}
    data = {
        'marker_type': 'apriltag',
        'marker_size': '0.19',
        'session_id': session_id
    }
    response = requests.post(
        'http://127.0.0.1:5000/api/v1/detect',
        files=files,
        data=data
    )

result = response.json()
markers = result['markers']
timings = result['timings_ms']
```

### 4. Process Results

```python
for marker in markers:
    print(f"Marker ID: {marker['id']}")
    print(f"Position: {marker['position']}")
    print(f"4x4 Transform: {marker['transform_matrix']}")
    print(f"Confidence: {marker['confidence']}")
```

## 🎯 Key Features

### Session Management
```python
# Each session is isolated
session_1 = create_session(width=1280, height=720)
session_2 = create_session(width=1920, height=1080)

# Sessions don't interfere with each other
detect(image1, session_id=session_1)  # Uses 1280x720 config
detect(image2, session_id=session_2)  # Uses 1920x1080 config
```

### Calibration Persistence
```python
# Save calibration once
response = requests.post('http://127.0.0.1:5000/api/v1/config', json={
    "image_width": 1920,
    "image_height": 1080,
    "save_calibration": True,
    "device_name": "iPhone_15_Pro"
})
calibration_id = response.json()['calibration_id']

# Reuse calibration later (even after server restart if persisted)
response = requests.post('http://127.0.0.1:5000/api/v1/detect', json={
    "image": base64_image,
    "calibration_id": calibration_id
})
```

### Multipart vs Base64

**Multipart (30% faster):**
```python
# Recommended for production
files = {'image': open('photo.jpg', 'rb')}
response = requests.post(url, files=files, data={'marker_type': 'apriltag'})
```

**Base64 (backward compatible):**
```python
# Still supported
import base64
import cv2

image = cv2.imread('photo.jpg')
_, buffer = cv2.imencode('.jpg', image)
image_b64 = base64.b64encode(buffer).decode('utf-8')

response = requests.post(url, json={'image': image_b64, 'marker_type': 'apriltag'})
```

## 📊 Response Format

```json
{
  "status": "success",
  "markers": [
    {
      "id": 0,
      "position": {"x": 0.05, "y": -0.02, "z": 0.5},
      "rvec": [0.1, -0.05, 0.02],
      "tvec": [0.05, -0.02, 0.5],
      "rotation_matrix": [[...], [...], [...]],
      "transform_matrix": [[...], [...], [...], [...]],
      "corners": [[...], [...], [...], [...]],
      "confidence": 0.95
    }
  ],
  "marker_count": 1,
  "timings_ms": {
    "image_decode_ms": 15.2,
    "detection_ms": 45.8,
    "total_ms": 61.5
  },
  "camera": {
    "width": 1280,
    "height": 720,
    "calibration_id": "abc-123"
  },
  "warnings": [],
  "session_id": "xyz-789"
}
```

## 🛡️ Security Limits

- **Rate Limit:** 100 requests/minute per IP
- **Max Payload:** 10 MB per request
- **Max Image Size:** 4096x4096 pixels

**Error Response:**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

## 🔧 Complete Example

```python
import requests
import cv2

# Configuration
API_URL = "http://127.0.0.1:5000"

# 1. Create session
config_response = requests.post(f"{API_URL}/api/v1/config", json={
    "image_width": 1280,
    "image_height": 720,
    "fov_degrees": 60.0,
    "save_calibration": True,
    "device_name": "webcam_01"
})

session_id = config_response.json()['session_id']
calibration_id = config_response.json()['calibration_id']

print(f"Session ID: {session_id}")
print(f"Calibration ID: {calibration_id}")

# 2. Detect markers (multipart upload)
with open('test_image.jpg', 'rb') as f:
    files = {'image': ('test_image.jpg', f, 'image/jpeg')}
    data = {
        'marker_type': 'apriltag',
        'marker_size': '0.19',
        'tag_family': 'tag36h11',
        'session_id': session_id
    }
    
    detect_response = requests.post(
        f"{API_URL}/api/v1/detect",
        files=files,
        data=data
    )

# 3. Process results
result = detect_response.json()

print(f"\nDetection Results:")
print(f"Status: {result['status']}")
print(f"Markers found: {result['marker_count']}")
print(f"Detection time: {result['timings_ms']['detection_ms']:.1f}ms")
print(f"Total time: {result['timings_ms']['total_ms']:.1f}ms")

# 4. Display marker details
for marker in result['markers']:
    print(f"\nMarker {marker['id']}:")
    print(f"  Position: x={marker['position']['x']:.3f}, "
          f"y={marker['position']['y']:.3f}, "
          f"z={marker['position']['z']:.3f}")
    print(f"  Confidence: {marker['confidence']:.2f}")
    print(f"  Transform matrix shape: {len(marker['transform_matrix'])}x{len(marker['transform_matrix'][0])}")

# 5. Check for warnings
if result['warnings']:
    print("\nWarnings:")
    for warning in result['warnings']:
        print(f"  - {warning}")
```

## 📚 Common Patterns

### Error Handling
```python
def detect_with_retry(image_path, session_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                data = {'session_id': session_id}
                response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                return response.json()['markers']
            elif response.status_code == 429:
                # Rate limited
                time.sleep(response.json().get('retry_after', 60))
            else:
                print(f"Error: {response.json().get('error')}")
                return None
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    return None
```

### Reusing Calibrations
```python
# Store calibration ID in config file
import json

def save_calibration(calibration_id, device_name):
    config = {'calibrations': {}}
    try:
        with open('calibrations.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        pass
    
    config['calibrations'][device_name] = calibration_id
    
    with open('calibrations.json', 'w') as f:
        json.dump(config, f)

def load_calibration(device_name):
    try:
        with open('calibrations.json', 'r') as f:
            config = json.load(f)
        return config['calibrations'].get(device_name)
    except FileNotFoundError:
        return None
```

### Performance Monitoring
```python
def monitor_performance(result):
    timings = result['timings_ms']
    total = timings['total_ms']
    
    # Log slow requests
    if total > 100:
        print(f"SLOW REQUEST ({total:.1f}ms):")
        print(f"  Decode: {timings['image_decode_ms']:.1f}ms")
        print(f"  Detection: {timings['detection_ms']:.1f}ms")
    
    # Return breakdown
    return {
        'decode_pct': timings['image_decode_ms'] / total * 100,
        'detect_pct': timings['detection_ms'] / total * 100
    }
```

## 🧪 Testing

```bash
# Run test suite
cd python-dev
python test_ar_engine_api.py

# Should see: Total: 13/13 tests passed
```

## 📖 More Documentation

- **Full API Docs:** `AR_ENGINE_API.md`
- **Migration Guide:** `API_V2_MIGRATION_GUIDE.md`
- **Implementation Details:** `V2_IMPLEMENTATION_SUMMARY.md`
- **OpenAPI Spec:** `http://127.0.0.1:5000/api/v1/openapi.json`
- **Interactive Docs:** `http://127.0.0.1:5000/api/docs`

## ⚠️ Production Checklist

Before deploying to production:

- [ ] Use WSGI server (Gunicorn/uWSGI), not Flask dev server
- [ ] Enable HTTPS/TLS
- [ ] Implement authentication (API keys/OAuth)
- [ ] Restrict CORS origins
- [ ] Set up monitoring and logging
- [ ] Configure appropriate rate limits
- [ ] Set up session persistence (Redis)
- [ ] Configure calibration database
- [ ] Test error handling
- [ ] Load test at expected scale

## 🎉 You're Ready!

Start the server and visit `http://127.0.0.1:5000/api/docs` for interactive documentation!
