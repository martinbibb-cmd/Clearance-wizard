# Lens Correction Feature

## Overview

The Lens Correction feature automatically detects your device and applies distortion correction to improve marker detection accuracy. This feature corrects for chromatic aberration and lens distortion commonly found in mobile phone cameras.

## What It Does

Mobile phone cameras often have barrel distortion (lines appear curved) and chromatic aberration (color fringing at edges). These optical imperfections can reduce marker detection accuracy, especially:

- At the edges of the camera frame
- With markers at steep angles
- When using wide-angle cameras

The lens correction feature:
1. **Detects your device** automatically from the user agent
2. **Applies device-specific distortion coefficients** based on known camera characteristics
3. **Undistorts the image** before marker detection using OpenCV's undistort function
4. **Improves detection accuracy** especially for markers near frame edges

## How to Use

### Enabling Lens Correction

1. Open Clearance Genie
2. Tap "🚀 Get Started"
3. Expand "⚙️ Advanced Settings"
4. Check the box "🔍 Lens Correction (chromatic aberration)"
5. Start the camera as normal

The setting is saved to your browser's local storage and will persist across sessions.

### Supported Devices

The feature includes calibration profiles for:

**iPhone Models:**
- iPhone (generic)
- iPhone 11, 12, 13, 14, 15 series
- iPad

**Android Models:**
- Samsung Galaxy S series (SM-G*)
- Samsung Galaxy A series (SM-A*)
- Google Pixel 6, 7, 8 series
- Generic Android (default profile)

**Fallback:**
- Any device without a specific profile uses conservative default values

## Technical Details

### Distortion Coefficients

The feature uses the standard OpenCV distortion model with 5 coefficients:
- **k1, k2, k3**: Radial distortion coefficients
- **p1, p2**: Tangential distortion coefficients

Example (iPhone):
```javascript
distCoeffs: [-0.12, 0.08, 0, 0, 0]
```

Negative k1 indicates barrel distortion (most common in phone cameras).

### Device Detection

The system automatically detects your device from `navigator.userAgent` and matches it against known profiles. If no specific match is found, it falls back to conservative default values that work reasonably well across devices.

### Performance Impact

Lens correction adds minimal overhead:
- OpenCV's `cv.undistort()` is highly optimized
- Processing happens on scaled-down images (0.5x resolution)
- Typical overhead: < 2ms per frame on modern mobile devices

### When to Enable

**Enable lens correction when:**
- Using wide-angle cameras (common on recent phones)
- Detecting markers near the edges of the frame
- Working at steep angles to markers
- Experiencing inconsistent detection at frame edges

**You may not need it when:**
- Using center-mounted markers
- Working with high-end devices with computational photography corrections
- Detection is already working reliably

## Parallax Image Support

### Overview

Parallax image support is **already enabled by default** through the plane alignment feature. When the tag is detected with plane adjustment enabled, AR objects are rendered directly on the plane of the detected marker, regardless of orientation.

### How It Works

1. **Marker Detection**: System detects AprilTag or ArUco marker corners
2. **Pose Estimation**: Uses `cv.solvePnP` with `SOLVEPNP_IPPE_SQUARE` algorithm
3. **Transformation Matrix**: Computes complete 4x4 homogeneous transformation matrix
4. **Plane Alignment**: All AR objects align to the marker's plane, even if tilted or vertical

### What This Means

- **Flat markers**: Objects render perpendicular to the surface
- **Tilted markers**: Objects follow the marker's tilt
- **Vertical markers**: Objects render on vertical plane (wall-mounted)
- **Any orientation**: Tracking works regardless of marker rotation

### Technical Details

The `parallaxEnabled` flag (enabled by default in `GraphicsEngine`) controls:
- Full 3D transformation matrix application
- Quaternion-based smooth interpolation
- Coordinate system conversion (OpenCV ↔ Three.js)

See [PLANE_ALIGNMENT_TESTING.md](PLANE_ALIGNMENT_TESTING.md) for detailed testing guidelines.

## Troubleshooting

### Lens Correction Not Working

1. **Check Console**: Open browser developer tools (F12) and check for errors
2. **Verify Device Detection**: Look for "Matched device profile" message in console
3. **Try Default Profile**: If detection fails, the system uses a conservative default

### Detection Worse After Enabling

1. **Try Disabling**: Some devices already apply software corrections
2. **Check Lighting**: Poor lighting affects detection more than distortion
3. **Report Issue**: Your device may need a custom profile

### Performance Issues

If you experience lag after enabling lens correction:
1. **Disable the Feature**: Use the checkbox in Advanced Settings
2. **Check Device Resources**: Ensure sufficient memory is available
3. **Reduce Resolution**: Use smaller marker sizes or better lighting

## Adding New Device Profiles

To add a custom device profile:

1. **Calibrate Camera**: Use OpenCV calibration tools or online services
2. **Get Distortion Coefficients**: Extract k1, k2, p1, p2, k3 values
3. **Add to Database**: Edit `VisionSystem.DEVICE_PROFILES` in index.html
4. **Test Thoroughly**: Verify detection accuracy with various markers

Example:
```javascript
'My Device': {
    distCoeffs: [-0.13, 0.09, 0.001, 0.001, 0],
    fovDegrees: 62
},
```

## References

- **OpenCV Camera Calibration**: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
- **Distortion Models**: https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html
- **Plane Alignment**: See [APRILTAG_DETECTION.md](APRILTAG_DETECTION.md)

## Future Enhancements

Potential improvements:
- Dynamic calibration wizard (users calibrate their own device)
- Cloud-based profile database
- Machine learning-based distortion estimation
- Per-camera profile selection (front/rear cameras)
