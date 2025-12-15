# UI Configuration Guide

## Overview

This guide explains how to configure and use the Clearance Wizard UI to select marker types, sizes, and other detection parameters for optimal AR performance.

## Table of Contents

1. [Marker Type Selection](#marker-type-selection)
2. [Marker Dictionary/Family Selection](#marker-dictionaryfamily-selection)
3. [Marker Size Configuration](#marker-size-configuration)
4. [Detection Mode Selection](#detection-mode-selection)
5. [Advanced Settings](#advanced-settings)
6. [Troubleshooting](#troubleshooting)

## Marker Type Selection

The UI supports two types of AR markers, each with different characteristics:

### ArUco Markers

**Characteristics:**
- Fast detection speed (5-10ms per frame)
- Good accuracy for most use cases
- Wide industry support
- Multiple dictionary sizes available

**Best For:**
- General AR applications
- When speed is priority
- Standard installations

**How to Use:**
1. Open the app and tap "Get Started"
2. Select "ArUco" from the **Marker Type** dropdown
3. Choose your ArUco dictionary (DICT_4X4_50 recommended)

### AprilTag Markers

**Characteristics:**
- High detection accuracy
- Better performance at steep angles
- More robust in challenging conditions
- Industry standard for robotics

**Best For:**
- Precision measurements
- Difficult viewing angles
- Low-light conditions
- Professional applications

**How to Use:**
1. Open the app and tap "Get Started"
2. Select "✨ AprilTag" from the **Marker Type** dropdown
3. Choose your AprilTag family (tag36h11 recommended)

## Marker Dictionary/Family Selection

### ArUco Dictionaries

When using ArUco markers, you can select from various dictionaries:

#### Available Dictionaries

| Dictionary | IDs Available | Best For |
|------------|--------------|----------|
| **DICT_4X4_50** ⭐ | 0-49 | General use, fastest detection |
| DICT_4X4_100 | 0-99 | More marker IDs |
| DICT_4X4_250 | 0-249 | Large installations |
| DICT_4X4_1000 | 0-999 | Maximum marker variety |
| DICT_5X5_50 | 0-49 | Better accuracy than 4x4 |
| DICT_5X5_100 | 0-99 | Balanced accuracy/speed |
| DICT_6X6_50 | 0-49 | High accuracy |
| DICT_7X7_50 | 0-49 | Maximum accuracy |

**Recommendation:** Use **DICT_4X4_50** for best balance of speed and reliability.

**How to Select:**
1. Choose "ArUco" as marker type
2. Select dictionary from the **ArUco Dictionary** dropdown
3. The dictionary name must match your printed markers

**Generating ArUco Markers:**
- Visit [ArUco Generator](https://chev.me/arucogen/)
- Select the same dictionary you chose in the app
- Download and print markers

### AprilTag Families

When using AprilTag markers, you can select from various families:

#### Available Families

| Family | IDs Available | Hamming Distance | Best For |
|--------|--------------|------------------|----------|
| **tag36h11** ⭐ | 0-586 | 11 | Best error correction |
| tag36h10 | 0-2,320 | 10 | More IDs, good accuracy |
| tag36h9 | 0-??? | 9 | Many IDs available |
| tag25h9 | 0-34 | 9 | Smaller markers |
| tag16h5 | 0-29 | 5 | Fastest detection |
| tagStandard41h12 | 0-2,115 | 12 | Maximum error correction |

**Recommendation:** Use **tag36h11** for best detection accuracy and error correction.

**Hamming Distance:** Higher number = better error correction = more robust detection

**How to Select:**
1. Choose "✨ AprilTag" as marker type
2. Select family from the **AprilTag Family** dropdown
3. The family must match your printed markers

**Generating AprilTag Markers:**
1. Tap "Get Markers" on the welcome screen
2. Click "Generate AprilTag" button
3. Select the same family you chose in the app
4. Download and print markers

## Marker Size Configuration

Accurate marker size is **critical** for correct pose estimation and measurements.

### Measurement Guidelines

**IMPORTANT:** Always measure the **BLACK SQUARE ONLY**, excluding the white border.

```
┌───────────────────────┐
│   White Border        │  ← Do NOT measure this
│  ┌─────────────────┐  │
│  │                 │  │
│  │  Black Square   │  │  ← Measure ONLY this
│  │                 │  │
│  └─────────────────┘  │
│                       │
└───────────────────────┘
```

### Single Marker Mode

**Preset Sizes:**
- **45mm** - Close-up work (0.2m - 1m)
- **53mm** - Credit card size
- **148mm (A5)** - Better stability (0.5m - 3m) ⭐
- **167mm (A4)** - Long distance work
- **190mm** - Best for distance (0.7m - 5m) ⭐⭐⭐
- **Custom** - Enter your own size

**How to Configure:**
1. Select detection mode (Single Marker)
2. Choose from preset sizes or select "Custom"
3. If custom, enter exact size in millimeters
4. Verify measurement before starting

### Multi-Marker Mode

For 4-marker or 5-marker detection:

**Recommended Size:** 90mm per marker

**How to Configure:**
1. Select detection mode (4-Marker or 5-Marker)
2. Enter marker size in the **Marker Size** input field
3. All markers must be the same size
4. Maintain consistent spacing between markers

### Size Recommendations by Distance

| Marker Size | Optimal Distance | Use Case |
|-------------|------------------|----------|
| 45mm | 0.2m - 1m | Close inspection |
| 90mm | 0.5m - 2m | Multi-marker setups |
| 148mm | 0.5m - 3m | Standard installations |
| 190mm | 0.7m - 5m | Large rooms, distant objects |

**Rule of Thumb:** Larger markers = better tracking stability at distance

## Detection Mode Selection

Choose the detection mode based on your measurement needs:

### Single Marker

**Description:** Detects one marker and displays AR overlay relative to that marker.

**Use Cases:**
- Quick clearance checks
- Simple measurements
- Appliance positioning

**Configuration:**
1. Select "📍 Single Marker" from **Detection Mode**
2. Configure marker type and size
3. Place single marker on reference surface
4. Point camera at marker

### 4-Marker Mode

**Description:** Detects 4 markers arranged in a rectangle for enhanced stability.

**Use Cases:**
- Boiler installations
- Large appliances
- Stable multi-point reference

**Configuration:**
1. Select "📐 4-Marker (Boiler)" from **Detection Mode**
2. Configure marker type and size
3. Print and arrange 4 markers in corners of a rectangle
4. Point camera to see all 4 markers

**Marker Arrangement:**
```
Marker 0 ───────── Marker 1
   │                   │
   │                   │
   │                   │
Marker 3 ───────── Marker 2
```

### 5-Marker Mode

**Description:** Detects 5 markers (4 corners + 1 center) for maximum accuracy.

**Use Cases:**
- Window installations
- Precise positioning
- Reference plane definition

**Configuration:**
1. Select "🪟 5-Marker (Window)" from **Detection Mode**
2. Configure marker type and size
3. Print and arrange 5 markers (4 corners + center)
4. Point camera to see all 5 markers

**Marker Arrangement:**
```
Marker 0 ───────── Marker 1
   │                   │
   │     Marker 4      │
   │                   │
Marker 3 ───────── Marker 2
```

## Advanced Settings

Access advanced settings by expanding the "⚙️ Advanced Settings" section:

### Depth Offset

**Description:** Fine-tune the depth position of the AR overlay.

**Use:**
- Compensate for camera calibration differences
- Adjust for specific viewing conditions
- Fine-tune measurement accuracy

**Configuration:**
1. Expand "Advanced Settings"
2. Enter offset value in millimeters (-1000 to +1000)
3. Positive values push overlay away from camera
4. Negative values pull overlay toward camera

### Testing Mode 🔬

**Description:** Shows calibrated 3D axes with distance labels for validation.

**Features:**
- Color-coded axes (X=red, Y=green, Z=blue)
- Distance tick marks every 100mm
- Labels every 200mm showing centimeters
- Device info overlay with real-time position

**Use:**
1. Check "🔬 Testing Mode" checkbox
2. Start camera session
3. Observe colored axes and distance labels
4. Verify measurements against physical measurements

**See also:** [TESTING_MODE_GUIDE.md](TESTING_MODE_GUIDE.md)

### Debug Plane

**Description:** Shows test objects (plane, sphere, cube) with axis lines.

**Use:**
1. Check "🎯 Debug Plane" checkbox
2. Start camera session
3. Verify AR pose alignment with test objects
4. Useful for debugging pose estimation issues

### Lens Correction 🔍

**Description:** Corrects for lens distortion and chromatic aberration.

**When to Use:**
- Wide-angle cameras (newer phones)
- Markers near frame edges
- Steep viewing angles
- Inconsistent detection at edges

**Configuration:**
1. Expand "Advanced Settings"
2. Check "🔍 Lens Correction" checkbox
3. Device-specific profiles automatically applied

**See also:** [LENS_CORRECTION.md](LENS_CORRECTION.md)

## Integration with AR Engine API

The UI can optionally connect to the AR Engine Backend API for enhanced processing:

### Prerequisites

1. **Start the API server:**
   ```bash
   cd python-dev
   python ar_engine_api.py --host 127.0.0.1 --port 5000
   ```

2. **Enable API mode in UI** (requires code modification)

### API Configuration Flow

1. UI captures video frame
2. Encodes frame as base64 JPEG
3. Sends to API with marker configuration:
   - Marker type (aruco/apriltag)
   - Dictionary/family
   - Marker size
   - Expected marker count
4. API processes and returns detections
5. UI updates AR overlay with detected poses

### Example Integration

```javascript
// Configure API detection
async function detectWithAPI(videoElement) {
  const canvas = document.createElement('canvas');
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(videoElement, 0, 0);
  
  const imageB64 = canvas.toDataURL('image/jpeg').split(',')[1];
  
  const response = await fetch('http://127.0.0.1:5000/api/v1/detect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image: imageB64,
      marker_type: document.getElementById('input-marker-type').value,
      marker_size: parseFloat(getMarkerSizeInMeters()),
      marker_count: getExpectedMarkerCount(),
      aruco_dict: document.getElementById('input-aruco-dict').value,
      tag_family: document.getElementById('input-apriltag-family').value
    })
  });
  
  const data = await response.json();
  return data.detections;
}
```

## Troubleshooting

### Marker Not Detected

**Possible Causes:**
- ✗ Incorrect marker type selected
- ✗ Wrong dictionary/family selected
- ✗ Marker too small or too far
- ✗ Poor lighting conditions
- ✗ Marker damaged or printed poorly

**Solutions:**
1. ✓ Verify marker type matches printed markers
2. ✓ Check dictionary/family selection
3. ✓ Move closer to marker
4. ✓ Improve lighting
5. ✓ Reprint marker at higher quality

### Inaccurate Measurements

**Possible Causes:**
- ✗ Incorrect marker size entered
- ✗ Measuring white border instead of black square
- ✗ Camera calibration issues

**Solutions:**
1. ✓ Re-measure marker (black square only)
2. ✓ Update marker size in app
3. ✓ Enable lens correction
4. ✓ Use larger markers

### Unstable Tracking

**Possible Causes:**
- ✗ Marker too small for distance
- ✗ Poor lighting
- ✗ Motion blur
- ✗ Viewing angle too steep

**Solutions:**
1. ✓ Use larger marker
2. ✓ Improve lighting
3. ✓ Move slower/steadier
4. ✓ Change viewing angle
5. ✓ Use multi-marker mode

### Multi-Marker Detection Issues

**Possible Causes:**
- ✗ Not all markers visible in frame
- ✗ Markers too close together
- ✗ Inconsistent marker sizes

**Solutions:**
1. ✓ Ensure all markers visible simultaneously
2. ✓ Increase spacing between markers
3. ✓ Verify all markers same size
4. ✓ Check marker IDs are sequential (0,1,2,3,4)

## Best Practices

### For Best Results

1. **Lighting:**
   - Use even, diffuse lighting
   - Avoid harsh shadows
   - Avoid direct sunlight on markers

2. **Marker Quality:**
   - Print on white paper
   - Use black ink (not dark gray)
   - Ensure sharp edges
   - Avoid damage or wear

3. **Marker Placement:**
   - Flat, stable surface
   - Perpendicular to camera when possible
   - Avoid curved or uneven surfaces

4. **Camera Technique:**
   - Hold device steady
   - Frame marker completely
   - Avoid excessive motion
   - Maintain appropriate distance

5. **Configuration:**
   - Measure marker size accurately
   - Select correct marker type/dictionary
   - Use larger markers when possible
   - Enable lens correction if needed

## Quick Reference

| Setting | Recommended Value | Why |
|---------|-------------------|-----|
| Marker Type | AprilTag | Better accuracy |
| AprilTag Family | tag36h11 | Best error correction |
| ArUco Dictionary | DICT_4X4_50 | Best balance |
| Marker Size (single) | 190mm | Best stability |
| Marker Size (multi) | 90mm | Optimal for multi-marker |
| Detection Mode | Based on use case | - |
| Lens Correction | Enabled | Better edge detection |
| Testing Mode | Optional | For validation |

## Additional Resources

- **Marker Guide:** [MARKER_GUIDE.md](MARKER_GUIDE.md)
- **Testing Mode:** [TESTING_MODE_GUIDE.md](TESTING_MODE_GUIDE.md)
- **Lens Correction:** [LENS_CORRECTION.md](LENS_CORRECTION.md)
- **AR Engine API:** [python-dev/AR_ENGINE_API.md](python-dev/AR_ENGINE_API.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)

## Support

For additional help:
1. Check the [README.md](README.md) for general information
2. Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if available
3. Open an issue on GitHub

---

**Version:** 2.0  
**Last Updated:** December 2025
