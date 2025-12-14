# Visual-Inertial Odometry (VIO) System

This directory contains a complete implementation of a loosely-coupled Visual-Inertial Odometry system for 3D measurement using AprilTags as reliable anchors.

## Overview

The VIO system fuses:
- **Visual measurements** from AprilTag detection (position and orientation)
- **Inertial measurements** from IMU sensors (accelerometer and gyroscope)
- **Extended Kalman Filter (EKF)** for optimal state estimation

This provides robust and accurate 3D pose tracking even when markers are temporarily occluded or IMU drift occurs.

## Architecture

### Components

#### 1. AprilTagDetector (`vio/apriltag_detector.py`)
- Detects AprilTags in images using the `apriltag` library
- Performs Perspective-n-Point (PnP) to estimate 3D pose
- Returns translation vector and rotation matrix relative to camera
- Supports multiple tag families (tagStandard41h12, tag36h11, etc.)

#### 2. IMUProcessor (`vio/imu_processor.py`)
- Pre-integrates high-frequency IMU measurements
- Calculates relative change in position, velocity, and orientation
- Handles bias subtraction for accelerometer and gyroscope
- Operates between consecutive image frames

#### 3. EKFFusionEngine (`vio/ekf_fusion_engine.py`)
- Implements Extended Kalman Filter for sensor fusion
- **State vector (16D):**
  - Position (3D)
  - Velocity (3D)
  - Orientation (Quaternion 4D)
  - Gyroscope bias (3D)
  - Accelerometer bias (3D)
- **Prediction step:** Uses IMU pre-integration
- **Update step:** Uses AprilTag pose measurements

#### 4. ARBridge (`vio/ar_bridge.py`)
- Streams VIO state to external AR rendering clients
- Uses UDP socket with JSON format
- Compatible with Unity, WebGL, Three.js
- Real-time pose data for 3D visualization
- Includes sample client for testing

#### 5. PoseStreamer (`vio/pose_streamer.py`)
- Lightweight pose streaming for 3D rendering
- Simple API: `stream_pose(position, quaternion)`
- Minimal JSON format: `{"pos": [x,y,z], "rot": [w,x,y,z]}`
- UDP broadcast on port 6000 (default)
- Perfect for simple 3D visualization needs

### Main Application (`main.py`)
- Demonstrates the complete VIO pipeline
- Simulates synced image and IMU data
- Processes frames through the VIO system
- Prints globally-referenced 3D pose (X, Y, Z)

## Installation

### Prerequisites

Python 3.7 or higher is required.

### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `numpy` - Numerical operations
- `scipy` - Rotation operations and linear algebra
- `opencv-python` - Computer vision and image processing
- `apriltag` - AprilTag detection library
- `matplotlib` - Optional, for visualization

### Troubleshooting Installation

#### AprilTag Library
If you have trouble installing the `apriltag` library:

```bash
# On Ubuntu/Debian
sudo apt-get install python3-dev

# On macOS
brew install cmake

# Then install apriltag
pip install apriltag
```

Alternatively, you can build from source:
```bash
git clone https://github.com/AprilRobotics/apriltag.git
cd apriltag
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
cd ..
pip install apriltag/
```

## Usage

### Quick Start - Simulation

Run the simulation with synthetic data:

```bash
python main.py
```

This will:
1. Initialize the VIO system
2. Generate synthetic IMU data
3. Process frames (without real AprilTags)
4. Display pose estimates
5. Print final results

### Using with Real Data

To use the VIO system with real camera and IMU data:

#### 1. Camera Calibration

First, calibrate your camera to get the intrinsic matrix:

```python
import numpy as np
import cv2

# Example calibrated camera matrix
camera_matrix = np.array([
    [fx, 0, cx],
    [0, fy, cy],
    [0, 0, 1]
], dtype=np.float32)

# Example distortion coefficients
dist_coeffs = np.array([k1, k2, p1, p2, k3], dtype=np.float32)
```

Use OpenCV's calibration tools or this tutorial:
https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html

#### 2. Print AprilTag Markers

Generate AprilTag markers:

**Option A: Use the built-in generator in the web app**
1. Open the Clearance Wizard web app
2. Click "Get Markers" → "Generate AprilTag"
3. Select family: tag36h11 (recommended)
4. Choose size: 190mm recommended
5. Download and print

**Option B: Online generator**
- Visit: https://github.com/AprilRobotics/apriltag-imgs
- Download pre-generated tags
- Print at appropriate size

**Important:** Measure the BLACK SQUARE AREA ONLY (exclude white border)

#### 3. Capture Data

```python
import cv2
from vio import AprilTagDetector, IMUProcessor, EKFFusionEngine

# Initialize system
tag_size = 0.19  # 190mm in meters
detector = AprilTagDetector(tag_size, camera_matrix, dist_coeffs)
imu_processor = IMUProcessor()
ekf = EKFFusionEngine()

# Capture from camera
cap = cv2.VideoCapture(0)

while True:
    # Read frame
    ret, frame = cap.read()
    if not ret:
        break
    
    # Get IMU data (pseudo-code - replace with actual IMU reading)
    gyro_data = read_gyroscope()  # List of (timestamp, reading) tuples
    accel_data = read_accelerometer()  # List of (timestamp, reading) tuples
    
    # Detect AprilTags
    detections = detector.detect(frame)
    
    # Pre-integrate IMU
    if len(gyro_data) > 0:
        state = ekf.get_state()
        delta_pos, delta_vel, delta_rot = imu_processor.preintegrate(
            gyro_data, accel_data, state['orientation']
        )
        
        # EKF prediction
        ekf.predict(delta_pos, delta_vel, delta_rot, dt=0.033)
    
    # EKF update with visual measurements
    if len(detections) > 0:
        measured_pos = detections[0]['translation']
        measured_rot = Rotation.from_matrix(detections[0]['rotation_matrix'])
        ekf.update(measured_pos, measured_rot)
    
    # Get pose estimate
    pose = ekf.get_state()
    print(f"Position: {pose['position']}")
    
    # Visualize
    if len(detections) > 0:
        vis_frame = detector.visualize_detections(frame, detections)
        cv2.imshow('VIO System', vis_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## API Reference

### AprilTagDetector

```python
from vio import AprilTagDetector

# Initialize
detector = AprilTagDetector(
    tag_size=0.19,              # Physical tag size in meters
    camera_matrix=K,            # 3x3 camera intrinsic matrix
    dist_coeffs=D,              # Distortion coefficients
    tag_family='tagStandard41h12'  # Tag family
)

# Detect tags in image
detections = detector.detect(image)

# Each detection contains:
# - tag_id: Unique identifier
# - center: 2D center position
# - corners: 4x2 corner positions
# - translation: 3D position [x, y, z]
# - rotation_matrix: 3x3 rotation matrix
# - rotation_vector: 3D rotation vector
```

### IMUProcessor

```python
from vio import IMUProcessor

# Initialize
imu = IMUProcessor(
    gyro_bias=np.zeros(3),    # Initial gyroscope bias
    accel_bias=np.zeros(3),   # Initial accelerometer bias
    gravity=np.array([0, 0, -9.81])  # Gravity vector
)

# Pre-integrate IMU measurements
delta_pos, delta_vel, delta_rot = imu.preintegrate(
    gyro_measurements=[(t1, gyro1), (t2, gyro2), ...],
    accel_measurements=[(t1, accel1), (t2, accel2), ...],
    initial_rotation=current_orientation
)
```

### EKFFusionEngine

```python
from vio import EKFFusionEngine

# Initialize
ekf = EKFFusionEngine()

# Prediction step (using IMU)
ekf.predict(delta_position, delta_velocity, delta_rotation, dt)

# Update step (using AprilTag measurement)
ekf.update(measured_position, measured_rotation)

# Get current state
state = ekf.get_state()
# Returns:
# - position: 3D position
# - velocity: 3D velocity
# - orientation: Rotation object
# - quaternion: [w, x, y, z]
# - gyro_bias: Gyroscope bias
# - accel_bias: Accelerometer bias
```

### ARBridge

```python
from vio import ARBridge

# Initialize AR bridge for streaming to rendering client
bridge = ARBridge(
    host='127.0.0.1',      # Localhost
    port=9999              # UDP port
)

# Stream EKF state to AR client
state = ekf.get_state()
bridge.send_ekf_state(state, timestamp=time.time())

# Or send individual components
bridge.send_state(
    position=state['position'],
    velocity=state['velocity'],
    orientation=state['orientation'],
    quaternion=state['quaternion'],
    gyro_bias=state['gyro_bias'],
    accel_bias=state['accel_bias'],
    timestamp=time.time(),
    extra_data={'frame': 123, 'detections': 1}
)

# Close when done
bridge.close()

# Or use as context manager
with ARBridge(port=9999) as bridge:
    bridge.send_ekf_state(state)
```

## Configuration

### Tuning EKF Parameters

You can tune the EKF by adjusting noise covariances:

```python
# Process noise (how much we trust the motion model)
process_noise = np.eye(16)
process_noise[0:3, 0:3] *= 0.01    # Position
process_noise[3:6, 3:6] *= 0.01    # Velocity
process_noise[6:10, 6:10] *= 0.001 # Orientation
process_noise[10:13, 10:13] *= 0.0001  # Gyro bias
process_noise[13:16, 13:16] *= 0.001   # Accel bias

# Measurement noise (how much we trust AprilTag measurements)
measurement_noise = np.eye(7)
measurement_noise[0:3, 0:3] *= 0.01   # Position (1cm std)
measurement_noise[3:7, 3:7] *= 0.001  # Orientation

ekf = EKFFusionEngine(
    process_noise=process_noise,
    measurement_noise=measurement_noise
)
```

### Camera Parameters

For best results, properly calibrate your camera:

```bash
# Using OpenCV calibration sample
python camera_calibration.py \
    --input chessboard_images/ \
    --output camera_params.yaml
```

## Testing

The implementation includes synthetic data generation for testing:

```python
from vio import IMUProcessor

# Generate simulated IMU data
gyro_data, accel_data = IMUProcessor.simulate_imu_data(
    duration=1.0,           # 1 second
    frequency=200.0,        # 200 Hz
    motion_type='circular'  # 'stationary', 'linear', or 'circular'
)
```

## Performance Considerations

### Frame Rate
- **Camera:** 30 FPS typical, 60 FPS recommended for fast motion
- **IMU:** 200 Hz typical, 400+ Hz for high-accuracy applications

### Computational Cost
- **AprilTag detection:** ~10-30ms per frame (depends on resolution)
- **IMU pre-integration:** <1ms for typical rates
- **EKF update:** <1ms

### Accuracy
- **Position:** ~1cm with good tag visibility
- **Orientation:** ~1-2 degrees with good tag visibility
- **IMU drift:** Bounded by regular visual updates

## Limitations

1. **Requires visible AprilTags:** System degrades to pure IMU when no tags visible
2. **Camera calibration:** Accuracy depends on calibration quality
3. **Lighting conditions:** Poor lighting affects tag detection
4. **Tag size:** Smaller tags harder to detect at distance

## AR Visualization

### Streaming to 3D Rendering Clients

The ARBridge component enables real-time streaming of VIO pose data to external 3D rendering applications for Augmented Reality visualization.

#### Quick Start

**Example: Streaming VIO data**

```bash
# Run the AR bridge example
python example_ar_bridge.py --duration 10 --port 9999

# In another terminal, run the sample client
python example_ar_bridge.py --client --port 9999
```

#### Integration with Unity/WebGL/Three.js

The ARBridge streams JSON data via UDP that can be consumed by any rendering engine:

**JSON Message Format:**
```json
{
  "frame": 123,
  "timestamp": 1234567890.123,
  "pose": {
    "position": {"x": 1.5, "y": 2.0, "z": 0.5},
    "orientation": {
      "quaternion": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
      "euler": {"roll": 0.0, "pitch": 0.0, "yaw": 0.0}
    }
  },
  "velocity": {"x": 0.1, "y": 0.2, "z": 0.0},
  "biases": {
    "gyroscope": {"x": 0.01, "y": 0.02, "z": 0.03},
    "accelerometer": {"x": 0.001, "y": 0.002, "z": 0.003}
  },
  "extra": {
    "detections": 1,
    "has_visual_update": true
  }
}
```

#### Use Cases

1. **3D Model Overlay:** Place virtual 3D models (e.g., boiler controls) aligned with real-world objects
2. **Measurement Visualization:** Show distance measurements and annotations in AR
3. **System Monitoring:** Visualize clearance zones and safety boundaries
4. **Training Applications:** Interactive AR instructions overlaid on equipment

#### Example: Unity Client (C#)

```csharp
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;

public class VIOReceiver : MonoBehaviour
{
    private UdpClient udpClient;
    public Transform targetObject;
    
    void Start()
    {
        udpClient = new UdpClient(9999);
        udpClient.BeginReceive(ReceiveCallback, null);
    }
    
    void ReceiveCallback(IAsyncResult ar)
    {
        IPEndPoint endpoint = new IPEndPoint(IPAddress.Any, 9999);
        byte[] data = udpClient.EndReceive(ar, ref endpoint);
        string json = Encoding.UTF8.GetString(data);
        
        // Parse JSON and update object transform
        VIOData vioData = JsonUtility.FromJson<VIOData>(json);
        targetObject.position = new Vector3(
            vioData.pose.position.x,
            vioData.pose.position.y,
            vioData.pose.position.z
        );
        targetObject.rotation = new Quaternion(
            vioData.pose.orientation.quaternion.x,
            vioData.pose.orientation.quaternion.y,
            vioData.pose.orientation.quaternion.z,
            vioData.pose.orientation.quaternion.w
        );
        
        udpClient.BeginReceive(ReceiveCallback, null);
    }
}
```

#### Example: Three.js Client (JavaScript)

```javascript
// WebSocket or UDP-over-WebRTC for browser
const socket = new WebSocket('ws://localhost:9999');

socket.onmessage = (event) => {
  const vioData = JSON.parse(event.data);
  
  // Update Three.js object
  object.position.set(
    vioData.pose.position.x,
    vioData.pose.position.y,
    vioData.pose.position.z
  );
  
  object.quaternion.set(
    vioData.pose.orientation.quaternion.x,
    vioData.pose.orientation.quaternion.y,
    vioData.pose.orientation.quaternion.z,
    vioData.pose.orientation.quaternion.w
  );
};
```

## Custom Fiducial Markers

### Beautifying Markers for User-Facing Applications

Standard AprilTags are highly robust but can appear industrial. For consumer applications, you may want more aesthetically pleasing markers.

**📖 See [CUSTOM_MARKERS.md](CUSTOM_MARKERS.md) for a comprehensive guide** covering:

- Custom template markers (VuMark, JuMarker)
- Deep learning-based markers (DeepTag)
- Color-based markers
- Invisible markers (IR/UV)
- Hybrid approaches (ChArUco)

#### Quick Recommendations

**For immediate use:**
- Continue with AprilTags (tag36h11 family recommended)
- Enhance presentation with frames, branding, and design integration
- Print on high-quality materials for professional appearance

**For future enhancement:**
- Research color-based markers for branded applications
- Consider custom template markers for specific use cases
- Investigate deep learning approaches for maximum flexibility

#### Key Principle

Any custom marker system should maintain the same API as AprilTagDetector:

```python
# Drop-in replacement for AprilTagDetector
detector = CustomMarkerDetector(
    marker_size=0.19,
    camera_matrix=camera_matrix,
    dist_coeffs=dist_coeffs
)

# Same detection API
detections = detector.detect(image)
# Returns same format: tag_id, translation, rotation_matrix, etc.
```

This ensures the VIO system works seamlessly with any marker type.

## Future Improvements

1. **Multi-tag fusion:** Use multiple tags simultaneously for better accuracy
2. **Loop closure:** Detect when returning to known locations
3. **Map building:** Build persistent map of tag locations
4. **Adaptive tuning:** Automatically tune EKF parameters
5. **Mobile deployment:** Port to iOS/Android for real-time performance
6. **Custom markers:** Implement aesthetic marker alternatives (color, DeepTag)
7. **3D visualization:** Native AR rendering within Python application

## References

### Papers
- Mourikis, A. I., & Roumeliotis, S. I. (2007). "A multi-state constraint Kalman filter for vision-aided inertial navigation." ICRA.
- Forster, C., et al. (2017). "On-Manifold Preintegration for Real-Time Visual-Inertial Odometry." IEEE TRO.
- Wang, J., & Olson, E. (2016). "AprilTag 2: Efficient and robust fiducial detection." IROS.

### Libraries
- AprilTag: https://github.com/AprilRobotics/apriltag
- OpenCV: https://opencv.org/
- SciPy: https://scipy.org/

### Tutorials
- Camera calibration: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
- Kalman filtering: https://www.kalmanfilter.net/
- Quaternion math: https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation

## License

This implementation is part of the Clearance Wizard project. See the main README for license information.

## Support

For questions or issues:
1. Check the documentation above
2. Review the inline code comments (NumPy style docstrings)
3. Open an issue on GitHub

## Contributing

Contributions are welcome! Areas for improvement:
- Better IMU bias estimation
- Adaptive noise covariances
- Multi-tag fusion algorithms
- Performance optimizations
- Mobile platform support
