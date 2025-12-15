# AR Engine Testing Instructions

## Overview

This document provides comprehensive testing instructions to verify the integration between the AR Engine Backend API and the UI, as well as testing the individual components.

## Prerequisites

### Required Software

- Python 3.7 or higher
- pip package manager
- Modern web browser (Chrome, Safari, Firefox, Edge)
- Local web server (Python's http.server, Node's http-server, etc.)

### Required Packages

```bash
cd python-dev
pip install -r requirements.txt
```

**Key packages:**
- flask>=2.0.0
- flask-cors>=3.0.0
- opencv-python>=4.5.0
- numpy>=1.20.0
- apriltag>=0.0.16 (optional but recommended)

## Component Testing

### 1. AR Engine API Testing

#### 1.1 Start the API Server

**Terminal 1:**
```bash
cd /home/runner/work/Clearance-wizard/Clearance-wizard/python-dev
python ar_engine_api.py --host 127.0.0.1 --port 5000
```

**Expected Output:**
```
 * Serving Flask app 'ar_engine_api'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
```

#### 1.2 Run Automated Tests

**Terminal 2:**
```bash
cd /home/runner/work/Clearance-wizard/Clearance-wizard/python-dev
python test_ar_engine_api.py
```

**Expected Test Results:**
```
============================================================
AR Engine API Test Suite
============================================================

=== Testing Health Check ===
Status Code: 200
Status: ok
Features: {
  "apriltag": true,
  "aruco": true
}
✓ Health check passed

=== Testing Supported Markers ===
Status Code: 200
Marker Types: {...}
✓ Supported markers test passed

=== Testing Camera Configuration ===
Status Code: 200
Status: configured
✓ Camera configuration test passed

=== Testing ArUco Detection ===
Status Code: 200
Status: success
Detected Count: 1
✓ ArUco detection test passed

=== Testing Multi-Marker Detection ===
Status Code: 200
Detected Count: 4
✓ Multi-marker detection test passed

=== Testing Marker Generation ===
Status Code: 200
✓ Marker generation test passed

=== Testing Error Handling ===
✓ Missing image error handled correctly
✓ Invalid marker type error handled correctly
✓ Error handling tests passed

============================================================
Test Results Summary
============================================================
health               : ✓ PASS
supported_markers    : ✓ PASS
camera_config        : ✓ PASS
aruco_detection      : ✓ PASS
multi_marker         : ✓ PASS
marker_generation    : ✓ PASS
error_handling       : ✓ PASS

============================================================
Total: 7/7 tests passed
============================================================
```

#### 1.3 Manual API Testing

**Test Health Endpoint:**
```bash
curl http://127.0.0.1:5000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-12-15T06:30:00.000Z",
  "features": {
    "apriltag": true,
    "aruco": true
  }
}
```

**Test Supported Markers:**
```bash
curl http://127.0.0.1:5000/api/v1/supported_markers
```

**Expected Response:**
```json
{
  "marker_types": {
    "apriltag": {
      "available": true,
      "families": ["tag36h11", "tag25h9", ...],
      "default": "tag36h11"
    },
    "aruco": {
      "available": true,
      "dictionaries": ["DICT_4X4_50", ...],
      "default": "DICT_4X4_50"
    }
  }
}
```

### 2. UI Testing

#### 2.1 Start Web Server

**Terminal 3:**
```bash
cd /home/runner/work/Clearance-wizard/Clearance-wizard
python -m http.server 8000
```

**Expected Output:**
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

#### 2.2 Open Application

1. Open browser and navigate to: `http://localhost:8000`
2. Wait for OpenCV.js to load
3. Check browser console for any errors

**Expected Console Output:**
```
OpenCV loaded from local file
OpenCV Ready
AprilTag detector initialized
```

#### 2.3 Test UI Configuration Options

**Test 1: Marker Type Selection**
1. Click "🚀 Get Started"
2. Locate "🏷️ Marker Type" dropdown
3. Select "ArUco"
   - ✓ ArUco Dictionary dropdown should appear
   - ✓ AprilTag Family dropdown should be hidden
4. Select "✨ AprilTag"
   - ✓ AprilTag Family dropdown should appear
   - ✓ ArUco Dictionary dropdown should be hidden

**Test 2: Dictionary/Family Selection**
1. With "ArUco" selected:
   - ✓ Verify DICT_4X4_50 is default
   - ✓ Open dropdown and check all options visible
   - ✓ Select DICT_5X5_50
2. With "AprilTag" selected:
   - ✓ Verify tag36h11 is default
   - ✓ Open dropdown and check all options visible
   - ✓ Select tag25h9

**Test 3: Marker Size Configuration**
1. With "Single Marker" detection mode:
   - ✓ Preset size dropdown should be visible
   - ✓ Select "190mm (Recommended) ⭐"
   - ✓ Select "Custom..."
   - ✓ Custom input field should appear
   - ✓ Enter "120" and verify acceptance
2. With "4-Marker" detection mode:
   - ✓ Number input should appear
   - ✓ Preset dropdown should be hidden
   - ✓ Enter "90" and verify acceptance

**Test 4: Detection Mode Selection**
1. Select "📍 Single Marker"
   - ✓ Preset size dropdown visible
2. Select "📐 4-Marker (Boiler)"
   - ✓ Number input visible
3. Select "🪟 5-Marker (Window)"
   - ✓ Number input visible

**Test 5: Advanced Settings**
1. Expand "⚙️ Advanced Settings"
   - ✓ Depth Offset input visible
   - ✓ Testing Mode checkbox visible
   - ✓ Debug Plane checkbox visible
   - ✓ Lens Correction checkbox visible
2. Check "🔬 Testing Mode"
   - ✓ Checkbox state changes
3. Check "🎯 Debug Plane"
   - ✓ Checkbox state changes

### 3. Camera Detection Testing

#### 3.1 Prepare Test Markers

**Option A: Generate ArUco Marker**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/generate_marker \
  -H "Content-Type: application/json" \
  -d '{"marker_type":"aruco","marker_id":0,"size_pixels":400}' \
  --output test_marker_0.png
```
Print the generated marker.

**Option B: Use In-App Generator**
1. On welcome screen, click "Get Markers"
2. Click "Generate AprilTag" button
3. Select tag36h11 family
4. Enter ID 0
5. Download and print

**Measure Marker:**
- Measure BLACK SQUARE ONLY (not white border)
- Record exact measurement in mm

#### 3.2 Test Single Marker Detection

1. In UI, configure:
   - Detection Mode: "Single Marker"
   - Marker Type: Match your printed marker
   - Dictionary/Family: Match your printed marker
   - Marker Size: Enter your measured size
2. Click "Start Camera"
3. Allow camera access
4. Point camera at marker

**Expected Behavior:**
- ✓ Status pill shows "Looking..."
- ✓ When marker detected: "✓ Tracking"
- ✓ AR overlay appears aligned with marker
- ✓ Appliance model rendered in 3D
- ✓ Clearance zones visible

**Verify:**
- Check browser console for detection logs
- Verify marker ID matches printed marker
- Test different distances (0.5m - 2m)
- Test different angles

#### 3.3 Test Multi-Marker Detection

1. Print 4 markers (IDs 0, 1, 2, 3)
2. Arrange in rectangle pattern:
   ```
   0 ─────── 1
   │         │
   │         │
   3 ─────── 2
   ```
3. In UI, configure:
   - Detection Mode: "4-Marker"
   - Marker Type: Match your markers
   - Marker Size: Enter measured size
4. Click "Start Camera"
5. Point camera to see all 4 markers

**Expected Behavior:**
- ✓ Status shows "Found X of 4 markers"
- ✓ When all 4 detected: "✓ All markers found"
- ✓ AR overlay spans across all markers
- ✓ More stable tracking than single marker

#### 3.4 Test Testing Mode

1. Enable "🔬 Testing Mode" checkbox
2. Start camera session
3. Point at marker

**Expected Behavior:**
- ✓ Colored axes appear (X=red, Y=green, Z=blue)
- ✓ Tick marks every 100mm
- ✓ Distance labels every 200mm
- ✓ Device info overlay shows:
  - Position (x, y, z)
  - Device name
  - Screen resolution
  - Pixel ratio
  - Marker size
  - Marker type
  - Detection mode

**Verify:**
- Measure physical distance along X axis
- Compare with displayed label
- Tolerance: ±5% acceptable

#### 3.5 Test Lens Correction

1. Enable "🔍 Lens Correction" checkbox
2. Start camera session
3. Move marker to edge of frame
4. Compare detection with/without correction

**Expected Behavior:**
- ✓ Better detection at frame edges
- ✓ More consistent tracking
- ✓ Reduced false positives

### 4. Integration Testing

#### 4.1 API + UI Integration (Optional)

**Note:** This requires code modification to enable API mode in UI.

**Setup:**
1. Keep API server running (Terminal 1)
2. Keep web server running (Terminal 3)
3. Modify UI JavaScript to use API (see UI_CONFIGURATION_GUIDE.md)

**Test API Detection:**
1. Start camera session
2. Point at marker
3. Check network tab in browser DevTools
4. Verify POST requests to `/api/v1/detect`
5. Verify responses contain detections

**Expected Behavior:**
- ✓ API requests sent every frame
- ✓ Responses received within 50ms
- ✓ Detection results rendered in UI
- ✓ No CORS errors

### 5. Performance Testing

#### 5.1 API Performance

**Test Detection Speed:**
```bash
cd python-dev
python -c "
import cv2
import numpy as np
import time
import requests
import base64

# Create test image
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
marker = cv2.aruco.generateImageMarker(aruco_dict, 0, 400)
test_image = cv2.copyMakeBorder(marker, 150, 150, 150, 150, cv2.BORDER_CONSTANT, value=255)

# Encode to base64
_, buffer = cv2.imencode('.jpg', test_image)
image_b64 = base64.b64encode(buffer).decode('utf-8')

# Test 100 detections
times = []
for i in range(100):
    start = time.time()
    response = requests.post('http://127.0.0.1:5000/api/v1/detect', json={
        'image': image_b64,
        'marker_type': 'aruco',
        'marker_size': 0.19
    })
    end = time.time()
    if response.status_code == 200:
        times.append(end - start)

print(f'Average detection time: {np.mean(times)*1000:.2f} ms')
print(f'Median: {np.median(times)*1000:.2f} ms')
print(f'Min: {np.min(times)*1000:.2f} ms')
print(f'Max: {np.max(times)*1000:.2f} ms')
"
```

**Expected Results:**
- Average: 20-50ms
- Median: 15-40ms
- Target: <50ms for real-time

#### 5.2 UI Performance

**In Browser Console:**
```javascript
// Test detection speed
let frameCount = 0;
let startTime = Date.now();

// Run for 10 seconds
setTimeout(() => {
  const elapsed = (Date.now() - startTime) / 1000;
  const fps = frameCount / elapsed;
  console.log(`FPS: ${fps.toFixed(2)}`);
}, 10000);

// Increment on each detection
// (Add this to your detection loop)
frameCount++;
```

**Expected Results:**
- Client-side detection: 20-30 FPS
- API-based detection: 10-20 FPS (due to network overhead)

### 6. Error Testing

#### 6.1 Test API Error Handling

**Test 1: Missing Image**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/detect \
  -H "Content-Type: application/json" \
  -d '{"marker_type":"aruco"}'
```

**Expected:** HTTP 400, error message about missing image

**Test 2: Invalid Marker Type**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/detect \
  -H "Content-Type: application/json" \
  -d '{"image":"invalid","marker_type":"unknown"}'
```

**Expected:** HTTP 400, error about unknown marker type

**Test 3: Invalid Image Data**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/detect \
  -H "Content-Type: application/json" \
  -d '{"image":"notbase64data","marker_type":"aruco"}'
```

**Expected:** HTTP 400, error about image decode failure

#### 6.2 Test UI Error Handling

**Test 1: No Camera Access**
1. Deny camera permission
2. Click "Start Camera"
3. **Expected:** Error message displayed

**Test 2: Invalid Marker Size**
1. Select "Custom" marker size
2. Enter "0" or negative number
3. **Expected:** Validation prevents start

**Test 3: OpenCV.js Load Failure**
1. Disconnect internet (if using CDN)
2. Reload page
3. **Expected:** Error message about OpenCV load failure

### 7. Cross-Browser Testing

Test on multiple browsers:

| Browser | Version | Expected Result |
|---------|---------|----------------|
| Chrome | 90+ | ✓ Full support |
| Safari | 14+ | ✓ Full support |
| Firefox | 88+ | ✓ Full support |
| Edge | 90+ | ✓ Full support |

**Test for Each Browser:**
1. Open application
2. Verify OpenCV.js loads
3. Test marker detection
4. Test UI responsiveness
5. Check console for errors

### 8. Mobile Testing

Test on mobile devices:

**iOS:**
1. iPhone (iOS 14+)
2. iPad (iPadOS 14+)

**Android:**
1. Samsung Galaxy (Android 10+)
2. Google Pixel (Android 10+)

**Test Cases:**
1. Camera access
2. Marker detection
3. Touch controls
4. Orientation changes
5. PWA installation
6. Offline functionality

### 9. Test Checklist

#### API Tests
- [ ] Health check endpoint works
- [ ] Supported markers endpoint works
- [ ] Camera configuration works
- [ ] ArUco detection works
- [ ] AprilTag detection works (if available)
- [ ] Multi-marker detection works
- [ ] Marker generation works
- [ ] Error handling works
- [ ] Performance acceptable (<50ms)

#### UI Tests
- [ ] Marker type selection works
- [ ] Dictionary/family dropdowns toggle correctly
- [ ] Marker size configuration works
- [ ] Detection mode selection works
- [ ] Advanced settings work
- [ ] Camera access works
- [ ] Single marker detection works
- [ ] Multi-marker detection works
- [ ] Testing mode works
- [ ] Lens correction works
- [ ] UI responsive on mobile
- [ ] No console errors

#### Integration Tests
- [ ] UI and API communicate correctly (if enabled)
- [ ] CORS headers correct
- [ ] Data format matches expectations
- [ ] Performance acceptable for real-time use

#### Browser Compatibility
- [ ] Chrome works
- [ ] Safari works
- [ ] Firefox works
- [ ] Edge works
- [ ] Mobile browsers work

## Troubleshooting

### API Won't Start

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000
# Kill the process
kill -9 <PID>
# Or use different port
python ar_engine_api.py --port 5001
```

### Tests Fail

**Error:** `Connection refused`

**Solution:**
1. Verify API server is running
2. Check firewall settings
3. Verify port number matches

### Detection Not Working

**Possible Issues:**
1. Camera not accessible
2. Marker type mismatch
3. Dictionary/family mismatch
4. Incorrect marker size
5. Poor lighting

**Solutions:**
1. Grant camera permissions
2. Verify marker type setting
3. Verify dictionary/family setting
4. Re-measure marker size
5. Improve lighting

### Poor Performance

**Possible Causes:**
1. Large image size
2. Network latency (API mode)
3. CPU limitations

**Solutions:**
1. Reduce camera resolution
2. Use client-side detection
3. Optimize detection parameters

## Success Criteria

Tests are considered successful when:

1. ✅ All API endpoints respond correctly
2. ✅ All automated tests pass (7/7)
3. ✅ UI configuration options work as expected
4. ✅ Marker detection works for both ArUco and AprilTag
5. ✅ Multi-marker detection works reliably
6. ✅ Performance meets target (<50ms API, 20+ FPS UI)
7. ✅ No console errors during normal operation
8. ✅ Cross-browser compatibility confirmed
9. ✅ Mobile devices work correctly
10. ✅ Documentation matches actual behavior

## Reporting Issues

When reporting issues, include:

1. **Environment:**
   - OS and version
   - Browser and version
   - Python version
   - Package versions

2. **Steps to Reproduce:**
   - Exact configuration used
   - Actions taken
   - Expected vs actual behavior

3. **Logs:**
   - Browser console output
   - API server output
   - Test output (if applicable)

4. **Screenshots/Videos:**
   - UI state
   - Error messages
   - Unexpected behavior

## Next Steps

After successful testing:

1. ✅ Mark all checklist items as complete
2. ✅ Document any issues found
3. ✅ Create bug reports for failures
4. ✅ Update documentation as needed
5. ✅ Deploy to production environment
6. ✅ Monitor performance in production

---

**Version:** 1.0  
**Last Updated:** December 2025
