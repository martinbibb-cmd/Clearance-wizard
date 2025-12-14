# Testing Mode Verification Checklist

This document provides a step-by-step checklist for verifying that the testing mode feature works correctly across different devices and scenarios.

## Pre-Testing Setup

### Required Materials
- [ ] Printed AprilTag or ArUco marker (190mm recommended)
- [ ] Ruler or measuring tape (metric)
- [ ] Multiple test devices (phone, tablet, desktop)
- [ ] Good lighting conditions
- [ ] Flat mounting surface for marker

### Initial Configuration
- [ ] Local web server running on port 8000
- [ ] Browser with camera permissions granted
- [ ] OpenCV.js loaded successfully
- [ ] No console errors on page load

## Feature Testing

### 1. Testing Mode Activation

#### URL Parameter Method
- [ ] Navigate to `http://localhost:8000/?testMode=true`
- [ ] Verify welcome panel shows testing mode checkbox checked
- [ ] Verify device info overlay appears after clicking "Get Started"

#### UI Toggle Method (Welcome Screen)
- [ ] Navigate to `http://localhost:8000/` (no parameters)
- [ ] Check "🔬 Testing Mode" checkbox on welcome panel
- [ ] Verify checkbox remains checked
- [ ] Click "Get Started"
- [ ] Verify testing mode is active in menu

#### UI Toggle Method (Advanced Settings)
- [ ] Navigate to welcome screen
- [ ] Click "Get Started"
- [ ] Expand "⚙️ Advanced Settings"
- [ ] Check "🔬 Testing Mode" checkbox
- [ ] Start camera session
- [ ] Verify axes and device info appear

### 2. Persistence Testing

#### LocalStorage Persistence
- [ ] Enable testing mode via UI toggle
- [ ] Close browser tab
- [ ] Reopen application
- [ ] Verify testing mode is still enabled
- [ ] Verify both checkboxes show checked state

#### Toggle Synchronization
- [ ] Navigate to welcome screen with testing mode enabled
- [ ] Verify welcome checkbox is checked
- [ ] Click "Get Started" → expand Advanced Settings
- [ ] Verify menu checkbox is also checked
- [ ] Uncheck menu checkbox
- [ ] Return to welcome screen
- [ ] Verify welcome checkbox is now unchecked

### 3. Device Info Overlay

#### Display Elements
- [ ] Device model displayed correctly
- [ ] Screen resolution shown (width × height)
- [ ] Device pixel ratio displayed
- [ ] Marker size shown (matches configured value)
- [ ] Marker type shown (ArUco or AprilTag)
- [ ] Detection mode shown (single/4-marker/5-marker)

#### Position Updates
- [ ] Position coordinates initially not shown (no marker detected)
- [ ] Detect marker in camera view
- [ ] Position coordinates appear in green
- [ ] Position updates smoothly as marker moves
- [ ] Values change appropriately with marker position

#### Overlay Visibility
- [ ] Overlay appears in top-left corner
- [ ] Text is readable (white on black background)
- [ ] Overlay doesn't interfere with AR view
- [ ] Overlay visible in all screen orientations

### 4. Calibration Axes Visualization

#### Axis Appearance
- [ ] Three axes visible (red, green, blue)
- [ ] X-axis (red) extends to the right
- [ ] Y-axis (green) extends upward
- [ ] Z-axis (blue) extends forward
- [ ] Arrow heads visible at axis ends
- [ ] Yellow sphere at origin (0,0,0)

#### Axis Labels
- [ ] Tick marks visible every 10cm
- [ ] Labels show distance in centimeters
- [ ] Labels appear every 20cm (2, 4, 6, 8, etc.)
- [ ] Labels are readable (white text on colored background)
- [ ] Axis end labels (X, Y, Z) clearly visible

#### Origin Alignment
- [ ] Yellow origin sphere centered on marker
- [ ] All axes originate from marker center
- [ ] Origin moves with marker detection
- [ ] Origin remains stable during tracking

### 5. Scale Accuracy Verification

#### X-Axis (Horizontal) Measurement
- [ ] Place ruler horizontally from marker center
- [ ] Verify 10cm tick aligns with 100mm mark
- [ ] Verify 20cm label aligns with 200mm mark
- [ ] Verify 50cm aligns with 500mm mark
- [ ] Record any discrepancies: _________

#### Y-Axis (Vertical) Measurement
- [ ] Place ruler vertically from marker center
- [ ] Verify 10cm tick aligns with 100mm mark
- [ ] Verify 20cm label aligns with 200mm mark
- [ ] Verify 50cm aligns with 500mm mark
- [ ] Record any discrepancies: _________

#### Z-Axis (Depth) Measurement
- [ ] More difficult to measure physically
- [ ] Move marker closer/further from camera
- [ ] Verify Z-coordinate in overlay changes appropriately
- [ ] Verify rate of change seems proportional
- [ ] Note: Depth accuracy depends on camera calibration

### 6. Cross-Device Testing

#### Device 1: _______________
- [ ] Device model shown correctly in overlay
- [ ] Axes render properly
- [ ] Scale matches physical measurements
- [ ] Position tracking smooth
- [ ] No performance issues
- [ ] Screenshot captured: _______________

#### Device 2: _______________
- [ ] Device model shown correctly in overlay
- [ ] Axes render properly
- [ ] Scale matches physical measurements
- [ ] Position tracking smooth
- [ ] No performance issues
- [ ] Screenshot captured: _______________

#### Device 3: _______________
- [ ] Device model shown correctly in overlay
- [ ] Axes render properly
- [ ] Scale matches physical measurements
- [ ] Position tracking smooth
- [ ] No performance issues
- [ ] Screenshot captured: _______________

#### Cross-Device Consistency
- [ ] Same marker size on all devices
- [ ] Measurements consistent across devices
- [ ] No significant scale differences
- [ ] Device pixel ratios documented
- [ ] Any discrepancies noted: _________

### 7. Marker Type Compatibility

#### ArUco Markers
- [ ] Testing mode works with ArUco detection
- [ ] Axes align with marker center
- [ ] Scale accurate with physical measurements
- [ ] Position tracking stable

#### AprilTag Markers
- [ ] Testing mode works with AprilTag detection
- [ ] Axes align with marker center
- [ ] Scale accurate with physical measurements
- [ ] Position tracking stable

### 8. Detection Mode Compatibility

#### Single Marker Mode
- [ ] Testing mode works in single marker mode
- [ ] Axes track with marker movement
- [ ] Position updates shown in overlay
- [ ] No conflicts with normal AR overlay

#### 4-Marker Mode
- [ ] Testing mode works in 4-marker mode
- [ ] Axes appear once markers detected
- [ ] Position represents calculated center
- [ ] Marker feedback doesn't obscure axes

#### 5-Marker Mode
- [ ] Testing mode works in 5-marker mode
- [ ] Axes appear once markers detected
- [ ] Position represents calculated center
- [ ] Marker feedback doesn't obscure axes

### 9. Toggle On/Off Testing

#### During Active Session
- [ ] Start session with testing mode OFF
- [ ] Detect marker
- [ ] Enable testing mode via console: `App.toggleTestingMode()`
- [ ] Verify axes appear
- [ ] Verify device info overlay appears
- [ ] Disable testing mode via console
- [ ] Verify axes disappear
- [ ] Verify device info overlay disappears
- [ ] Normal AR visualization still works

### 10. Performance Testing

#### Frame Rate
- [ ] Note frame rate without testing mode: ___ fps
- [ ] Enable testing mode
- [ ] Note frame rate with testing mode: ___ fps
- [ ] Performance impact acceptable: YES / NO
- [ ] No stuttering or lag observed

#### Memory Usage
- [ ] Note memory before testing mode: ___ MB
- [ ] Enable testing mode
- [ ] Note memory with testing mode: ___ MB
- [ ] Run for 5 minutes
- [ ] Check for memory leaks: YES / NO
- [ ] Memory usage stable: YES / NO

### 11. Edge Cases

#### No Marker Detected
- [ ] Testing mode enabled
- [ ] Camera running but no marker visible
- [ ] Device info overlay shows (no position)
- [ ] Axes not visible (no tracking data)
- [ ] Status pill shows detection hints
- [ ] No errors in console

#### Poor Lighting
- [ ] Test in low light conditions
- [ ] Axes visibility acceptable
- [ ] Labels still readable
- [ ] Device info overlay readable

#### Marker at Extreme Angles
- [ ] View marker at 45° angle
- [ ] Axes maintain orientation
- [ ] Origin stays aligned with marker
- [ ] Position tracking continues

#### Multiple Markers Visible
- [ ] Place extra markers in view
- [ ] Testing mode uses primary marker
- [ ] Axes track correctly
- [ ] No confusion in detection

### 12. Documentation Verification

#### README.md
- [ ] Testing mode mentioned in features
- [ ] Link to TESTING_MODE_GUIDE.md works
- [ ] Recent updates section includes testing mode
- [ ] Quick start instructions present

#### TESTING_MODE_GUIDE.md
- [ ] All activation methods documented
- [ ] Usage instructions clear
- [ ] Troubleshooting section helpful
- [ ] API reference accurate
- [ ] Screenshots/examples would enhance (future)

## Test Results Summary

### Overall Status
- [ ] All critical features working
- [ ] No blocking issues found
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] Ready for production

### Issues Found
List any issues discovered during testing:

1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

### Recommendations
List any recommendations for improvements:

1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

### Test Environment
- **Date**: _______________
- **Tester**: _______________
- **Browser**: _______________
- **OS**: _______________
- **Test Duration**: _______________

### Sign-off
- [ ] All tests completed
- [ ] Results documented
- [ ] Issues reported
- [ ] Feature approved for release

**Tester Signature**: _______________ **Date**: _______________
