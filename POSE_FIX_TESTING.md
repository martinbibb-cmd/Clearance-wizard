# AR Marker Pose Alignment Fix - Testing Guide

## Overview

This document describes the fix applied to resolve the issue where 3D AR objects don't sit properly on the marker plane. The objects appeared "standing up" or at incorrect orientations instead of lying flat on the marker surface.

## Problem Description

### Symptoms
- 2D marker detection works correctly (marker outline is drawn accurately)
- 3D AR overlays don't align with the marker plane
- Objects appear to be standing upright when marker is flat
- Objects don't follow the marker orientation when tilted

### Root Cause
The coordinate system conversion between OpenCV (used for marker detection) and Three.js/WebGL (used for 3D rendering) was not being applied correctly.

**OpenCV coordinate system:**
- X: right
- Y: down
- Z: forward (into the scene)

**Three.js/WebGL coordinate system:**
- X: right
- Y: up
- Z: backward (toward the camera)

## Solution Implemented

### 1. Fixed Coordinate Transformation (`applyTransformationMatrix`)

The key fix is to properly apply the axis flip matrix to convert from OpenCV to WebGL coordinates:

```javascript
// Build 4x4 pose matrix from OpenCV
const poseCV = new THREE.Matrix4();
poseCV.set(
    R[0], R[1], R[2], T[0],
    R[3], R[4], R[5], T[1],
    R[6], R[7], R[8], T[2],
    0,    0,    0,    1
);

// Apply axis flip matrix F = diag(1, -1, -1, 1)
const axisFlip = new THREE.Matrix4();
axisFlip.set(
    1,  0,  0, 0,
    0, -1,  0, 0,
    0,  0, -1, 0,
    0,  0,  0, 1
);

// Convert: pose_webgl = F * pose_opencv
const poseWebGL = new THREE.Matrix4();
poseWebGL.multiplyMatrices(axisFlip, poseCV);
```

This properly flips the Y and Z axes to convert between the two coordinate systems.

### 2. Added Debug Test Objects Visualization

To help verify the fix works correctly, a new debug mode was added:

**Features:**
- Flat green plane (200mm) - should lie flat on the marker surface
- Yellow sphere at marker center (origin point)
- Magenta cube (100mm) - positioned above the plane
- Colored axis lines with tick marks:
  - Red = X axis (right)
  - Green = Y axis (up)
  - Blue = Z axis (forward)

**How to enable:**
1. Open Advanced Settings in the main menu
2. Check "🎯 Debug Plane (test alignment)"
3. Start the camera session

## Testing Instructions

### Test 1: Flat Marker (Baseline)

**Setup:**
1. Print an AprilTag or ArUco marker
2. Place it flat on a table
3. Enable "Debug Plane" in Advanced Settings
4. Start camera and point at marker

**Expected Result:**
- Green plane should lie flat on the marker
- Sphere should be at the center
- Cube should sit on the plane (not penetrate or float)
- Axis lines should extend correctly:
  - Red (X) pointing right
  - Green (Y) pointing up
  - Blue (Z) pointing forward (away from marker surface)

**If this fails:**
- Objects appear rotated/tilted when marker is flat
- Indicates the coordinate transformation still has issues

### Test 2: Tilted Marker (Primary Test)

**Setup:**
1. Prop marker at a 45° angle (use a book or stand)
2. Keep debug plane enabled
3. Point camera at tilted marker

**Expected Result:**
- Green plane should follow the marker tilt
- Plane should remain "glued" to the marker surface
- Cube and sphere should tilt with the plane
- Axis lines should maintain their orientation relative to the marker

**If this fails:**
- Plane doesn't follow marker tilt
- Objects appear to rotate incorrectly
- Indicates rotation transformation issues

### Test 3: Vertical Marker (Critical Test)

**Setup:**
1. Attach marker to a wall (tape or hold vertically)
2. Keep debug plane enabled
3. Point camera at vertical marker

**Expected Result:**
- Green plane should be vertical (perpendicular to ground)
- Objects should "stick" to the wall
- No "falling down" effect
- Axis lines maintain correct orientation

**If this fails:**
- Most dramatic test of alignment
- Objects don't stay vertical with marker
- Strong indication of transformation issues

### Test 4: Dynamic Movement

**Setup:**
1. Start with marker flat
2. Slowly rotate to vertical
3. Observe transitions

**Expected Result:**
- Smooth interpolation as marker rotates
- No jitter or sudden jumps
- Objects maintain alignment throughout

## Debugging

### Console Logs

Check browser console (F12) for debug messages:

```
🎯 Debug test objects enabled - showing plane, sphere, cube with axis lines
```

### Device Info Overlay

When Testing Mode is enabled, you'll see real-time position information in the top-right corner.

### Common Issues

**Issue: Plane appears rotated 90°**
- Indicates the axis flip might need adjustment
- Try adding additional rotation: `anchor.rotation.x += Math.PI/2`

**Issue: Objects jitter or shake**
- May be lighting or focus issues
- Check smoothing factors (POSITION_SMOOTH_FACTOR, ROTATION_SMOOTH_FACTOR)

**Issue: Plane penetrates marker or floats**
- Check depth offset settings
- Verify marker size is measured correctly (black square only)

## Code Changes Summary

### Modified Functions

1. **`applyTransformationMatrix(transformMatrix, depthOffset)`** (GraphicsEngine)
   - Complete rewrite of coordinate transformation logic
   - Proper matrix multiplication for axis conversion
   - Cleaner decompose() for position/rotation extraction

2. **`showDebugTestObjects()`** (GraphicsEngine)
   - New method to render test visualization objects
   - Creates plane, sphere, cube, and axis lines
   - All objects are children of this.debugTestObjects group

3. **`hideDebugTestObjects()`** (GraphicsEngine)
   - Cleanup method for debug objects

4. **`toggleDebugTestObjects(event)`** (App)
   - UI toggle handler
   - Persists state to localStorage

5. **`initDebugTestObjects()`** (App)
   - Initialization from localStorage on app load

### UI Changes

Added to Advanced Settings panel:
```html
<label>
    <input type="checkbox" id="debug-test-objects-checkbox" 
           onchange="App.toggleDebugTestObjects(event)">
    <span>🎯 Debug Plane (test alignment)</span>
</label>
```

## Verification Checklist

Before considering the fix complete, verify:

- [ ] Flat marker: plane lies flat, cube sits on top
- [ ] Tilted marker: objects follow tilt correctly
- [ ] Vertical marker: objects stick to vertical surface
- [ ] Smooth tracking during movement
- [ ] No jitter or instability
- [ ] Works with both AprilTag and ArUco markers
- [ ] Multi-marker mode maintains alignment
- [ ] No performance degradation

## Technical Notes

### Coordinate System Details

**OpenCV (solvePnP output):**
```
    Z (forward)
   /
  /
 /_____X (right)
 |
 |
 Y (down)
```

**Three.js/WebGL:**
```
 Y (up)
 |
 |
 |_____X (right)
  \
   \
    Z (backward/toward camera)
```

### Transformation Mathematics

The axis flip matrix F = diag(1, -1, -1, 1) can be understood as:
- X component: unchanged (1)
- Y component: flipped (-1)
- Z component: flipped (-1)
- W component: unchanged (1) for homogeneous coords

When applied to a pose matrix:
```
F * Pose_CV = Pose_WebGL
```

This converts the marker pose from OpenCV's coordinate system to Three.js's coordinate system, ensuring objects align correctly with the marker surface.

### Object Points Definition (Unchanged)

The marker object points remain correctly defined:
```javascript
const objectPoints = [
    [-halfSize, -halfSize, 0],  // Bottom-left
    [ halfSize, -halfSize, 0],  // Bottom-right
    [ halfSize,  halfSize, 0],  // Top-right
    [-halfSize,  halfSize, 0]   // Top-left
];
```

All points have Z=0, confirming they are coplanar and lie in the marker's XY plane.

## References

- Problem statement: GitHub issue describing "standing up" objects
- OpenCV solvePnP documentation: https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html
- Three.js Matrix4 documentation: https://threejs.org/docs/#api/en/math/Matrix4
- Related documentation: PLANE_ALIGNMENT_TESTING.md (previous alignment work)

## Success Criteria

✅ The fix is successful if:
1. Debug plane lies flat on flat markers
2. Debug plane follows marker orientation correctly
3. Real appliance/clearance visualizations align properly
4. No performance impact
5. Works across different device types
6. Compatible with existing features (multi-marker, testing mode)
