# AR Engine Backend API

## Overview

The AR Engine Backend API provides a RESTful HTTP interface for AR marker detection and pose estimation. It supports both AprilTag and ArUco markers and can be integrated with web applications, mobile apps, or other systems requiring AR functionality.

## Features

- **Multiple Marker Types**: Support for AprilTag (tag36h11, etc.) and ArUco (DICT_4X4_50, etc.)
- **Pose Estimation**: 3D position and orientation for each detected marker
- **Multi-Marker Support**: Detect multiple markers in a single image
- **Camera Calibration**: Configurable camera parameters for accurate pose estimation
- **REST API**: Standard HTTP/JSON interface for easy integration
- **CORS Enabled**: Accessible from web browsers

## Installation

### Prerequisites

```bash
cd python-dev
pip install -r requirements.txt
```

### Required Packages

- `flask>=2.0.0` - Web framework
- `flask-cors>=3.0.0` - Cross-origin resource sharing
- `opencv-python>=4.5.0` - Computer vision
- `numpy>=1.20.0` - Numerical operations
- `apriltag>=0.0.16` - AprilTag detection (optional but recommended)

## Running the Server

### Basic Usage

```bash
cd python-dev
python ar_engine_api.py
```

Server will start on `http://127.0.0.1:5000`

### Custom Host and Port

```bash
python ar_engine_api.py --host 0.0.0.0 --port 8080
```

### Debug Mode

```bash
python ar_engine_api.py --debug
```

## API Endpoints

### 1. Health Check

Check if the API is running and what features are available.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-12-15T06:30:00.000Z",
  "features": {
    "apriltag": true,
    "aruco": true
  }
}
```

### 2. Configure Camera

Setup camera calibration parameters for accurate pose estimation.

**Endpoint:** `POST /api/v1/config`

**Request Body:**
```json
{
  "image_width": 1280,
  "image_height": 720,
  "fov_degrees": 60.0,
  "dist_coeffs": [0, 0, 0, 0, 0]
}
```

**Parameters:**
- `image_width` (required): Image width in pixels
- `image_height` (required): Image height in pixels
- `fov_degrees` (optional): Vertical field of view in degrees (default: 60.0)
- `dist_coeffs` (optional): Lens distortion coefficients [k1, k2, p1, p2, k3] (default: [0, 0, 0, 0, 0])

**Response:**
```json
{
  "status": "configured",
  "camera_matrix": [
    [1245.56, 0, 640],
    [0, 1245.56, 360],
    [0, 0, 1]
  ],
  "dist_coeffs": [0, 0, 0, 0, 0]
}
```

### 3. Detect Markers

Detect AR markers in an image and estimate their pose.

**Endpoint:** `POST /api/v1/detect`

**Request Body:**
```json
{
  "image": "<base64-encoded image>",
  "marker_type": "apriltag",
  "marker_size": 0.19,
  "marker_count": 1,
  "tag_family": "tag36h11"
}
```

**Parameters:**
- `image` (required): Base64-encoded image (JPEG or PNG)
- `marker_type` (optional): "apriltag" or "aruco" (default: "apriltag")
- `marker_size` (optional): Physical marker size in meters (default: 0.19)
- `marker_count` (optional): Expected number of markers
- `tag_family` (optional): AprilTag family (default: "tag36h11")
- `aruco_dict` (optional): ArUco dictionary name (default: "DICT_4X4_50")

**Response:**
```json
{
  "status": "success",
  "marker_type": "apriltag",
  "marker_size": 0.19,
  "detected_count": 1,
  "expected_count": 1,
  "all_markers_found": true,
  "detections": [
    {
      "id": 0,
      "family": "tag36h11",
      "position": {
        "x": 0.045,
        "y": -0.023,
        "z": 0.512
      },
      "rotation_matrix": [
        [0.998, -0.052, 0.036],
        [0.053, 0.998, -0.020],
        [-0.034, 0.022, 0.999]
      ],
      "corners": [
        [320.5, 240.3],
        [420.8, 245.1],
        [418.2, 345.7],
        [318.1, 340.9]
      ],
      "confidence": 0.95
    }
  ],
  "timestamp": "2025-12-15T06:30:00.000Z"
}
```

**Detection Object Fields:**
- `id`: Marker ID number
- `family`: Marker family/dictionary name
- `position`: 3D position in meters relative to camera (x=right, y=up, z=forward)
- `rotation_matrix`: 3x3 rotation matrix
- `corners`: Four corner points in image coordinates [top-left, top-right, bottom-right, bottom-left]
- `confidence`: Detection confidence (0-1, AprilTag only)

### 4. Get Supported Markers

Get list of all supported marker types and their options.

**Endpoint:** `GET /api/v1/supported_markers`

**Response:**
```json
{
  "marker_types": {
    "apriltag": {
      "available": true,
      "families": [
        "tag36h11",
        "tag36h10",
        "tag36h9",
        "tag25h9",
        "tag16h5",
        "tagStandard41h12"
      ],
      "default": "tag36h11"
    },
    "aruco": {
      "available": true,
      "dictionaries": [
        "DICT_4X4_50",
        "DICT_4X4_100",
        "DICT_5X5_50",
        "DICT_6X6_50",
        "DICT_7X7_50"
      ],
      "default": "DICT_4X4_50"
    }
  }
}
```

### 5. Generate Marker

Generate a marker image (ArUco only for now).

**Endpoint:** `POST /api/v1/generate_marker`

**Request Body:**
```json
{
  "marker_type": "aruco",
  "marker_id": 0,
  "size_pixels": 400,
  "aruco_dict": "DICT_4X4_50"
}
```

**Parameters:**
- `marker_type` (required): "aruco" (AprilTag generation not yet supported)
- `marker_id` (required): Marker ID number
- `size_pixels` (optional): Output image size in pixels (default: 400)
- `aruco_dict` (optional): ArUco dictionary name (default: "DICT_4X4_50")

**Response:** PNG image file

## Usage Examples

### Python Client

```python
import requests
import base64
import cv2
import json

# Server URL
API_URL = "http://127.0.0.1:5000"

# Read and encode image
image = cv2.imread("test_image.jpg")
_, buffer = cv2.imencode('.jpg', image)
image_b64 = base64.b64encode(buffer).decode('utf-8')

# Configure camera (optional, auto-configured if not set)
config_response = requests.post(f"{API_URL}/api/v1/config", json={
    "image_width": image.shape[1],
    "image_height": image.shape[0],
    "fov_degrees": 60.0
})
print("Camera configured:", config_response.json())

# Detect AprilTag markers
detect_response = requests.post(f"{API_URL}/api/v1/detect", json={
    "image": image_b64,
    "marker_type": "apriltag",
    "marker_size": 0.19,  # 190mm
    "tag_family": "tag36h11"
})

result = detect_response.json()
print(f"Detected {result['detected_count']} markers")

for detection in result['detections']:
    print(f"Marker {detection['id']}:")
    print(f"  Position: {detection['position']}")
    print(f"  Confidence: {detection['confidence']}")
```

### JavaScript/Web Client

```javascript
// Capture image from video element
const video = document.querySelector('video');
const canvas = document.createElement('canvas');
canvas.width = video.videoWidth;
canvas.height = video.videoHeight;
const ctx = canvas.getContext('2d');
ctx.drawImage(video, 0, 0);

// Convert to base64
const imageB64 = canvas.toDataURL('image/jpeg').split(',')[1];

// Detect markers
fetch('http://127.0.0.1:5000/api/v1/detect', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    image: imageB64,
    marker_type: 'apriltag',
    marker_size: 0.19,
    tag_family: 'tag36h11'
  })
})
.then(response => response.json())
.then(data => {
  console.log(`Detected ${data.detected_count} markers`);
  data.detections.forEach(detection => {
    console.log(`Marker ${detection.id} at position:`, detection.position);
  });
})
.catch(error => console.error('Error:', error));
```

### curl

```bash
# Health check
curl http://127.0.0.1:5000/health

# Get supported markers
curl http://127.0.0.1:5000/api/v1/supported_markers

# Configure camera
curl -X POST http://127.0.0.1:5000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "image_width": 1280,
    "image_height": 720,
    "fov_degrees": 60
  }'

# Detect markers (with base64-encoded image)
curl -X POST http://127.0.0.1:5000/api/v1/detect \
  -H "Content-Type: application/json" \
  -d '{
    "image": "<base64-image-data>",
    "marker_type": "apriltag",
    "marker_size": 0.19
  }'

# Generate ArUco marker
curl -X POST http://127.0.0.1:5000/api/v1/generate_marker \
  -H "Content-Type: application/json" \
  -d '{
    "marker_type": "aruco",
    "marker_id": 0,
    "size_pixels": 400
  }' \
  --output marker_0.png
```

## Multi-Marker Detection

To detect multiple markers in a single image:

```python
# Detect 4 markers
response = requests.post(f"{API_URL}/api/v1/detect", json={
    "image": image_b64,
    "marker_type": "apriltag",
    "marker_size": 0.09,  # 90mm for multi-marker setup
    "marker_count": 4,    # Expect 4 markers
    "tag_family": "tag36h11"
})

result = response.json()
print(f"Found {result['detected_count']} of {result['expected_count']} markers")
print(f"All markers found: {result['all_markers_found']}")

# Process each marker
for detection in result['detections']:
    marker_id = detection['id']
    position = detection['position']
    print(f"Marker {marker_id}: x={position['x']:.3f}, y={position['y']:.3f}, z={position['z']:.3f}")
```

## Integration with UI

The AR Engine API can be integrated with the existing web UI by:

1. **Start the API server** in the background
2. **Update UI JavaScript** to send camera frames to API
3. **Process API responses** to update 3D rendering

Example integration:

```javascript
// In your app's detection loop
async function detectWithAPI(videoElement) {
  // Capture frame
  const canvas = document.createElement('canvas');
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(videoElement, 0, 0);
  
  // Convert to base64
  const imageB64 = canvas.toDataURL('image/jpeg').split(',')[1];
  
  try {
    // Call API
    const response = await fetch('http://127.0.0.1:5000/api/v1/detect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image: imageB64,
        marker_type: document.getElementById('input-marker-type').value,
        marker_size: parseFloat(document.getElementById('input-size').value) / 1000,
        marker_count: getExpectedMarkerCount()
      })
    });
    
    const data = await response.json();
    
    if (data.status === 'success' && data.detected_count > 0) {
      // Update 3D rendering with detected poses
      updateAROverlay(data.detections);
    }
  } catch (error) {
    console.error('API detection error:', error);
  }
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK` - Successful request
- `400 Bad Request` - Invalid request parameters
- `500 Internal Server Error` - Server-side error
- `501 Not Implemented` - Feature not yet available

Error responses include an error message:

```json
{
  "error": "Description of what went wrong"
}
```

## Performance Considerations

- **Image Size**: Smaller images process faster. Consider resizing to 640x480 or 1280x720.
- **Marker Count**: More markers increase detection time slightly.
- **Network Latency**: API calls add network overhead. For real-time applications, consider running the server locally.
- **Frame Rate**: Aim for 10-30 FPS depending on use case.

## Security Considerations

- **Local Network Only**: By default, the server runs on `127.0.0.1` (localhost only).
- **Production Deployment**: For public deployment, implement:
  - Authentication (API keys, OAuth)
  - Rate limiting
  - Input validation
  - HTTPS/TLS encryption
- **CORS**: Currently enabled for all origins. Restrict in production.

## Troubleshooting

### AprilTag Detection Not Available

If you see `"apriltag": false` in the health check:

```bash
# Install AprilTag library
pip install apriltag
```

### Port Already in Use

```bash
# Use a different port
python ar_engine_api.py --port 5001
```

### Connection Refused

Make sure the server is running and accessible:

```bash
# Check if server is running
curl http://127.0.0.1:5000/health

# If using a different host, update the URL
curl http://192.168.1.100:5000/health
```

### CORS Errors in Browser

If you see CORS errors, make sure the API server is running with CORS enabled (it's enabled by default).

## Testing

### Test Script

```python
# test_ar_engine_api.py
import requests
import cv2
import base64

API_URL = "http://127.0.0.1:5000"

def test_health():
    response = requests.get(f"{API_URL}/health")
    print("Health check:", response.json())

def test_supported_markers():
    response = requests.get(f"{API_URL}/api/v1/supported_markers")
    print("Supported markers:", response.json())

def test_detection():
    # Create a test image with an ArUco marker
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker_image = cv2.aruco.generateImageMarker(aruco_dict, 0, 400)
    
    # Add some padding
    test_image = cv2.copyMakeBorder(
        marker_image, 100, 100, 100, 100,
        cv2.BORDER_CONSTANT, value=255
    )
    
    # Encode to base64
    _, buffer = cv2.imencode('.jpg', test_image)
    image_b64 = base64.b64encode(buffer).decode('utf-8')
    
    # Detect
    response = requests.post(f"{API_URL}/api/v1/detect", json={
        "image": image_b64,
        "marker_type": "aruco",
        "marker_size": 0.19
    })
    
    print("Detection result:", response.json())

if __name__ == '__main__':
    test_health()
    test_supported_markers()
    test_detection()
```

Run the test:

```bash
python test_ar_engine_api.py
```

## Next Steps

1. **Deploy the API**: Set up on a server or cloud platform
2. **Update UI**: Integrate with the web application
3. **Add Authentication**: Implement API keys for production
4. **Optimize Performance**: Profile and optimize detection speed
5. **Add Features**: Implement additional endpoints as needed

## Support

For issues, questions, or contributions, see the main project documentation in the parent directory.
