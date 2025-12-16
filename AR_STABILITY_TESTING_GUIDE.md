# AR Object Stability Testing Guide

## Overview
This guide describes how to manually test the AR object alignment and stability fixes. The fixes address three main issues:
1. **Scale Issue**: AR objects appearing oversized
2. **Erratic Movement**: Objects moving rapidly or jumping unexpectedly
3. **Poor Tracking**: Unstable positioning when marker is steady

## What Was Fixed

### 1. Scale Reset (Critical Fix)
**Problem**: Transformation matrix decomposition can extract non-uniform scale values that were incorrectly applied to AR objects, making them appear oversized.

**Fix**: After decomposing the transformation matrix, scale is explicitly reset to `(1, 1, 1)` to ensure AR objects maintain correct size.

**Expected Behavior**:
- AR objects (radiators, pipes, clearance zones) should appear at the correct size relative to the marker
- Object size should remain constant as you move the camera
- No sudden size changes or "ballooning" effects

### 2. Outlier Detection
**Problem**: Detection noise or errors could cause sudden large jumps in position, making AR objects appear to "teleport" or move erratically.

**Fix**: Added validation to reject:
- NaN or Infinity values in position/rotation
- Position jumps larger than 1000mm (1 meter) per frame

**Expected Behavior**:
- Smooth, continuous tracking even with camera shake
- No sudden "jumps" or "teleporting" of AR objects
- Objects maintain position when marker is steady

### 3. Improved Smoothing
**Problem**: Original smoothing factors (0.2 for position, 0.15 for rotation) were too conservative, making tracking feel sluggish.

**Fix**: Increased to 0.3 for position and 0.25 for rotation, providing better responsiveness while still filtering jitter.

**Expected Behavior**:
- AR objects respond more quickly to marker movement
- Tracking feels more "immediate" and less laggy
- Still smooth, no jitter or shaking

### 4. Tracking State Management
**Problem**: When a marker was lost and reacquired, the outlier detection could incorrectly reject the first valid position.

**Fix**: Added tracking reset mechanism that clears position history when marker is lost.

**Expected Behavior**:
- Smooth reacquisition when marker comes back into view
- No delay or stuttering on reacquisition
- Immediate tracking restoration

## Test Scenarios

### Test 1: Scale Verification (Most Critical)
**Setup**:
1. Print an AprilTag marker (recommended: 190mm)
2. Measure the marker size accurately with a ruler (measure BLACK SQUARE only)
3. Place marker on a flat surface
4. Start AR session with correct marker size entered

**Test Steps**:
1. Point camera at marker from ~50cm distance
2. Enable "🎯 Debug Plane" in settings
3. Observe the green debug plane and magenta cube

**Pass Criteria**:
- ✅ Debug plane appears to be the same size as the physical marker
- ✅ Magenta cube sits on plane at reasonable scale (100mm cube on 190mm marker)
- ✅ Appliance models appear proportionally correct
- ✅ Clearance zones extend to reasonable distances (not meters away)

**Fail Indicators**:
- ❌ Debug plane appears much larger than physical marker
- ❌ Cube is enormous (fills entire screen)
- ❌ Appliance appears giant-sized
- ❌ Clearance zones extend unrealistically far

### Test 2: Position Stability
**Setup**:
1. Place marker on stable surface (table, floor)
2. Position camera on tripod or stable support at ~50cm
3. Start AR session

**Test Steps**:
1. Keep both marker and camera completely still for 10 seconds
2. Observe AR object movement
3. Enable Testing Mode to see position values

**Pass Criteria**:
- ✅ AR objects remain nearly stationary (< 5mm drift)
- ✅ No sudden jumps or teleporting
- ✅ Position values in Testing Mode show minimal variation
- ✅ Smooth, gentle drift only (if any)

**Fail Indicators**:
- ❌ Objects "vibrate" or shake visibly
- ❌ Sudden jumps of 10cm or more
- ❌ Continuous drifting in one direction
- ❌ Position values jumping erratically

### Test 3: Movement Responsiveness
**Setup**:
1. Hold marker in hand
2. Start AR session
3. Enable Testing Mode

**Test Steps**:
1. Move marker slowly left/right (5cm)
2. Move marker slowly up/down (5cm)
3. Move marker slowly toward/away from camera (10cm)
4. Observe AR object tracking

**Pass Criteria**:
- ✅ AR objects follow marker smoothly
- ✅ No visible lag > 0.3 seconds
- ✅ Movement feels "connected" to marker
- ✅ No overshooting or oscillation

**Fail Indicators**:
- ❌ Significant lag (> 0.5 seconds)
- ❌ Objects "catch up" with visible delay
- ❌ Overshooting (objects move past marker position)
- ❌ Oscillation or "hunting" behavior

### Test 4: Marker Reacquisition
**Setup**:
1. Place marker on table
2. Start AR session
3. Ensure tracking is active

**Test Steps**:
1. Cover marker with hand for 2 seconds
2. Remove hand quickly
3. Observe how quickly tracking resumes
4. Repeat 5 times

**Pass Criteria**:
- ✅ Tracking resumes within 1 second
- ✅ No visible "jump" on reacquisition
- ✅ Smooth transition from "Looking..." to "Tracking"
- ✅ Consistent behavior across multiple reacquisitions

**Fail Indicators**:
- ❌ Delay > 2 seconds to resume tracking
- ❌ Large position jump on reacquisition
- ❌ Incorrect position after reacquisition
- ❌ Tracking fails to resume

### Test 5: Different Marker Sizes
**Setup**: Test with three different marker sizes

**Test Steps**:
1. Test with 40mm marker at 20-30cm distance
2. Test with 90mm marker at 50-70cm distance
3. Test with 190mm marker at 100-150cm distance

**Pass Criteria**:
- ✅ All sizes track correctly when entered accurately
- ✅ Scale appears correct relative to marker size
- ✅ No size-specific issues (all sizes work equally well)

**Fail Indicators**:
- ❌ Some sizes work better than others
- ❌ Scale issues specific to certain sizes
- ❌ Tracking quality varies with marker size

### Test 6: Lighting Conditions
**Setup**: Test in different lighting

**Test Steps**:
1. Good lighting (bright indoor, no shadows)
2. Low light (dim room, evening)
3. Mixed lighting (partially shadowed marker)
4. Bright backlight (window behind marker)

**Pass Criteria**:
- ✅ Stable tracking in good lighting
- ✅ Reasonable tracking in low light (may be slower)
- ✅ Graceful degradation in difficult conditions
- ✅ No sudden failures or crashes

**Fail Indicators**:
- ❌ Tracking fails in any reasonable lighting
- ❌ Different behavior in different lighting (should be consistent)
- ❌ Crashes or freezes

### Test 7: Camera Movement
**Setup**:
1. Place marker on table
2. Hold phone/camera in hand

**Test Steps**:
1. Slowly orbit around marker (circular path)
2. Move closer/farther (50cm to 150cm range)
3. Tilt camera angle (5° to 45° from perpendicular)
4. Shake camera slightly (simulate hand tremor)

**Pass Criteria**:
- ✅ Smooth tracking during slow movement
- ✅ Objects stay "glued" to marker during orbiting
- ✅ Stable tracking at various distances
- ✅ Minor camera shake filtered out
- ✅ Smooth tracking at various angles

**Fail Indicators**:
- ❌ Objects "slide" on marker during movement
- ❌ Tracking breaks at certain angles
- ❌ Excessive sensitivity to camera shake
- ❌ Position "jumps" during smooth camera motion

## Automated Tests

### Browser Test Suite
Open `test_ar_alignment.html` in a web browser to run automated unit tests:

```bash
# From repository root
open test_ar_alignment.html  # macOS
xdg-open test_ar_alignment.html  # Linux
start test_ar_alignment.html  # Windows
```

**Expected Results**: All 7 tests should pass (100% success rate)

### Python Test Suite
Run the Python stability tests:

```bash
cd python-dev
pip install numpy opencv-python
python3 test_ar_stability.py
```

**Expected Results**: All 5 tests should pass

## Performance Benchmarks

### Frame Rate
- **Desktop/Laptop**: Should maintain 60 FPS
- **Modern Mobile**: Should maintain 30-60 FPS
- **Older Mobile**: Should maintain 20-30 FPS

### Detection Latency
- **First Detection**: < 500ms
- **Tracking Update**: < 33ms (30 FPS)
- **Reacquisition**: < 1000ms

### Position Accuracy
- **Static Marker Drift**: < 5mm over 10 seconds
- **Position Jump Threshold**: Rejects > 1000mm jumps
- **Smoothing Convergence**: Reaches 95% in ~8 frames (0.27s at 30fps)

## Known Limitations

### Expected Behavior
1. **Initial Acquisition**: May take 0.5-1 second for first detection
2. **Extreme Angles**: Tracking may degrade beyond 60° tilt
3. **Very Close/Far**: Optimal range is 0.3-2.0 meters
4. **Low Light**: Detection may slow down but should not fail completely
5. **Motion Blur**: Fast marker movement may cause temporary tracking loss

### Not Bugs
1. **Slight drift**: 1-2mm drift over time is normal in monocular AR
2. **Perspective changes**: Apparent "size change" when moving camera is correct perspective
3. **Brief tracking loss**: Losing tracking for <1 second during occlusion is expected

## Reporting Issues

If you encounter problems, please report with:

1. **Device Info**: Phone/tablet model, browser version
2. **Marker Info**: Type (AprilTag/ArUco), size in mm, family
3. **Test Scenario**: Which test from this guide failed
4. **Observed Behavior**: Specific symptoms (with screenshots/video)
5. **Expected Behavior**: What should have happened
6. **Frequency**: Always, sometimes, rarely
7. **Console Logs**: Browser console output (F12 → Console tab)

### How to Capture Console Logs
1. Open browser developer tools (F12)
2. Go to Console tab
3. Reproduce the issue
4. Look for warning/error messages mentioning:
   - "Position jump too large"
   - "Invalid pose values detected"
   - Any other errors or warnings
5. Copy the console output

## Success Criteria

The fix is successful if:

- ✅ All automated tests pass
- ✅ AR objects appear at correct scale (Test 1)
- ✅ Tracking is stable with <5mm drift (Test 2)
- ✅ Movement tracking is responsive (Test 3)
- ✅ Reacquisition is smooth (Test 4)
- ✅ Works with multiple marker sizes (Test 5)
- ✅ Degrades gracefully in poor lighting (Test 6)
- ✅ Handles camera movement smoothly (Test 7)
- ✅ Frame rate meets benchmarks
- ✅ No regressions in existing features

## Regression Testing

To ensure the fixes don't break existing functionality:

1. **Multi-marker Mode**: Verify 4-marker and 5-marker modes still work
2. **Parallax Toggle**: Verify disabling parallax still works
3. **Manual Depth Offset**: Verify depth offset control works
4. **Lens Correction**: Verify lens correction toggle works
5. **Testing Mode**: Verify calibration axes and position display work
6. **Screenshot Capture**: Verify screenshot button works
7. **All Appliance Types**: Test radiator, flue, and custom models

## Timeline for Testing

- **Automated Tests**: 5 minutes
- **Quick Manual Test**: 10 minutes (Tests 1-4)
- **Comprehensive Manual Test**: 30 minutes (all tests)
- **Full Regression Test**: 45 minutes (including all features)

## Contact

For questions about this testing guide:
- Check browser console for technical details
- Review EXPECTED_BEHAVIOR.md for visual guide
- Consult COORDINATE_SYSTEM_FIX.md for coordinate system info
