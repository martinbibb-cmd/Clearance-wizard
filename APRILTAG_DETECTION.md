# AprilTag Detection Implementation

This document describes the AprilTag detection implementation in Clearance Genie.

## Overview

The application now supports both ArUco and AprilTag marker detection through a unified marker interface. Users can switch between marker types using a dropdown in the configuration menu.

## Architecture

### Unified Marker Interface

**File:** `src/detectors/types.js`

Defines the common interface for all marker detectors:

- `MarkerDetection` - Standard format for detected markers
  - `id` - Marker identifier
  - `family` - Marker family (e.g., 'DICT_4X4_50', 'tag36h11')
  - `cornersPx` - Four corner positions in pixels
  - `centerPx` - Center position in pixels
  - `confidence` - Optional detection confidence score

- `IMarkerDetector` - Interface for detector implementations
  - `detect(grayImageData, width, height)` - Returns `MarkerDetection[]`

### AprilTag Detector

**File:** `src/detectors/apriltagDetector.js`

#### Features

- Detects square markers using OpenCV contour detection
- Supports all AprilTag families (36h11, 25h9, 16h5, 36h9, 36h10)
- Async initialization to load tag family data from JSON files
- Memory-efficient with pre-allocated OpenCV Mats
- Returns detections in unified `MarkerDetection` format

#### Detection Pipeline

1. **Input Processing**
   - Accepts grayscale image data or OpenCV Mat
   - Applies Gaussian blur to reduce noise

2. **Thresholding**
   - Uses adaptive thresholding for varying lighting conditions
   - Handles both bright and dark environments

3. **Contour Detection**
   - Finds all contours in binary image
   - Filters for quadrilaterals (4-sided polygons)
   - Checks aspect ratio to ensure square-like shapes

4. **Marker Creation**
   - Extracts corner coordinates
   - Calculates center position
   - Assigns sequential ID (detection order)
   - Returns confidence score of 0.8

#### Limitations

- **No ID Decoding**: Current implementation cannot decode actual AprilTag IDs from the marker pattern. Markers are assigned sequential IDs based on detection order.
- **Future Enhancement**: Full AprilTag ID decoding would require a custom OpenCV.js build with the apriltag module.
- **Workaround**: For applications requiring specific IDs, use ArUco markers instead, or map detected positions to expected marker locations.

### VisionSystem Integration

**File:** `index.html` (VisionSystem class)

The VisionSystem class has been updated to support both marker types:

#### Initialization

```javascript
await vision.init(video, markerType);
// markerType: 'aruco' or 'apriltag'
```

- Initializes appropriate detector based on marker type
- Falls back to ArUco if AprilTag initialization fails
- Maintains backwards compatibility

#### Detection Routing

```javascript
findMarker(video, markerSize, detectionMode)
```

Routes detection to appropriate method:
- `_findAprilTagMarker()` - For AprilTag detection
- `_findArucoMarker()` - For ArUco detection (single marker)
- `_findMultipleArucoMarkers()` - For ArUco detection (multi-marker)

#### Pose Estimation

Both marker types use the same pose estimation pipeline:
- Pinhole camera model for 3D position calculation
- Perspective distortion analysis for rotation estimation
- Smooth interpolation for stable tracking

### UI Integration

**User Flow:**

1. Open Clearance Genie
2. Tap "🚀 Get Started"
3. Select "Marker Type" dropdown
   - Choose "ArUco (DICT_4X4_50)" for ArUco markers
   - Choose "✨ AprilTag (Default: tag36h11)" for AprilTag markers
4. Configure other settings (detection mode, marker size, appliance type)
5. Tap "📷 Start Camera"
6. Point camera at marker(s)

**Visual Feedback:**

- Green overlay on detected markers
- Corner highlighting
- Center checkmark
- Marker ID display
- Multi-marker progress indicators (●○○○ style)

## Usage

### For End Users

**Generating AprilTag Markers:**

1. On welcome screen, tap "Get Markers"
2. Click "Generate AprilTag" button
3. Select tag family (tag36h11 recommended)
4. Enter tag ID (0-586 for tag36h11)
5. Choose marker size (190mm recommended)
6. Download or print marker

**Using AprilTag Detection:**

1. Follow user flow above
2. Select "AprilTag" as marker type
3. Use generated AprilTag markers
4. Measure BLACK SQUARE AREA ONLY (no white border)

### For Developers

**Creating a Custom Detector:**

```javascript
class CustomDetector {
    async init() {
        // Initialize detector
    }
    
    detect(grayImageData, width, height) {
        // Return MarkerDetection[]
        return [{
            id: 0,
            family: 'custom',
            cornersPx: [{x,y}, {x,y}, {x,y}, {x,y}],
            centerPx: {x, y},
            confidence: 1.0
        }];
    }
    
    dispose() {
        // Cleanup resources
    }
}
```

**Integrating with VisionSystem:**

1. Add detector initialization in `VisionSystem.init()`
2. Add detection routing in `VisionSystem.findMarker()`
3. Handle marker format in `drawMarkerFeedback()`
4. Add UI option in marker type dropdown

## Technical Details

### Dependencies

- **OpenCV.js** - Computer vision operations
- **apriltag.js** - AprilTag generation (browser.ts compiled)
- **AprilTag families** - JSON files with tag codes (apriltag-families/)

### Performance

- Detection runs at video frame rate (~30fps)
- Scaled down image processing (0.5x) for performance
- Pre-allocated Mats to reduce GC pressure
- Efficient contour detection with area filtering

### Memory Management

- Detector properly disposes OpenCV Mats
- Reuses Mats between detections when possible
- Explicit cleanup on detector disposal

## Comparison: ArUco vs AprilTag

| Feature | ArUco | AprilTag |
|---------|-------|----------|
| ID Decoding | ✅ Full ID decoding | ⚠️ Sequential IDs only* |
| Detection Speed | Fast | Fast |
| Lighting Robustness | Good | Good |
| Angle Tolerance | Good | Good |
| False Positives | Low | Low |
| Library Support | OpenCV.js built-in | Custom implementation |
| Marker Generation | External tool | Built-in generator |

*Future enhancement: Full ID decoding requires custom OpenCV.js build

## Future Enhancements

1. **Full AprilTag Decoding**
   - Build custom OpenCV.js with apriltag module
   - Implement pattern sampling and decoding
   - Add error correction (Hamming distance checking)

2. **Tag Family Selection**
   - Add dropdown to select different tag families
   - Load appropriate family JSON dynamically

3. **Performance Optimization**
   - WebAssembly implementation for faster detection
   - Multi-threaded processing using Web Workers
   - Adaptive frame rate based on device capability

4. **Enhanced Calibration**
   - Camera calibration wizard
   - Lens distortion correction
   - Improved pose estimation accuracy

## Troubleshooting

### AprilTag Not Detecting

1. **Check marker type is selected:**
   - Ensure "AprilTag" is selected in dropdown, not "ArUco"

2. **Verify marker quality:**
   - High contrast (black on white)
   - Sharp edges (good printer quality)
   - Flat surface (no warping or creases)

3. **Improve lighting:**
   - Even lighting without shadows
   - Avoid direct glare on marker
   - Sufficient brightness

4. **Check marker size:**
   - Larger markers work better at distance
   - Marker size must match configured size
   - Measure BLACK SQUARE only (no white border)

### Detector Initialization Failed

1. **Check OpenCV.js loaded:**
   - Open browser console (F12)
   - Look for "OpenCV Ready" message
   - Verify no load errors

2. **Check AprilTagDetector loaded:**
   - Console should show "AprilTag detector initialized"
   - Verify src/detectors/apriltagDetector.js is loaded

3. **Check tag family JSON:**
   - Verify apriltag-families/36h11.json exists
   - Check network tab for 404 errors

### Performance Issues

1. **Reduce video resolution:**
   - Default is 1280px ideal width
   - Lower if device is slow

2. **Check detection scale:**
   - Default is 0.5x scaling
   - Already optimized for performance

3. **Close other apps:**
   - Free up device resources
   - Disable battery saver if active

## References

- [AprilTag Paper](https://april.eecs.umich.edu/papers/details.php?name=olson2011tags)
- [OpenCV.js Documentation](https://docs.opencv.org/4.5.2/d5/d10/tutorial_js_root.html)
- [Original AprilTag Library](https://github.com/AprilRobotics/apriltag)

## Contributing

To improve AprilTag detection:

1. Fork the repository
2. Create a feature branch
3. Implement enhancements in `src/detectors/apriltagDetector.js`
4. Test with real markers
5. Submit pull request with description

## License

Same as parent project (Clearance Genie).
