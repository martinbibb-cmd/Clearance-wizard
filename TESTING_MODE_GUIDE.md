# Testing Mode User Guide

## Overview

Testing Mode provides a visual debugging interface for validating AR measurements and ensuring cross-device calibration accuracy. It displays 3D calibration axes aligned to AprilTag/ArUco markers, helping you verify the precision of the AR positioning system.

## Enabling Testing Mode

There are three ways to enable Testing Mode:

### 1. URL Parameter
Add `?testMode=true` to the application URL:
```
http://localhost:8000/?testMode=true
```

### 2. Welcome Panel Checkbox
On the welcome screen, check the "🔬 Enable Testing Mode" checkbox before starting the application.

### 3. Advanced Settings
In the main menu, expand "⚙️ Advanced Settings" and check the "🔬 Testing Mode" checkbox.

## Visual Elements

### 3D Calibration Axes

When Testing Mode is active, you'll see three colored axes extending from the marker's center:

- **Red Axis (X)**: Points to the right
- **Green Axis (Y)**: Points upward
- **Blue Axis (Z)**: Points forward (away from the marker)

Each axis extends 1 meter (1000mm) from the origin.

### Tick Marks and Labels

- **Tick Marks**: Small perpendicular markers appear every 100mm along each axis
- **Labels**: Distance labels appear every 200mm, showing measurements in centimeters
  - Example: "10cm", "20cm", "40cm", etc.

### Origin Sphere

A **yellow sphere** marks the origin point (0,0,0) at the center of the detected marker.

### Device Information Overlay

A real-time information panel appears in the top-right corner displaying:

- **Position**: Current X, Y, Z coordinates in millimeters
- **Device**: Device model/type
- **Screen**: Screen resolution (width x height)
- **Pixel Ratio**: Device pixel ratio
- **Marker Size**: Currently configured marker size in millimeters
- **Marker Type**: AprilTag or ArUco
- **Detection**: Single, 4-marker, or 5-marker mode

## Coordinate System

The application uses a **right-handed coordinate system**:

```
      Y (Green, Up)
      |
      |
      |_____X (Red, Right)
     /
    /
   Z (Blue, Forward)
```

- **Origin (0,0,0)**: Center of the detected marker
- **X-axis**: Extends to the right (red)
- **Y-axis**: Extends upward (green)
- **Z-axis**: Extends forward, away from the marker surface (blue)

## Using Testing Mode

### Basic Validation

1. Enable Testing Mode using any of the three methods
2. Start the camera and point it at your marker
3. Observe the calibration axes appearing at the marker origin
4. Move your device to different angles and distances
5. Verify that:
   - Axes remain aligned to the marker
   - Tick marks are evenly spaced
   - Labels show correct distances
   - Origin sphere stays at marker center

### Cross-Device Testing

To validate consistency across multiple devices:

1. Enable Testing Mode on each device
2. Point all devices at the same marker
3. Compare the device info overlays:
   - Check that marker size is consistent
   - Note screen resolutions and pixel ratios
   - Verify that position readings are similar
4. Place a physical object at a known position along an axis
5. Verify that all devices report approximately the same coordinates

### Measurement Verification

To verify physical measurement accuracy:

1. Place a ruler or measuring tape along one of the axes
2. Note the tick marks and labels on the calibration axes
3. Compare the displayed measurements with the physical ruler
4. Each tick mark represents 100mm (10cm)
5. Labels show cumulative distance in centimeters

## Troubleshooting

### Axes Not Appearing

- **Check Testing Mode is enabled**: Verify checkboxes are checked
- **Restart the session**: Go back to menu and start camera again
- **Clear browser cache**: Testing mode state is stored in localStorage

### Axes Jumping or Unstable

- **Improve lighting**: Ensure marker is well-lit and evenly illuminated
- **Stabilize device**: Hold device steady or use a tripod
- **Check marker quality**: Ensure marker is flat and not damaged
- **Increase marker size**: Larger markers (190mm) provide better tracking

### Incorrect Measurements

- **Verify marker size**: Measure the BLACK SQUARE AREA ONLY (excluding white border)
- **Re-enter marker size**: Ensure the configured size matches the physical marker
- **Check marker flatness**: Warped or curved markers will cause inaccuracies
- **Test different distances**: Measurements are most accurate at 50-100cm from marker

### Device Info Not Updating

- **Updates are throttled**: Information refreshes every 30 frames (~1 second)
- **Check marker detection**: Position info only updates when marker is detected
- **Restart if frozen**: Refresh the page if overlay stops updating

## Performance Notes

- Testing Mode adds minimal overhead (<5% FPS impact)
- Memory footprint is approximately 2MB for visualization geometry
- Device info updates are throttled to avoid DOM thrashing
- All visualization geometry is static (no per-frame calculations)

## Best Practices

1. **Use consistent marker sizes**: Same physical size across all test devices
2. **Test at various distances**: 30cm to 150cm range
3. **Test at various angles**: Straight-on and oblique views
4. **Document your results**: Note device model, distance, and coordinate readings
5. **Compare against known measurements**: Use physical rulers for validation
6. **Test in different lighting**: Indoor, outdoor, bright, dim conditions

## Disabling Testing Mode

To disable Testing Mode:

1. Uncheck the Testing Mode checkbox in welcome or advanced settings
2. Calibration axes and device overlay will disappear immediately
3. The setting is saved and will persist across browser sessions

## Notes

- Testing Mode state persists in `localStorage` with key `testingMode`
- URL parameter `?testMode=true` takes precedence over stored setting
- All UI elements sync automatically when toggling Testing Mode
- Testing Mode can be toggled without restarting the camera session
