# ARBridge - Streaming VIO to AR Clients

## Overview

The ARBridge component provides real-time streaming of Visual-Inertial Odometry state data to external 3D rendering applications via UDP socket in JSON format.

This enables the VIO system to power Augmented Reality experiences in Unity, WebGL, Three.js, and other rendering engines.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     VIO System (Python)                         │
│                                                                  │
│  ┌──────────────┐   ┌──────────┐   ┌──────────────────┐       │
│  │ AprilTag     │──▶│   IMU    │──▶│ EKF Fusion      │       │
│  │ Detector     │   │Processor │   │ Engine          │       │
│  └──────────────┘   └──────────┘   └────────┬─────────┘       │
│                                              │                  │
│                                              ▼                  │
│                                     ┌────────────────┐          │
│                                     │   ARBridge     │          │
│                                     │  (UDP/JSON)    │          │
│                                     └────────┬───────┘          │
└──────────────────────────────────────────────┼──────────────────┘
                                               │ UDP Socket
                                               │ Port 9999
                                               ▼
                        ┌──────────────────────────────────────┐
                        │    3D Rendering Client               │
                        │  (Unity / WebGL / Three.js)          │
                        │                                      │
                        │  • Receives pose data via UDP/JSON  │
                        │  • Updates 3D object transforms      │
                        │  • Renders AR visualization          │
                        └──────────────────────────────────────┘
```

## Key Features

### Real-Time Streaming
- **Low Latency:** UDP protocol for minimal delay
- **High Frequency:** Supports 30+ FPS streaming
- **Reliable:** Error handling and connection monitoring

### Universal Format
- **JSON Messages:** Easy to parse in any language
- **Structured Data:** Organized hierarchy for easy access
- **Flexible:** Support for custom extra data fields

### Easy Integration
- **Drop-in Component:** Minimal code to add to existing VIO
- **Context Manager:** Automatic resource cleanup
- **Sample Client:** Built-in test client for validation

## Quick Start

### Basic Usage

```python
from vio import EKFFusionEngine, ARBridge

# Create EKF and ARBridge
ekf = EKFFusionEngine()
bridge = ARBridge(host='127.0.0.1', port=9999)

# In your main loop:
while running:
    # ... VIO processing ...
    
    # Get current state
    state = ekf.get_state()
    
    # Stream to AR client
    bridge.send_ekf_state(state, timestamp=time.time())

# Clean up
bridge.close()
```

### Context Manager Usage

```python
with ARBridge(port=9999) as bridge:
    while running:
        state = ekf.get_state()
        bridge.send_ekf_state(state)
```

### Testing the Connection

**Terminal 1: Start receiver**
```bash
python -c "from vio import ARBridge; ARBridge.create_sample_client(port=9999, duration=30)"
```

**Terminal 2: Run VIO with streaming**
```bash
python example_ar_bridge.py --duration 20 --port 9999
```

## API Reference

### ARBridge Class

#### Constructor

```python
ARBridge(
    host: str = '127.0.0.1',
    port: int = 9999,
    target_host: Optional[str] = None,
    target_port: Optional[int] = None
)
```

**Parameters:**
- `host`: IP address to bind to (usually '127.0.0.1' for localhost)
- `port`: UDP port to send data to
- `target_host`: Target IP (if different from host)
- `target_port`: Target port (if different from port)

**Example:**
```python
# Local testing
bridge = ARBridge(port=9999)

# Remote client
bridge = ARBridge(target_host='192.168.1.100', target_port=9999)
```

#### send_ekf_state()

```python
send_ekf_state(
    ekf_state: dict,
    timestamp: Optional[float] = None,
    extra_data: Optional[dict] = None
) -> bool
```

Convenience method that accepts the dictionary format from `EKFFusionEngine.get_state()`.

**Parameters:**
- `ekf_state`: Dictionary from `ekf.get_state()`
- `timestamp`: Timestamp in seconds (optional)
- `extra_data`: Additional data to include (optional)

**Returns:**
- `bool`: True if sent successfully, False otherwise

**Example:**
```python
state = ekf.get_state()
success = bridge.send_ekf_state(
    state,
    timestamp=time.time(),
    extra_data={'frame': 123, 'detections': 2}
)
```

#### send_state()

```python
send_state(
    position: np.ndarray,
    velocity: np.ndarray,
    orientation: Rotation,
    quaternion: np.ndarray,
    gyro_bias: np.ndarray,
    accel_bias: np.ndarray,
    timestamp: Optional[float] = None,
    extra_data: Optional[dict] = None
) -> bool
```

Send VIO state with individual components.

**Parameters:**
- `position`: 3D position [x, y, z] in meters
- `velocity`: 3D velocity [vx, vy, vz] in m/s
- `orientation`: scipy Rotation object
- `quaternion`: [w, x, y, z] quaternion
- `gyro_bias`: [bgx, bgy, bgz] in rad/s
- `accel_bias`: [bax, bay, baz] in m/s²
- `timestamp`: Timestamp in seconds
- `extra_data`: Additional data dictionary

**Returns:**
- `bool`: True if sent successfully

#### close()

```python
close()
```

Close the UDP socket and clean up resources.

**Example:**
```python
bridge.close()
```

### Static Methods

#### create_sample_client()

```python
ARBridge.create_sample_client(
    port: int = 9999,
    duration: float = 10.0,
    host: str = '127.0.0.1'
)
```

Create a sample UDP client to receive and display AR data. Useful for testing.

**Parameters:**
- `port`: Port to listen on
- `duration`: How long to run (seconds)
- `host`: Host address to bind to (default: '127.0.0.1' for localhost only, use '0.0.0.0' for all interfaces)

**Example:**
```bash
# Listen on localhost only (secure)
python -c "from vio import ARBridge; ARBridge.create_sample_client(port=9999, duration=30)"

# Listen on all interfaces (for remote connections)
python -c "from vio import ARBridge; ARBridge.create_sample_client(port=9999, duration=30, host='0.0.0.0')"
```

## JSON Message Format

### Complete Message Structure

```json
{
  "frame": 123,
  "timestamp": 1234567890.123,
  "pose": {
    "position": {
      "x": 1.5,
      "y": 2.0,
      "z": 0.5
    },
    "orientation": {
      "quaternion": {
        "w": 1.0,
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
      },
      "euler": {
        "roll": 0.0,
        "pitch": 0.0,
        "yaw": 45.0
      }
    }
  },
  "velocity": {
    "x": 0.1,
    "y": 0.2,
    "z": 0.0
  },
  "biases": {
    "gyroscope": {
      "x": 0.01,
      "y": 0.02,
      "z": 0.03
    },
    "accelerometer": {
      "x": 0.001,
      "y": 0.002,
      "z": 0.003
    }
  },
  "extra": {
    "detections": 1,
    "has_visual_update": true,
    "detected_tag_id": 0
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `frame` | int | Sequential frame counter |
| `timestamp` | float | Unix timestamp in seconds |
| `pose.position` | object | 3D position in meters |
| `pose.orientation.quaternion` | object | Unit quaternion (w, x, y, z) |
| `pose.orientation.euler` | object | Euler angles in degrees (roll, pitch, yaw) |
| `velocity` | object | 3D velocity in m/s |
| `biases.gyroscope` | object | Gyroscope bias in rad/s |
| `biases.accelerometer` | object | Accelerometer bias in m/s² |
| `extra` | object | Optional custom data |

## Client Implementations

### Unity (C#)

#### VIOReceiver.cs

```csharp
using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;

[Serializable]
public class VIOPosition
{
    public float x, y, z;
}

[Serializable]
public class VIOQuaternion
{
    public float w, x, y, z;
}

[Serializable]
public class VIOOrientation
{
    public VIOQuaternion quaternion;
}

[Serializable]
public class VIOPose
{
    public VIOPosition position;
    public VIOOrientation orientation;
}

[Serializable]
public class VIOData
{
    public int frame;
    public float timestamp;
    public VIOPose pose;
}

public class VIOReceiver : MonoBehaviour
{
    [Header("Network Settings")]
    public int udpPort = 9999;
    
    [Header("Target Object")]
    public Transform targetObject;
    
    [Header("Coordinate Conversion")]
    public bool swapYZ = true;  // Unity uses Y-up, VIO might use Z-up
    
    private UdpClient udpClient;
    private VIOData latestData;
    private bool hasNewData = false;
    
    void Start()
    {
        try
        {
            udpClient = new UdpClient(udpPort);
            udpClient.BeginReceive(ReceiveCallback, null);
            Debug.Log($"VIOReceiver started on port {udpPort}");
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to start UDP client: {e.Message}");
        }
    }
    
    void ReceiveCallback(IAsyncResult ar)
    {
        try
        {
            IPEndPoint endpoint = new IPEndPoint(IPAddress.Any, udpPort);
            byte[] data = udpClient.EndReceive(ar, ref endpoint);
            string json = Encoding.UTF8.GetString(data);
            
            // Parse JSON
            latestData = JsonUtility.FromJson<VIOData>(json);
            hasNewData = true;
            
            // Continue receiving
            udpClient.BeginReceive(ReceiveCallback, null);
        }
        catch (Exception e)
        {
            Debug.LogError($"Error receiving data: {e.Message}");
        }
    }
    
    void Update()
    {
        if (hasNewData && targetObject != null && latestData != null)
        {
            // Update position
            Vector3 position = new Vector3(
                latestData.pose.position.x,
                swapYZ ? latestData.pose.position.z : latestData.pose.position.y,
                swapYZ ? latestData.pose.position.y : latestData.pose.position.z
            );
            targetObject.position = position;
            
            // Update rotation
            Quaternion rotation = new Quaternion(
                latestData.pose.orientation.quaternion.x,
                swapYZ ? latestData.pose.orientation.quaternion.z : latestData.pose.orientation.quaternion.y,
                swapYZ ? latestData.pose.orientation.quaternion.y : latestData.pose.orientation.quaternion.z,
                latestData.pose.orientation.quaternion.w
            );
            targetObject.rotation = rotation;
            
            hasNewData = false;
        }
    }
    
    void OnApplicationQuit()
    {
        if (udpClient != null)
        {
            udpClient.Close();
        }
    }
}
```

#### Usage in Unity

1. Create a new C# script `VIOReceiver.cs` with the code above
2. Attach to a GameObject in your scene
3. Assign the target object to transform (e.g., a 3D model)
4. Run the VIO system with ARBridge
5. Play the Unity scene

### Three.js (JavaScript)

#### VIOClient.js

```javascript
class VIOClient {
    constructor(wsUrl = 'ws://localhost:9999') {
        this.wsUrl = wsUrl;
        this.socket = null;
        this.onDataCallback = null;
        this.latestData = null;
        this.frameCount = 0;
    }
    
    connect() {
        return new Promise((resolve, reject) => {
            this.socket = new WebSocket(this.wsUrl);
            
            this.socket.onopen = () => {
                console.log('VIO Client connected');
                resolve();
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                reject(error);
            };
            
            this.socket.onmessage = (event) => {
                try {
                    this.latestData = JSON.parse(event.data);
                    this.frameCount++;
                    
                    if (this.onDataCallback) {
                        this.onDataCallback(this.latestData);
                    }
                } catch (e) {
                    console.error('Error parsing VIO data:', e);
                }
            };
        });
    }
    
    onData(callback) {
        this.onDataCallback = callback;
    }
    
    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }
    
    getLatestData() {
        return this.latestData;
    }
}

// Usage example with Three.js
const vioClient = new VIOClient('ws://localhost:9999');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();

// Create object to control
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// Connect and receive VIO data
vioClient.connect().then(() => {
    vioClient.onData((data) => {
        // Update cube position
        cube.position.set(
            data.pose.position.x,
            data.pose.position.y,
            data.pose.position.z
        );
        
        // Update cube rotation
        cube.quaternion.set(
            data.pose.orientation.quaternion.x,
            data.pose.orientation.quaternion.y,
            data.pose.orientation.quaternion.z,
            data.pose.orientation.quaternion.w
        );
    });
});

// Render loop
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();
```

**Note:** WebSocket support requires a bridge since UDP is not directly available in browsers. Consider using:
- WebRTC Data Channels
- WebSocket-to-UDP bridge server
- HTTP SSE (Server-Sent Events)

### Python Client

#### Simple receiver example

```python
import socket
import json
import time

def receive_vio_data(port=9999, duration=10.0):
    """Receive and display VIO data."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    sock.settimeout(1.0)
    
    print(f"Listening on port {port}...")
    start_time = time.time()
    
    while (time.time() - start_time) < duration:
        try:
            data, addr = sock.recvfrom(4096)
            message = json.loads(data.decode('utf-8'))
            
            pos = message['pose']['position']
            print(f"Frame {message['frame']}: "
                  f"Position = ({pos['x']:.3f}, {pos['y']:.3f}, {pos['z']:.3f})")
        except socket.timeout:
            continue
    
    sock.close()

if __name__ == '__main__':
    receive_vio_data(duration=30)
```

## Use Cases

### 1. 3D Model Overlay

Place virtual 3D models aligned with real-world objects:

```python
# VIO anchored to AprilTag on boiler
# Unity receives pose and renders boiler control overlay
extra_data = {
    'anchor_tag_id': 0,
    'model_name': 'boiler_controls',
    'scale': 1.0
}
bridge.send_ekf_state(state, extra_data=extra_data)
```

### 2. Distance Measurement Visualization

Show measurement annotations in AR:

```python
extra_data = {
    'measurement_type': 'clearance',
    'distance': 0.45,  # meters
    'min_clearance': 0.30
}
bridge.send_ekf_state(state, extra_data=extra_data)
```

### 3. Safety Zone Visualization

Display safety boundaries and restricted areas:

```python
extra_data = {
    'safety_zones': [
        {'type': 'danger', 'radius': 0.5},
        {'type': 'caution', 'radius': 1.0}
    ]
}
bridge.send_ekf_state(state, extra_data=extra_data)
```

### 4. Training and Instructions

Provide step-by-step AR guidance:

```python
extra_data = {
    'instruction_step': 3,
    'instruction_text': 'Connect wire to terminal A',
    'highlight_objects': ['terminal_a', 'wire_red']
}
bridge.send_ekf_state(state, extra_data=extra_data)
```

## Performance Tuning

### Network Settings

**Localhost (Testing):**
```python
bridge = ARBridge(host='127.0.0.1', port=9999)
```

**LAN (Production):**
```python
bridge = ARBridge(target_host='192.168.1.100', port=9999)
```

### Message Size Optimization

Average message size: ~300-500 bytes
At 30 FPS: ~10-15 KB/s bandwidth

**Reduce size by:**
- Limiting decimal precision
- Omitting unnecessary fields
- Compressing extra_data

### Frequency Control

```python
# Only send at specific intervals
last_send_time = 0
send_interval = 1.0 / 30  # 30 Hz

if (time.time() - last_send_time) >= send_interval:
    bridge.send_ekf_state(state)
    last_send_time = time.time()
```

### Error Handling

```python
try:
    success = bridge.send_ekf_state(state)
    if not success:
        print("Warning: Failed to send VIO data")
except Exception as e:
    print(f"Error sending VIO data: {e}")
```

## Troubleshooting

### No Data Received

1. **Check firewall:** Ensure UDP port is open
2. **Verify IP/Port:** Confirm client listening on correct address
3. **Test locally:** Use 127.0.0.1 first
4. **Check network:** Ping between devices

### Data Corruption

1. **Increase buffer size:** Use larger UDP buffer
2. **Check message size:** Ensure < 4096 bytes
3. **Validate JSON:** Check for serialization errors

### High Latency

1. **Use UDP:** Ensure not using TCP
2. **Reduce message size:** Remove unnecessary data
3. **Lower frequency:** Send at 20 Hz instead of 30 Hz
4. **Check network:** Look for congestion

## Best Practices

### 1. Always Use Context Manager

```python
with ARBridge(port=9999) as bridge:
    # Your code here
    pass
# Automatically closed
```

### 2. Include Timestamps

```python
bridge.send_ekf_state(state, timestamp=time.time())
```

### 3. Add Metadata

```python
extra_data = {
    'frame': frame_count,
    'detections': num_detections,
    'quality': detection_quality
}
bridge.send_ekf_state(state, extra_data=extra_data)
```

### 4. Handle Errors Gracefully

```python
if not bridge.send_ekf_state(state):
    # Log error but continue
    error_count += 1
```

### 5. Monitor Performance

```python
start = time.time()
bridge.send_ekf_state(state)
send_time = (time.time() - start) * 1000
if send_time > 1.0:  # > 1ms
    print(f"Warning: Slow send time: {send_time:.2f}ms")
```

## Examples

See the following files for complete examples:
- `test_ar_bridge.py` - Comprehensive test suite
- `example_ar_bridge.py` - Full VIO with AR streaming
- `main.py` - Basic VIO (can be extended with ARBridge)

## License

Part of the Clearance Wizard VIO project.

---

*For questions or issues, see the main README or open a GitHub issue.*
