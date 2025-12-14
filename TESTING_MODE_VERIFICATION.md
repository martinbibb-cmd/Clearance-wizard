# Testing Mode Verification Checklist

## Overview

This document provides a comprehensive QA checklist for verifying Testing Mode functionality across different devices and configurations.

## Pre-Test Setup

- [ ] Prepare test markers (AprilTag and ArUco) in multiple sizes:
  - [ ] 90mm markers
  - [ ] 148mm markers
  - [ ] 190mm markers
- [ ] Have measuring tools ready:
  - [ ] Ruler or measuring tape (metric)
  - [ ] Calipers for precise marker measurements
- [ ] Prepare test devices representing different categories:
  - [ ] iOS device (iPhone)
  - [ ] Android device (phone)
  - [ ] Tablet (iPad or Android)
  - [ ] Desktop with webcam (optional)
- [ ] Set up controlled lighting environment
- [ ] Prepare documentation template for recording results

## UI Controls Verification

### URL Parameter Test
- [ ] Navigate to `http://localhost:8000/?testMode=true`
- [ ] Verify Testing Mode is enabled on load
- [ ] Check that welcome panel checkbox is checked
- [ ] Navigate without parameter: `http://localhost:8000/`
- [ ] Verify Testing Mode is disabled (unless previously enabled)

### Welcome Panel Checkbox Test
- [ ] Open application welcome screen
- [ ] Locate "🔬 Enable Testing Mode" checkbox
- [ ] Check the checkbox
- [ ] Navigate to main menu
- [ ] Go to Advanced Settings
- [ ] Verify advanced settings checkbox is also checked (synced)
- [ ] Start camera session
- [ ] Verify calibration axes are visible
- [ ] Verify device info overlay is visible

### Advanced Settings Checkbox Test
- [ ] Open application and go to main menu
- [ ] Expand "⚙️ Advanced Settings"
- [ ] Locate "🔬 Testing Mode" checkbox
- [ ] Check the checkbox
- [ ] Return to welcome screen
- [ ] Verify welcome checkbox is also checked (synced)
- [ ] Start camera session
- [ ] Verify calibration axes are visible

### State Persistence Test
- [ ] Enable Testing Mode via any method
- [ ] Close browser tab
- [ ] Open application in new tab (same URL, no parameters)
- [ ] Verify Testing Mode is still enabled
- [ ] Disable Testing Mode
- [ ] Close and reopen browser
- [ ] Verify Testing Mode is disabled
- [ ] Clear localStorage
- [ ] Verify Testing Mode resets to disabled

## 3D Visualization Verification

### Axes Rendering
- [ ] Start camera with Testing Mode enabled
- [ ] Point at marker and verify all three axes appear:
  - [ ] Red axis (X) points to the right
  - [ ] Green axis (Y) points upward
  - [ ] Blue axis (Z) points forward
- [ ] Verify each axis extends approximately 1 meter
- [ ] Verify axes originate from marker center

### Origin Sphere
- [ ] Verify yellow sphere appears at marker center (0,0,0)
- [ ] Verify sphere size is appropriate (not too large/small)
- [ ] Verify sphere remains centered on marker when device moves

### Tick Marks
- [ ] Count tick marks along each axis
- [ ] Verify 10 tick marks per axis (every 100mm from 100mm to 1000mm)
- [ ] Verify tick marks are perpendicular to their axis
- [ ] Verify larger ticks appear at label positions (every 200mm)
- [ ] Verify smaller ticks appear at intermediate positions

### Distance Labels
- [ ] Verify labels appear every 200mm on each axis
- [ ] Expected labels: 20cm, 40cm, 60cm, 80cm, 100cm
- [ ] Verify label text is readable
- [ ] Verify label colors match their axis colors
- [ ] Verify labels face the camera (sprite behavior)

### Arrow Cones
- [ ] Verify cone appears at end of each axis
- [ ] Verify cone color matches axis color
- [ ] Verify cone points away from origin along axis direction

## Device Overlay Verification

### Overlay Visibility
- [ ] With Testing Mode ON and marker detected:
  - [ ] Verify overlay appears in top-right corner
  - [ ] Verify overlay has dark semi-transparent background
  - [ ] Verify all text is white and readable
- [ ] With Testing Mode OFF:
  - [ ] Verify overlay is hidden

### Position Information
- [ ] Point at marker from various positions
- [ ] Verify position updates show X, Y, Z in millimeters
- [ ] Move device left/right - verify X value changes
- [ ] Move device up/down - verify Y value changes
- [ ] Move device forward/back - verify Z value changes
- [ ] Lose marker detection - verify position shows "N/A"

### Device Information
- [ ] Verify device model/type is displayed correctly
- [ ] Compare with actual device specifications
- [ ] Test on multiple devices:
  - [ ] iPhone: Should show iOS and model
  - [ ] Android: Should show Android and model
  - [ ] Desktop: Should show OS and browser

### Screen Information
- [ ] Verify screen resolution matches actual display
- [ ] Test on devices with different resolutions:
  - [ ] Low res (e.g., 720p)
  - [ ] Medium res (e.g., 1080p)
  - [ ] High res (e.g., 1440p or higher)
- [ ] Rotate device (if mobile)
- [ ] Verify resolution updates correctly

### Pixel Ratio
- [ ] Verify pixel ratio is displayed as decimal number
- [ ] Common values to expect:
  - [ ] 1.0 for standard displays
  - [ ] 2.0 for Retina/high-DPI displays
  - [ ] 3.0 for high-end mobile devices

### Marker Configuration
- [ ] Verify marker size matches configured value
- [ ] Test with different marker sizes (90mm, 148mm, 190mm)
- [ ] Verify marker type shows "AprilTag" or "ArUco"
- [ ] Verify detection mode shows "Single", "4-MARKER", or "5-MARKER"

### Update Throttling
- [ ] Observe overlay updates
- [ ] Verify updates occur approximately every 1 second (30 frames)
- [ ] Verify no excessive flickering or rapid updates

## Coordinate System Verification

### Physical Measurement Test
For each axis (X, Y, Z):
- [ ] Place ruler parallel to axis in AR view
- [ ] Align ruler's 0cm with origin (yellow sphere)
- [ ] Verify tick marks align with ruler markings every 10cm
- [ ] Verify labels (20cm, 40cm, etc.) align with ruler
- [ ] Record any discrepancies (should be within ±5mm)

### Right-Handed System Verification
- [ ] Place marker on flat surface
- [ ] Verify X-axis points to marker's right edge
- [ ] Verify Y-axis points upward from marker surface
- [ ] Verify Z-axis points forward (away from marker)
- [ ] Use right-hand rule to confirm coordinate system
  - [ ] Thumb = X (right)
  - [ ] Index = Y (up)
  - [ ] Middle = Z (forward)

## Cross-Device Calibration Test

### Setup
- [ ] Prepare 3+ test devices
- [ ] Enable Testing Mode on all devices
- [ ] Use same marker and marker size configuration
- [ ] Use controlled lighting

### Consistency Test
- [ ] Point all devices at same marker simultaneously
- [ ] Record device info from each:
  - [ ] Position (X, Y, Z)
  - [ ] Device model
  - [ ] Screen resolution
  - [ ] Pixel ratio
- [ ] Compare position readings:
  - [ ] X coordinates should match within ±10mm
  - [ ] Y coordinates should match within ±10mm
  - [ ] Z coordinates should match within ±15mm
- [ ] Note any outliers and device-specific issues

### Scale Verification
- [ ] Place physical object at known distance (e.g., 50cm) along Z-axis
- [ ] Measure reported Z coordinate on each device
- [ ] Calculate error percentage: `|(reported - actual) / actual| * 100`
- [ ] Acceptable error: <5% at distances of 30-100cm

## Performance Testing

### Frame Rate Test
- [ ] Enable Testing Mode
- [ ] Start camera session
- [ ] Open browser DevTools and check FPS
- [ ] Record FPS with Testing Mode ON
- [ ] Disable Testing Mode (keep session running)
- [ ] Record FPS with Testing Mode OFF
- [ ] Calculate FPS impact: `(FPS_ON - FPS_OFF) / FPS_OFF * 100`
- [ ] Verify impact is <5%

### Memory Usage Test
- [ ] Open browser DevTools Performance Monitor
- [ ] Record baseline memory usage
- [ ] Enable Testing Mode and start session
- [ ] Record memory usage with calibration axes visible
- [ ] Calculate memory footprint of Testing Mode
- [ ] Verify additional memory usage is <5MB

### Stability Test
- [ ] Enable Testing Mode
- [ ] Run session continuously for 5 minutes
- [ ] Verify no memory leaks (memory should stabilize)
- [ ] Verify axes remain stable and don't degrade
- [ ] Verify device info continues to update correctly

## Edge Cases and Error Handling

### No Marker Detection
- [ ] Enable Testing Mode
- [ ] Start session but don't show marker
- [ ] Verify device info shows "N/A" for position
- [ ] Verify other device info still displays correctly
- [ ] Show marker - verify position updates resume

### Marker Loss
- [ ] Detect marker with Testing Mode ON
- [ ] Quickly hide marker
- [ ] Verify axes remain at last known position (smoothing)
- [ ] Verify position in overlay updates to "N/A"
- [ ] Re-show marker - verify tracking resumes

### Browser Compatibility
- [ ] Test on Chrome (desktop & mobile)
- [ ] Test on Safari (iOS & macOS)
- [ ] Test on Firefox (desktop & mobile)
- [ ] Test on Edge (desktop)
- [ ] Document any browser-specific issues

### Screen Rotation (Mobile)
- [ ] Start session in portrait mode
- [ ] Verify axes and overlay appear correctly
- [ ] Rotate device to landscape
- [ ] Verify axes, overlay, and device info adjust correctly
- [ ] Rotate back to portrait
- [ ] Verify everything still works

## Documentation Verification

- [ ] Verify TESTING_MODE_GUIDE.md is complete and accurate
- [ ] Verify TESTING_MODE_QUICKREF.md is complete and accurate
- [ ] Verify TESTING_MODE_IMPLEMENTATION_SUMMARY.md is complete and accurate
- [ ] Check all links in documentation work
- [ ] Verify code examples are syntactically correct
- [ ] Ensure screenshots (if any) are up-to-date

## Test Results Template

```markdown
## Test Results

**Date:** YYYY-MM-DD
**Tester:** [Name]
**Environment:** [Location, Lighting Conditions]

### Devices Tested
1. [Device 1 - Model, OS, Browser]
2. [Device 2 - Model, OS, Browser]
3. [Device 3 - Model, OS, Browser]

### Passed Tests
- [List of passed test sections]

### Failed Tests
- [List of failed tests with details]

### Issues Found
1. **Issue:** [Description]
   - **Severity:** Critical/High/Medium/Low
   - **Steps to Reproduce:** [Steps]
   - **Expected:** [Expected behavior]
   - **Actual:** [Actual behavior]
   - **Device:** [Affected device(s)]

### Measurement Accuracy
- **X-axis error:** ±[X]mm
- **Y-axis error:** ±[Y]mm
- **Z-axis error:** ±[Z]mm
- **Overall accuracy:** [Pass/Fail]

### Performance Metrics
- **FPS Impact:** [X]%
- **Memory Footprint:** [X]MB
- **Stability:** [Pass/Fail]

### Recommendations
- [Any recommendations for improvements]

### Sign-off
Testing Mode is [APPROVED / NEEDS REVISION] for production release.

Signed: _______________
```

## Sign-off Criteria

Testing Mode can be approved for production when:
- [ ] All UI controls work correctly across devices
- [ ] 3D visualization renders accurately on all test devices
- [ ] Device overlay displays correct information
- [ ] Coordinate system is verified with physical measurements
- [ ] Cross-device measurements are consistent (within acceptable error)
- [ ] Performance impact is <5% FPS and <5MB memory
- [ ] No critical bugs found
- [ ] All documentation is complete and accurate
- [ ] At least 3 different devices tested successfully
