# Marker Coordinate System Fix

## Issue Summary

Objects were appearing with incorrect orientation on markers due to inverted Y-axis in the marker coordinate system definition. This affected both ArUco and AprilTag markers.

## Root Cause

The backend (Python) code had the object points defined with an **inverted Y-axis**:

**INCORRECT (Before):**
```python
object_points = np.array([
    [-marker_size/2, marker_size/2, 0],   # Labeled "Top-left" but Y positive = BOTTOM
    [marker_size/2, marker_size/2, 0],    # Labeled "Top-right" but Y positive = BOTTOM
    [marker_size/2, -marker_size/2, 0],   # Labeled "Bottom-right" but Y negative = TOP
    [-marker_size/2, -marker_size/2, 0]   # Labeled "Bottom-left" but Y negative = TOP
], dtype=np.float32)
```

This resulted in an actual corner order of **[BL, BR, TR, TL]** instead of the expected **[TL, TR, BR, BL]**, causing a 180-degree coordinate system rotation.

## Solution

Fixed the object points to match OpenCV's coordinate system convention:

**CORRECT (After):**
```python
object_points = np.array([
    [-marker_size/2, -marker_size/2, 0],  # Top-left: X negative (left), Y negative (top)
    [marker_size/2, -marker_size/2, 0],   # Top-right: X positive (right), Y negative (top)
    [marker_size/2, marker_size/2, 0],    # Bottom-right: X positive (right), Y positive (bottom)
    [-marker_size/2, marker_size/2, 0]    # Bottom-left: X negative (left), Y positive (bottom)
], dtype=np.float32)
```

## OpenCV Coordinate System

### Marker Coordinate System (3D Object Points)
- **X-axis**: Points to the right (positive X = right side of marker)
- **Y-axis**: Points down (positive Y = bottom of marker, **NOT up**)
- **Z-axis**: Points forward into the scene (away from marker surface)

### Image Coordinate System (2D Image Points)
- **Origin**: Top-left corner of image
- **X-axis**: Points right (increasing column number)
- **Y-axis**: Points down (increasing row number)

### Corner Order Convention
OpenCV's `detectMarkers()` (ArUco) and the apriltag library return corners in this order:
1. **Top-Left**: (-X, -Y, 0)
2. **Top-Right**: (+X, -Y, 0)
3. **Bottom-Right**: (+X, +Y, 0)
4. **Bottom-Left**: (-X, +Y, 0)

This is a clockwise ordering when viewing the marker from the front.

## Files Changed

### Backend (Python)
1. **python-dev/ar_engine_api.py** (lines 424-432)
   - Fixed object_points array for ArUco detection
   - Added detailed comments

2. **python-dev/vio/apriltag_detector.py** (lines 80-90)
   - Fixed object_points array for AprilTag detection
   - Added detailed comments

### Frontend (JavaScript)
3. **index.html** (lines 930-950)
   - Updated comments to clarify coordinate system
   - Comments were previously misleading but code was actually correct

## Impact

This fix ensures that:
- ✅ Objects appear aligned with the marker plane
- ✅ Objects have correct orientation (not flipped 180°)
- ✅ Works correctly for flat, tilted, and vertical markers
- ✅ Consistent behavior between ArUco and AprilTag markers
- ✅ Coordinate transformation to Three.js/WebGL works correctly

## Testing

All existing tests pass with the corrected coordinate system:
- `test_apriltag_detector.py`: All 5 tests pass ✓
- Object points form a proper square centered at origin ✓
- Coordinate system follows OpenCV convention ✓

## Related Documentation

- OpenCV solvePnP: https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#ga549c2075fac14829ff4a58bc931c033d
- OpenCV ArUco: https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html
- See also: `POSE_ALIGNMENT_FIX_SUMMARY.md` for the Three.js coordinate conversion
- See also: `PLANE_ALIGNMENT_TESTING.md` for testing procedures

## Key Takeaway

**Always remember:** In OpenCV's coordinate system for markers:
- **Negative Y = Top** (not bottom!)
- **Positive Y = Bottom** (not top!)
- This is different from many graphics systems where Y-up is common
