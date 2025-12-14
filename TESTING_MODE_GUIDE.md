# Testing Mode Guide 🔬

## Overview

The Testing Mode is a specialized feature designed for debugging, validation, and cross-device calibration of the AR positioning system. It provides visual feedback through calibrated 3D axes and displays detailed device information to help verify measurement accuracy.

## Features

### 1. Calibrated 3D Axes
- **X-Axis (Red)**: Extends horizontally to the right
- **Y-Axis (Green)**: Extends vertically upward  
- **Z-Axis (Blue)**: Extends forward into space
- **Origin Point**: Yellow sphere at (0, 0, 0), aligned with the detected AprilTag marker
- **Tick Marks**: Displayed every 100mm (10cm) along each axis
- **Labels**: Measurement labels every 200mm showing distance in centimeters
- **Arrows**: Directional indicators at the end of each axis

### 2. Device Information Overlay
Real-time display of:
- Device model and platform
- Screen resolution
- Device pixel ratio
- Current marker size (mm)
- Marker type (ArUco/AprilTag)
- Detection mode
- Live 3D position coordinates (X, Y, Z in mm)

## How to Enable Testing Mode

### Method 1: URL Parameter (Recommended for quick testing)
Add `?testMode=true` to the URL:
```
http://localhost:8000/?testMode=true
```

This method is ideal for:
- Quick debugging sessions
- Sharing test links with specific configurations
- One-time testing without persistent state

### Method 2: Toggle in UI (Persistent)
1. **From Welcome Screen**:
   - Check the "🔬 Testing Mode" checkbox before starting
   - Setting persists across sessions via localStorage

2. **From Advanced Settings** (during setup):
   - Expand the "⚙️ Advanced Settings" section
   - Check "🔬 Testing Mode (Show calibrated axes)"
   - Setting persists across sessions

### Method 3: Browser Console (Developer testing)
```javascript
// Enable testing mode
App.testingMode = true;
App.toggleTestingMode();

// Disable testing mode
App.testingMode = false;
App.toggleTestingMode();
```

## Using Testing Mode

### Step 1: Enable and Configure
1. Enable testing mode using one of the methods above
2. Configure your detection settings:
   - Choose marker type (ArUco or AprilTag)
   - Set marker size (measure the BLACK SQUARE only)
   - Select detection mode (single or multi-marker)
   - Choose appliance type

### Step 2: Start Camera Session
1. Click "📷 Start Camera"
2. Point camera at your marker
3. Once detected, you'll see:
   - Normal AR clearance visualization
   - Calibrated axes overlay (X=red, Y=green, Z=blue)
   - Device info overlay in top-left corner

### Step 3: Verify Calibration
1. **Check Origin Alignment**:
   - Yellow sphere should be centered on the marker
   - All three axes should originate from the marker center

2. **Verify Scale Accuracy**:
   - Use a ruler or measuring tape
   - Compare physical measurements to axis tick marks
   - Each tick = 100mm (10cm), labels show distance in cm

3. **Test Multiple Angles**:
   - Move around the marker
   - Verify axes maintain proper orientation
   - Check that measurements remain consistent

4. **Cross-Device Validation**:
   - Test on different devices (phones, tablets)
   - Compare device info overlay values
   - Verify consistent scale across devices

## Understanding the Axes

### Coordinate System
The application uses a right-handed coordinate system:
- **X-Axis (Red)**: Right direction from marker
- **Y-Axis (Green)**: Up direction from marker
- **Z-Axis (Blue)**: Forward direction (away from camera)

### Scale and Units
- **Axis Length**: 1000mm (1 meter) per axis
- **Tick Spacing**: 100mm (10cm) intervals
- **Label Frequency**: Every 200mm (20cm)
- **All measurements in millimeters** internally
- **Labels display centimeters** for readability

### Visual Elements
- **Axis Lines**: Semi-transparent colored lines with 80% opacity
- **Arrow Heads**: Cone-shaped indicators at axis ends
- **Tick Marks**: Short perpendicular lines at regular intervals
- **Labels**: White text on colored backgrounds showing distance
- **Origin Marker**: Yellow semi-transparent sphere

## Troubleshooting

### Axes Not Visible
- Ensure testing mode is enabled (check the overlay in top-left)
- Verify marker is detected (status pill shows "✓ Tracking")
- Try moving camera closer to marker
- Check lighting conditions

### Incorrect Scale
- Verify marker size is correctly entered (BLACK SQUARE only)
- Check that you're measuring physical distance correctly
- Ensure device pixel ratio is accurate (shown in overlay)
- Try recalibrating camera by restarting session

### Axes Not Aligned with Marker
- Ensure marker is flat and not warped
- Check marker detection quality (corners should be clearly visible)
- Try printing marker on stiffer paper/cardboard
- Verify marker is the correct type (ArUco vs AprilTag)

### Device Info Not Updating
- Testing mode may take a few seconds to initialize
- Position updates every 30 frames (~0.5 seconds)
- Try toggling testing mode off and on again

## Best Practices

### For Accurate Measurements
1. **Marker Quality**:
   - Use high-quality printed markers
   - Ensure crisp, black squares with clean white borders
   - Mount on rigid, flat surface (cardboard or foam board)
   - Avoid glossy paper (causes reflections)

2. **Lighting Conditions**:
   - Use even, diffused lighting
   - Avoid direct sunlight or harsh shadows
   - Ensure marker is well-lit from all angles

3. **Camera Distance**:
   - Start at recommended distances for marker size:
     - 45mm marker: 0.2m - 1m
     - 90mm marker: 0.5m - 2m
     - 190mm marker: 0.7m - 5m
   - Move closer for more detail, further for larger view

4. **Verification Process**:
   - Measure physical distances with ruler/tape
   - Compare to axis tick marks
   - Test from multiple angles
   - Document results for each device

### For Cross-Device Testing
1. **Use Same Marker**:
   - Print one marker, test on all devices
   - Ensures consistent physical reference

2. **Record Device Info**:
   - Screenshot the device info overlay
   - Note any discrepancies in measurements
   - Compare pixel ratios and screen resolutions

3. **Test in Same Environment**:
   - Use same lighting conditions
   - Same room and setup
   - Consistent camera angles

4. **Document Results**:
   - Create a testing log
   - Record device model, measurements, and observations
   - Note any calibration adjustments needed

## Advanced Usage

### Custom Axis Configuration
While not exposed in the UI, developers can modify axis parameters in the code:

```javascript
// In GraphicsEngine.showCalibrationAxes()
const axisLength = 1000;    // Axis length in mm
const tickSpacing = 100;    // Tick spacing in mm
const tickHeight = 20;      // Tick mark height in mm
```

### Integration with VIO System
Testing mode is compatible with the Python VIO (Visual-Inertial Odometry) system:
- Axes provide reference for pose estimation validation
- Device info can be logged for analysis
- Position data can be exported for comparison

### Measurement Export (Future)
Future versions may support:
- CSV export of position data
- Screenshot with measurement overlays
- Calibration report generation

## API Reference

### JavaScript Methods

```javascript
// Initialize testing mode (called on page load)
App.initTestingMode()

// Toggle testing mode on/off
App.toggleTestingMode()

// Update device information display
App.updateDeviceInfo()

// Show calibration axes
App.graphics.showCalibrationAxes()

// Hide calibration axes
App.graphics.hideCalibrationAxes()
```

### URL Parameters

```
?testMode=true          // Enable testing mode
?testMode=false         // Disable testing mode
```

### LocalStorage Keys

```javascript
localStorage.getItem('testingMode')    // Get saved preference
localStorage.setItem('testingMode', 'true')  // Enable
localStorage.setItem('testingMode', 'false') // Disable
```

## FAQ

**Q: Does testing mode affect performance?**  
A: Minimal impact. Device info updates only every 30 frames (~0.5s), and axes are static geometry.

**Q: Can I use testing mode with multi-marker detection?**  
A: Yes! Testing mode works with all detection modes (single, 4-marker, 5-marker).

**Q: Will testing mode data be saved?**  
A: Currently, no automatic saving. Use screenshots to capture device info and measurements.

**Q: Can I customize axis colors?**  
A: Not through UI, but developers can modify colors in `GraphicsEngine.showCalibrationAxes()`.

**Q: Does testing mode work offline (PWA)?**  
A: Yes! Once cached, testing mode works fully offline.

**Q: Can I print the axes for reference?**  
A: Use the camera capture button (📷) to save screenshots including axes visualization.

## Contributing

Found a bug or have suggestions for testing mode improvements?
- Open an issue on GitHub
- Include device info, screenshots, and steps to reproduce
- Suggestions for new testing features are welcome!

## See Also

- [README.md](README.md) - Main application documentation
- [MARKER_GUIDE.md](MARKER_GUIDE.md) - Comprehensive marker setup guide
- [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) - Roadmap and planned features
- [python-dev/README_VIO.md](python-dev/README_VIO.md) - VIO system documentation
