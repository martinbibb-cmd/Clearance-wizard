# AprilTag Pose Estimation Stability Guide

This guide explains the pose estimation stability improvements implemented in the `AprilTagDetector` class to address common tracking issues.

## The Problem: Pose Estimation Collapse

When AprilTags are detected at close range, several issues can cause the pose estimate to become unstable:

1. **Near-field instability**: Markers too close to the camera create excessive perspective distortion
2. **Corner order ambiguity**: At close range, corner detection can flip, causing 180° pose jumps
3. **Excessive rejection**: Single-frame pose errors cause markers to be dropped immediately
4. **Motion artifacts**: Camera movement, blur, or auto-exposure changes destabilize tracking

### Symptoms
- Marker detected briefly, then "dies"
- Pose jumps wildly between frames
- Tracking loss at close distances
- Better stability with ArUco than AprilTag (AprilTag is more sensitive)

## The Solution: Multi-Layered Stability Improvements

### 1. Minimum Distance Enforcement

**Problem**: Markers too close create unstable pose estimates.

**Solution**: Enforce minimum distance based on marker size.

```python
detector = AprilTagDetector(
    tag_size=0.04,  # 40mm marker
    camera_matrix=K,
    dist_coeffs=D,
    min_distance=0.08  # 80mm minimum (2 × tag_size recommended)
)
```

**Rule of thumb**: `min_distance ≥ 2 × tag_size`

For 40mm marker: minimum 80mm distance
For 190mm marker: minimum 380mm distance

### 2. Pose Continuity with solvePnPGeneric

**Problem**: Corner order flips cause 180° pose jumps.

**Solution**: Use `solvePnPGeneric` to get all possible solutions, then select the one closest to the previous frame.

```python
# Automatically handled in detect() method
detections = detector.detect(frame)
# Each detection includes 'tracking_status': 'detected', 'tracking', or 'lost'
```

The detector:
1. Gets all possible pose solutions from `solvePnPGeneric`
2. Compares each to the previous frame's pose
3. Selects solution with minimal position + rotation change
4. Rejects mirror solutions (negative Z depth)

### 3. Temporal Smoothing

**Problem**: Single-frame noise causes jitter.

**Solution**: Exponential smoothing of position and rotation.

```python
detector = AprilTagDetector(
    tag_size=0.19,
    camera_matrix=K,
    dist_coeffs=D,
    smoothing_alpha=0.3  # 0 = no smoothing, 1 = no filtering
)
```

**Smoothing formula**:
```
new_pose = alpha × measured_pose + (1 - alpha) × previous_pose
```

**Recommended values**:
- `0.1-0.2`: Heavy smoothing (less jitter, more lag)
- `0.3-0.5`: Balanced (default 0.3)
- `0.6-0.8`: Light smoothing (more responsive, some jitter)

### 4. Distance-Aware Reprojection Error Thresholds

**Problem**: Near-field markers naturally have higher reprojection error.

**Solution**: Scale error threshold based on distance.

```python
detector = AprilTagDetector(
    tag_size=0.19,
    camera_matrix=K,
    dist_coeffs=D,
    max_reprojection_error=5.0  # pixels at nominal distance
)
```

**Adaptive threshold**:
```
adjusted_threshold = max_error × max(1.0, min_distance / actual_distance)
```

This allows higher error for close markers while maintaining quality for distant ones.

### 5. Tracking State Machine

**Problem**: Single-frame detection failure drops marker immediately.

**Solution**: Track marker state with timeout before declaring lost.

```python
detector = AprilTagDetector(
    tag_size=0.19,
    camera_matrix=K,
    dist_coeffs=D,
    lost_timeout_frames=5  # Wait 5 frames before declaring lost
)
```

**State transitions**:
```
Untracked → detected (first detection)
detected → tracking (subsequent detections with temporal continuity)
tracking → lost (after timeout_frames without detection)
lost → detected (re-detection after loss)
```

## Recommended Marker Sizes and Distances

Based on the rule `marker_width ≥ 1/6 of image_width` and `distance ≥ 2 × marker_size`:

| Use Case | Marker Size | Min Distance | Max Distance | Image Width |
|----------|-------------|--------------|--------------|-------------|
| Close-up work | 40-50mm | 80-100mm | ~500mm | 640px+ |
| Standard installation | 80-100mm | 160-200mm | ~1500mm | 640px+ |
| Better stability | 150mm (A5) | 300mm | ~3000mm | 1280px+ |
| Distance measurements | 190mm (A4) | 380mm | ~5000mm | 1280px+ |

**Key recommendations from problem statement**:
- Print 80-100mm markers for testing (larger = more stable)
- Measure the BLACK SQUARE only (exclude white border)
- Use A4-sized markers (190mm) for best distance performance

## Usage Example

```python
import numpy as np
import cv2
from vio import AprilTagDetector

# 1. Setup with stability parameters
camera_matrix = AprilTagDetector.create_default_camera_matrix(1280, 720, fov_degrees=60)
dist_coeffs = np.zeros(5)

detector = AprilTagDetector(
    tag_size=0.19,  # 190mm marker
    camera_matrix=camera_matrix,
    dist_coeffs=dist_coeffs,
    min_distance=0.38,  # 380mm minimum (2 × tag_size)
    max_reprojection_error=5.0,  # pixels
    smoothing_alpha=0.3,  # 30% new, 70% previous
    lost_timeout_frames=5  # Wait 5 frames before declaring lost
)

# 2. Process video frames
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detect with stability features
    detections = detector.detect(frame)
    
    for det in detections:
        tag_id = det['tag_id']
        position = det['translation']
        status = det['tracking_status']
        error = det['reprojection_error']
        
        print(f"Tag {tag_id}: {status}")
        print(f"  Position: {position}")
        print(f"  Reproj error: {error:.2f}px")
        
        # Check distance
        distance = np.linalg.norm(position)
        if distance < detector.min_distance:
            print(f"  Warning: Too close! ({distance:.3f}m < {detector.min_distance:.3f}m)")
    
    # Visualize
    vis_frame = detector.visualize_detections(frame, detections)
    cv2.imshow('Stable AprilTag Detection', vis_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## Reset Tracking

If tracking becomes corrupted or you want to restart:

```python
# Reset tracking for specific tag
detector.reset_tracking(tag_id=42)

# Reset all tracking
detector.reset_tracking()
```

## Detection Dictionary Fields

Each detection now includes:

- `tag_id`: Unique marker identifier
- `translation`: 3D position [x, y, z] in meters
- `rotation_matrix`: 3x3 rotation matrix
- `rotation_vector`: 3D rotation in Rodrigues format
- `corners`: 4×2 pixel coordinates
- `center`: 2D center position
- `hamming`: Detection quality (lower = better)
- `decision_margin`: Detection confidence (higher = better)
- **`tracking_status`**: 'detected', 'tracking', or 'lost' (NEW)
- **`reprojection_error`**: RMS error in pixels (NEW)

## Troubleshooting

### Marker still "dies" at close range

1. **Increase minimum distance**:
   ```python
   min_distance=3.0 * tag_size  # More conservative
   ```

2. **Increase smoothing**:
   ```python
   smoothing_alpha=0.2  # Heavier filtering
   ```

3. **Increase timeout**:
   ```python
   lost_timeout_frames=10  # More lenient
   ```

4. **Use larger marker**: Print 190mm instead of 40mm

### Tracking lags behind motion

1. **Decrease smoothing**:
   ```python
   smoothing_alpha=0.5  # More responsive
   ```

2. **Check frame rate**: Low FPS amplifies lag

### False positives at distance

1. **Stricter reprojection error**:
   ```python
   max_reprojection_error=3.0  # More strict
   ```

2. **Check hamming distance**: Lower is better
   ```python
   if det['hamming'] > 2:
       continue  # Skip poor detections
   ```

## Performance Considerations

The stability improvements add minimal overhead:
- `solvePnPGeneric`: ~2× slower than `solvePnP` (still <1ms per tag)
- Pose selection: O(n) where n = number of solutions (typically 1-2)
- Smoothing: Negligible

For 30 FPS video with 1-3 tags, overhead is <5ms total.

## References

Problem statement recommendations:
1. ✅ Enforce minimum distance
2. ✅ Use solvePnPGeneric for multiple solutions
3. ✅ Choose pose with minimal delta from last frame
4. ✅ Smooth instead of reject
5. ✅ Detection → Tracking → Lost (timeout)

See also:
- [OpenCV solvePnP documentation](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#ga549c2075fac14829ff4a58bc931c033d)
- [AprilTag paper](https://april.eecs.umich.edu/media/apriltag/wang2016iros.pdf)
- Original problem statement in issue tracker
