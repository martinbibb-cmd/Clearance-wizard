# PoseStreamer - Simple Pose Streaming for 3D Rendering

## Overview

The `PoseStreamer` class provides a lightweight, simple interface for streaming camera pose data (position and orientation) from the VIO system to external 3D rendering applications. It uses UDP sockets for low-latency, real-time transmission with a minimal JSON format.

**Key Features:**
- 🚀 **Ultra-simple API**: Just `stream_pose(position, quaternion)`
- ⚡ **Low latency**: UDP protocol with minimal overhead
- 📦 **Lightweight**: Simple JSON format: `{"pos": [x,y,z], "rot": [w,x,y,z]}`
- 🔌 **Easy integration**: Drop-in component for existing VIO systems
- 🎯 **Default port 6000**: Distinct from ARBridge (port 9999)

## Quick Start

### Basic Usage

```python
from vio import PoseStreamer
import numpy as np

# Create streamer
streamer = PoseStreamer(port=6000)

# Your VIO loop
while running:
    # ... VIO processing ...
    
    # Get pose from your system
    position = np.array([x, y, z])
    quaternion = np.array([w, x, y, z])
    
    # Stream to 3D renderer
    streamer.stream_pose(position, quaternion)

# Clean up
streamer.close()
```

### Context Manager (Recommended)

```python
with PoseStreamer(port=6000) as streamer:
    while running:
        position, quaternion = get_current_pose()
        streamer.stream_pose(position, quaternion)
```

## Integration with VIO System

### Complete Example

```python
from vio import AprilTagDetector, IMUProcessor, EKFFusionEngine, PoseStreamer
import numpy as np

# Initialize VIO components
detector = AprilTagDetector(tag_size=0.19, camera_matrix=K, dist_coeffs=D)
imu_processor = IMUProcessor()
ekf = EKFFusionEngine()

# Initialize PoseStreamer - THIS IS THE ONLY ADDITION!
pose_streamer = PoseStreamer(port=6000)

# Main VIO loop
for frame in camera_stream:
    # IMU prediction
    if last_time is not None:
        delta_pos, delta_vel, delta_rot = imu_processor.preintegrate(
            gyro_data, accel_data, ekf.get_state()['orientation']
        )
        ekf.predict(delta_pos, delta_vel, delta_rot, dt)
    
    # Visual update
    detections = detector.detect(frame)
    if detections:
        ekf.update(detections[0]['translation'], 
                   Rotation.from_matrix(detections[0]['rotation_matrix']))
    
    # Get current state
    state = ekf.get_state()
    
    # ===== STREAM POSE TO 3D RENDERER =====
    pose_streamer.stream_pose(state['position'], state['quaternion'])
    # ======================================

# Clean up
pose_streamer.close()
```

## API Reference

### Class: `PoseStreamer`

Streams camera pose to external 3D rendering clients via UDP/JSON.

#### Constructor

```python
PoseStreamer(port=6000, host='127.0.0.1')
```

**Parameters:**
- `port` (int): UDP port for broadcasting. Default: 6000
- `host` (str): Target IP address. Default: '127.0.0.1' (localhost)

**Example:**
```python
# Local streaming (default)
streamer = PoseStreamer()

# Custom port
streamer = PoseStreamer(port=7000)

# Remote streaming (use with caution!)
streamer = PoseStreamer(port=6000, host='192.168.1.100')
```

#### Method: `stream_pose`

```python
stream_pose(position, quaternion) -> bool
```

Stream the current camera pose to the rendering client.

**Parameters:**
- `position` (array-like): 3D position [x, y, z] in meters
- `quaternion` (array-like): Orientation quaternion [w, x, y, z]

**Returns:**
- `bool`: True if sent successfully, False otherwise

**Accepts:**
- NumPy arrays: `np.array([x, y, z])`
- Lists: `[x, y, z]`
- Tuples: `(x, y, z)`

**Example:**
```python
# With NumPy arrays
position = np.array([1.0, 2.0, 3.0])
quaternion = np.array([1.0, 0.0, 0.0, 0.0])
streamer.stream_pose(position, quaternion)

# With lists
streamer.stream_pose([1.0, 2.0, 3.0], [1.0, 0.0, 0.0, 0.0])

# With tuples
streamer.stream_pose((1.0, 2.0, 3.0), (1.0, 0.0, 0.0, 0.0))
```

#### Method: `close`

```python
close()
```

Close the UDP socket and clean up resources.

**Example:**
```python
streamer = PoseStreamer()
# ... use streamer ...
streamer.close()
```

#### Static Method: `create_sample_receiver`

```python
PoseStreamer.create_sample_receiver(port=6000, duration=10.0, host='127.0.0.1')
```

Create a sample UDP receiver to display streamed pose data (for testing).

**Parameters:**
- `port` (int): Port to listen on. Default: 6000
- `duration` (float): Duration to run in seconds. Default: 10.0
- `host` (str): Host address to bind to. Default: '127.0.0.1'

**Example:**
```python
# Run in a separate terminal to receive data
from vio import PoseStreamer
PoseStreamer.create_sample_receiver(port=6000, duration=30)
```

## JSON Message Format

The PoseStreamer sends pose data in a simple, minimal JSON format:

```json
{
  "pos": [x, y, z],
  "rot": [w, x, y, z]
}
```

**Example message:**
```json
{
  "pos": [1.5, 2.3, 0.8],
  "rot": [0.924, 0.0, 0.0, 0.383]
}
```

**Field descriptions:**
- `pos`: 3D position array [x, y, z] in meters
- `rot`: Quaternion array [w, x, y, z] representing orientation

## Testing Your Stream

### Step 1: Start the Receiver (Terminal 1)

```bash
python -c "from vio import PoseStreamer; PoseStreamer.create_sample_receiver(port=6000, duration=60)"
```

### Step 2: Run Your VIO System (Terminal 2)

```bash
python example_pose_streamer.py
```

You should see pose updates printed in the receiver terminal:

```
Frame 1:
  Position: [1.500, 2.300, 0.800]
  Quaternion: [0.924, 0.000, 0.000, 0.383]

Frame 2:
  Position: [1.502, 2.305, 0.801]
  Quaternion: [0.923, 0.000, 0.000, 0.384]
...
```

## Performance

The PoseStreamer is designed for real-time, high-frequency streaming:

- **Latency**: < 1ms (UDP overhead only)
- **Throughput**: 45,000+ Hz on typical hardware
- **Message size**: ~50 bytes per message
- **Network bandwidth**: ~1.2 KB/s @ 30 Hz

Tested on standard hardware with Python 3.8+.

## Receiving in 3D Applications

### Unity (C#)

```csharp
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using Newtonsoft.Json.Linq;

public class PoseReceiver : MonoBehaviour
{
    private UdpClient udpClient;
    public GameObject trackedObject;
    
    void Start()
    {
        udpClient = new UdpClient(6000);
        udpClient.BeginReceive(OnReceive, null);
    }
    
    void OnReceive(IAsyncResult result)
    {
        IPEndPoint remoteEP = new IPEndPoint(IPAddress.Any, 6000);
        byte[] data = udpClient.EndReceive(result, ref remoteEP);
        string json = Encoding.UTF8.GetString(data);
        
        JObject pose = JObject.Parse(json);
        JArray pos = (JArray)pose["pos"];
        JArray rot = (JArray)pose["rot"];
        
        // Update Unity object transform
        trackedObject.transform.position = new Vector3(
            (float)pos[0], (float)pos[1], (float)pos[2]
        );
        trackedObject.transform.rotation = new Quaternion(
            (float)rot[1], (float)rot[2], (float)rot[3], (float)rot[0]
        );
        
        // Continue receiving
        udpClient.BeginReceive(OnReceive, null);
    }
}
```

### JavaScript/Three.js (WebGL)

```javascript
// Requires a WebSocket-to-UDP bridge on server
// Or use WebRTC data channels for browser-to-Python communication

const ws = new WebSocket('ws://localhost:8080');
const trackedObject = new THREE.Object3D();

ws.onmessage = function(event) {
    const pose = JSON.parse(event.data);
    
    // Update Three.js object
    trackedObject.position.set(
        pose.pos[0], pose.pos[1], pose.pos[2]
    );
    trackedObject.quaternion.set(
        pose.rot[1], pose.rot[2], pose.rot[3], pose.rot[0]
    );
};
```

### Python Receiver (OpenGL/Visualization)

```python
import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 6000))

while True:
    data, _ = sock.recvfrom(4096)
    pose = json.loads(data.decode('utf-8'))
    
    position = pose['pos']
    quaternion = pose['rot']
    
    # Update your 3D visualization
    update_camera_transform(position, quaternion)
```

## Comparison with ARBridge

| Feature | PoseStreamer | ARBridge |
|---------|-------------|----------|
| **Default Port** | 6000 | 9999 |
| **Data Format** | Simple: pos + rot | Full state: pos, vel, rot, biases |
| **Message Size** | ~50 bytes | ~400 bytes |
| **API Complexity** | Minimal | Comprehensive |
| **Use Case** | Simple 3D rendering | Full VIO state streaming |
| **Overhead** | Minimal | Moderate |

**When to use PoseStreamer:**
- You only need camera position and orientation
- You want minimal overhead
- You're integrating with simple 3D renderers
- You prefer a straightforward API

**When to use ARBridge:**
- You need full VIO state (velocity, biases)
- You want detailed metadata (timestamps, frame counts)
- You need additional data fields
- You're building advanced AR applications

## Troubleshooting

### No data received

**Check 1: Firewall**
```bash
# Allow UDP port 6000
sudo ufw allow 6000/udp
```

**Check 2: Verify sender is running**
```bash
# Check if port is being used
netstat -an | grep 6000
```

**Check 3: Test with sample receiver**
```bash
python -c "from vio import PoseStreamer; PoseStreamer.create_sample_receiver(port=6000, duration=10)"
```

### High latency

- UDP should have minimal latency (~1ms)
- Check network congestion
- Consider using localhost (127.0.0.1) for local testing
- Verify receiver is processing messages quickly

### Dropped frames

- UDP does not guarantee delivery (by design)
- This is normal for real-time streaming
- Receiver should handle missing frames gracefully
- Consider using ARBridge if reliability is critical

## Examples

### Example 1: Minimal Usage

```python
from vio import PoseStreamer
import numpy as np
import time

with PoseStreamer() as streamer:
    for i in range(100):
        position = np.array([i * 0.01, 0.0, 0.5])
        quaternion = np.array([1.0, 0.0, 0.0, 0.0])
        streamer.stream_pose(position, quaternion)
        time.sleep(0.033)  # 30 Hz
```

### Example 2: Full VIO Integration

See `example_pose_streamer.py` for a complete working example with simulated VIO system.

### Example 3: Running Tests

```bash
cd python-dev
python test_pose_streamer.py
```

## Best Practices

1. **Use context manager** for automatic cleanup:
   ```python
   with PoseStreamer() as streamer:
       # Your code here
   ```

2. **Check return value** for error handling:
   ```python
   success = streamer.stream_pose(pos, quat)
   if not success:
       print("Failed to send pose")
   ```

3. **Normalize quaternions** before streaming:
   ```python
   quaternion = quaternion / np.linalg.norm(quaternion)
   streamer.stream_pose(position, quaternion)
   ```

4. **Use localhost for local testing**:
   ```python
   streamer = PoseStreamer(host='127.0.0.1')
   ```

5. **Stream at consistent frame rate**:
   ```python
   import time
   target_fps = 30
   frame_time = 1.0 / target_fps
   
   while running:
       start = time.time()
       # ... process and stream ...
       elapsed = time.time() - start
       time.sleep(max(0, frame_time - elapsed))
   ```

## Advanced Usage

### Multiple Clients

PoseStreamer broadcasts to a single address. To stream to multiple clients:

**Option 1: Multiple streamers**
```python
streamer1 = PoseStreamer(port=6000, host='127.0.0.1')
streamer2 = PoseStreamer(port=6001, host='192.168.1.100')

# Stream to both
streamer1.stream_pose(pos, quat)
streamer2.stream_pose(pos, quat)
```

**Option 2: Use ARBridge** which supports more advanced networking.

### Custom Port Configuration

```python
# Development: localhost only
dev_streamer = PoseStreamer(port=6000, host='127.0.0.1')

# Production: specific IP
prod_streamer = PoseStreamer(port=6000, host='10.0.0.5')
```

## Summary

The PoseStreamer provides the simplest possible interface for streaming camera pose from your VIO system to 3D rendering applications:

```python
# 1. Create streamer
streamer = PoseStreamer(port=6000)

# 2. In your VIO loop, stream pose
streamer.stream_pose(position, quaternion)

# 3. Clean up
streamer.close()
```

That's it! Your 3D renderer can now receive real-time pose updates via UDP on port 6000.

---

**Related Documentation:**
- `AR_BRIDGE_GUIDE.md` - Full-featured VIO state streaming
- `example_pose_streamer.py` - Complete working examples
- `test_pose_streamer.py` - Test suite and validation
