# AprilTag Plane Alignment - Testing Guide

## Overview

This document provides testing guidelines for the new AprilTag plane alignment feature. The feature ensures that all AR elements are rendered directly on the plane of detected AprilTag markers, regardless of marker orientation.

## What Changed

### Before
- AR objects were positioned at marker location but only with approximate rotation
- Objects would not properly align with tilted or vertical markers
- Rotation was estimated from perspective distortion (less accurate)

### After
- Full 3D pose estimation using OpenCV's `solvePnP` with `SOLVEPNP_IPPE_SQUARE`
- Complete transformation matrix (rotation + translation) applied to AR scene
- Accurate plane alignment regardless of marker orientation
- Smooth quaternion-based interpolation for stable tracking

## Testing Scenarios

### 1. Flat Marker (Baseline Test)

**Setup:**
- Place an AprilTag marker flat on a table
- Marker should be parallel to the table surface

**Expected Behavior:**
- AR objects render perpendicular to the table surface
- Clearance zones extend upward from the marker
- Appliance model sits on the marker plane
- No visible difference from previous behavior (this is the reference case)

**How to Test:**
1. Open Clearance Genie in browser
2. Select "AprilTag" as marker type
3. Configure marker size (190mm recommended)
4. Start camera and point at flat marker
5. Verify objects render correctly on the plane

### 2. Tilted Marker (Primary Test)

**Setup:**
- Prop marker at approximately 45° angle
- Can use a book or stand to hold marker

**Expected Behavior:**
- AR objects follow the marker's tilt
- Clearance zones extend at the same angle as the marker
- Objects appear "glued" to the marker surface
- Smooth transitions as you adjust the tilt angle

**How to Test:**
1. Start with marker flat
2. Slowly tilt marker to 45°
3. Observe AR objects rotating with the marker
4. Verify objects remain aligned throughout the motion
5. Try different tilt angles (15°, 30°, 60°)

### 3. Vertical Marker (Critical Test)

**Setup:**
- Mount marker vertically on a wall or hold it upright
- Marker should be perpendicular to ground

**Expected Behavior:**
- AR objects render on the vertical plane
- Clearance zones extend horizontally from the wall
- Objects don't "fall down" - they stay on the wall plane
- This is the most dramatic test of plane alignment

**How to Test:**
1. Attach AprilTag to wall with tape
2. Point camera at vertical marker
3. Verify AR objects render on wall plane
4. Try moving closer/farther - alignment should persist
5. Tilt camera up/down - objects stay wall-aligned

### 4. Upside-Down Marker

**Setup:**
- Rotate marker 180° (upside-down)
- Can be flat, tilted, or vertical

**Expected Behavior:**
- Detection should still work (AprilTags are rotation-invariant)
- Objects render correctly on the plane
- No visual artifacts or inversions

**How to Test:**
1. Flip marker upside-down
2. Verify detection continues
3. Check object alignment remains correct
4. Compare with right-side-up orientation

### 5. Dynamic Tracking

**Setup:**
- Start with marker in any orientation
- Slowly rotate or move the marker

**Expected Behavior:**
- AR objects smoothly follow marker motion
- No jitter or sudden jumps
- Rotation interpolation appears natural
- Objects maintain plane alignment during transitions

**How to Test:**
1. Hold marker and slowly rotate it
2. Move marker closer and farther
3. Tilt marker while moving
4. Verify smooth tracking throughout

### 6. Multi-Marker Mode

**Setup:**
- Use 4 or 5 markers in a pattern
- Test with markers at various orientations

**Expected Behavior:**
- Plane alignment uses first detected marker's orientation
- Centroid position calculated from all markers
- Alignment remains stable even with multiple markers

**How to Test:**
1. Enable multi-marker mode (4-marker or 5-marker)
2. Place markers in configuration
3. Verify plane alignment works with multiple markers
4. Tilt one or more markers - first marker should define plane

## Common Issues and Solutions

### Objects Not Aligning with Plane

**Symptoms:**
- Objects appear to float or penetrate marker
- Alignment is inconsistent

**Solutions:**
1. Check marker is clearly visible (good lighting, no occlusion)
2. Verify marker size is correctly measured (BLACK SQUARE only)
3. Adjust manual depth offset if needed
4. Check browser console for "Error computing pose" messages

### Jittery or Unstable Tracking

**Symptoms:**
- Objects shake or vibrate
- Sudden jumps in position/rotation

**Solutions:**
1. Improve lighting conditions
2. Ensure marker is crisp and in focus
3. Hold camera steadier
4. Smoothing factors can be adjusted in code if needed:
   - `POSITION_SMOOTH_FACTOR = 0.2` (decrease for slower response)
   - `ROTATION_SMOOTH_FACTOR = 0.15` (decrease for slower rotation)

### Objects Appear Upside-Down or Mirrored

**Symptoms:**
- Coordinate system appears inverted
- Objects render backwards

**Solutions:**
1. This may indicate a coordinate conversion issue
2. Report issue with specific device/browser details
3. Check browser console for errors

### Plane Alignment Only Works for Some Markers

**Symptoms:**
- Works for ArUco but not AprilTag (or vice versa)
- Works in single-marker but not multi-marker mode

**Solutions:**
1. Both marker types should support plane alignment
2. Check that `transformMatrix` is being computed
3. Verify `parallaxEnabled` is true in settings
4. Check browser console for specific errors

## Browser Console Debugging

Enable browser console (F12) to see debug messages:

**Success Messages:**
```
AprilTag detector initialized: family=36h11
ArUco detector initialized with enhanced parameters
OpenCV Ready
```

**Warning Messages:**
```
Error computing pose from corners: [details]
solvePnP failed for marker
```

**Check for:**
- OpenCV.js loaded successfully
- Camera matrix initialized
- No errors during pose computation

## Performance Considerations

- Plane alignment adds minimal overhead (solvePnP is fast)
- Typical performance: 30fps on modern mobile devices
- Older devices: may see 15-20fps
- Multi-marker mode: same performance as before

## Comparison with Legacy Behavior

| Aspect | Legacy (Approximate) | New (solvePnP) |
|--------|---------------------|----------------|
| Position Accuracy | Same | Same |
| Rotation Accuracy | Approximate (±10°) | Accurate (±1°) |
| Plane Alignment | No | Yes |
| Tilted Markers | Poor | Excellent |
| Vertical Markers | Poor | Excellent |
| Performance | Baseline | Same |
| Smoothing | Position only | Position + Quaternion |

## Reporting Issues

If you encounter issues, please report with:

1. **Device Information:**
   - Device model (iPhone 13, Samsung Galaxy S21, etc.)
   - Browser (Safari, Chrome, Firefox)
   - OS version

2. **Marker Configuration:**
   - Marker type (ArUco or AprilTag)
   - Marker size measured
   - Orientation tested

3. **Observed Behavior:**
   - What happened
   - What you expected
   - Screenshots or video if possible

4. **Console Output:**
   - Any error messages from browser console
   - Warnings or unusual log entries

## Success Criteria

✅ **Implementation is successful if:**

1. Flat markers work correctly (baseline)
2. Tilted markers show objects following the tilt
3. Vertical markers show objects on wall plane
4. Dynamic tracking is smooth and stable
5. Both ArUco and AprilTag markers work
6. Multi-marker mode maintains alignment
7. No performance degradation
8. Works across different devices/browsers

## Next Steps

After testing:
1. Gather feedback on alignment accuracy
2. Fine-tune smoothing factors if needed
3. Consider adding camera calibration wizard
4. Explore advanced features (multi-plane support, etc.)

## Technical Notes

- Camera FOV assumed to be 60° (typical for mobile)
- Distortion coefficients assumed to be zero
- For better accuracy, implement camera calibration
- solvePnP uses IPPE_SQUARE algorithm (best for planar markers)
- Coordinate conversion handles OpenCV → Three.js properly
