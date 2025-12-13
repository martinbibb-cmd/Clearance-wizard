# Marker Guide for Clearance Genie

## Quick Reference

### Marker Types Supported
- ✅ **ArUco Markers** (DICT_4X4_50) - Currently supported
- 🚀 **AprilTag** - Coming soon (higher accuracy)
- 📐 **Custom Squares** - Fallback detection

### Recommended Marker Sizes
| Size | Use Case | Detection Range | Tracking Stability |
|------|----------|----------------|-------------------|
| 45mm | Close-up work | 0.2m - 1m | ⭐⭐ Fair |
| 53mm | Credit card size | 0.3m - 1.5m | ⭐⭐⭐ Good |
| 148mm | A5 paper | 0.5m - 3m | ⭐⭐⭐⭐ Very Good |
| 190mm | A4 paper | 0.7m - 5m | ⭐⭐⭐⭐⭐ Excellent |

**💡 Tip:** Larger markers = better stability when viewing from distance!

---

## How to Create Markers

### Option 1: Online Generator (Recommended)
1. Visit [ArUco Marker Generator](https://chev.me/arucogen/)
2. Select dictionary: **DICT_4X4_50**
3. Choose marker IDs:
   - **Single marker mode**: Any ID (e.g., ID 1)
   - **4-marker mode**: Any 4 IDs (app detects automatically)
   - **5-marker mode**: Any 5 IDs
4. Set marker size: **190mm** (recommended)
5. Download and print on white paper

### Option 2: Manual Creation
```python
# Using Python and OpenCV
import cv2
import numpy as np

# Create ArUco dictionary
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)

# Generate marker
marker_size = 200  # pixels
marker_id = 1
marker_image = cv2.aruco.drawMarker(aruco_dict, marker_id, marker_size)

# Save marker
cv2.imwrite(f'marker_{marker_id}.png', marker_image)
```

### Option 3: Bulk Generation
```python
# Generate multiple markers for 4-marker or 5-marker mode
import cv2

aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)

# Generate 5 markers
for marker_id in range(1, 6):
    marker_image = cv2.aruco.drawMarker(aruco_dict, marker_id, 200)
    cv2.imwrite(f'marker_{marker_id}.png', marker_image)
    print(f"Generated marker ID {marker_id}")
```

---

## Measurement Guidelines

### ⚠️ Critical: Measure the BLACK SQUARE ONLY

**Correct Measurement:**
```
┌───────────────────────────┐
│        (white)            │  ← White border (IGNORE)
│    ┌──────────────┐       │
│    │              │       │
│    │   (black)    │       │  ← BLACK SQUARE (MEASURE THIS!)
│    │              │       │
│    └──────────────┘       │
│                           │
└───────────────────────────┘
```

**Why?** 
- ArUco markers have a white border that's NOT part of the marker
- Measuring the black area ensures accurate calibration
- Allows manual verification with a ruler

### Measurement Steps
1. Print marker on white paper
2. Use a ruler to measure the black square
3. Measure edge-to-edge of the BLACK area only
4. Enter this measurement in the app

---

## Printing Tips

### Best Results
- ✅ Print on **white paper** (not colored or gray)
- ✅ Use **black ink** (high contrast)
- ✅ Print at **100% scale** (no scaling in printer settings)
- ✅ Use **matte paper** (reduces glare)
- ✅ Mount on **stiff cardboard** (prevents warping)

### Avoid
- ❌ Glossy paper (causes reflections)
- ❌ Colored paper (reduces contrast)
- ❌ Scaling in printer settings
- ❌ Folded or creased markers
- ❌ Damaged or dirty markers

---

## Positioning Guide

### Single Marker Mode
```
        Camera
          📱
          |
          |
          ↓
    ┌─────────┐
    │ Marker  │  ← Place marker on wall/surface
    │   ID    │     where appliance will be installed
    └─────────┘
```

**Best Practices:**
- Place marker at center of installation area
- Ensure marker is flat against surface
- Good lighting without direct sunlight
- Camera 0.5m - 3m from marker (depending on size)

### 4-Marker Mode (Boiler Overlay)
```
    Marker 1 ●───────────● Marker 2
             │           │
             │  Boiler   │
             │   Area    │
             │           │
    Marker 3 ●───────────● Marker 4
```

**Best Practices:**
- Place markers at corners of boiler footprint
- All markers same size (90mm recommended)
- Form a rectangle (can be any dimensions)
- All markers visible from camera viewpoint

### 5-Marker Mode (Window + Flue)
```
    Marker 1 ●───────────● Marker 2
             │           │
             │  Window   │  
             │   Area    │        ● Marker 5 (Flue)
    Marker 3 ●───────────● Marker 4
```

**Best Practices:**
- Markers 1-4 at window corners
- Marker 5 at flue terminal location
- Useful for outdoor installations
- Consider weatherproofing for outdoor use

---

## Lighting Conditions

### Optimal Lighting
- ☀️ **Bright, indirect light**: Best for detection
- 💡 **Indoor lighting**: Works well
- 🌥️ **Overcast outdoors**: Good, even lighting

### Challenging Conditions
- ⚠️ **Direct sunlight**: May cause glare or shadows
- 🌙 **Low light**: May reduce accuracy
- 💡 **Backlit**: Camera may struggle with exposure

### Tips for Poor Lighting
1. Use flashlight to improve lighting
2. Try different times of day
3. Use larger markers (better in low light)
4. Move closer to marker
5. Adjust camera exposure if possible

---

## Troubleshooting

### "No markers detected"
**Possible causes:**
1. Marker too small for viewing distance
2. Poor lighting conditions
3. Marker damaged or dirty
4. Incorrect marker type (not ArUco DICT_4X4_50)
5. Camera out of focus

**Solutions:**
- Move closer or use larger marker
- Improve lighting
- Print new marker
- Verify marker type
- Tap screen to focus (mobile)

### "Tracking unstable / jumpy"
**Possible causes:**
1. Camera shake
2. Marker too small
3. Viewing at steep angle
4. Poor lighting

**Solutions:**
- Hold device steady or use tripod
- Use larger marker (190mm recommended)
- View marker more straight-on
- Improve lighting conditions

### "Partial detection (X/4 markers)"
**Possible causes:**
1. Some markers out of frame
2. Markers too far apart
3. Occlusion (something blocking markers)

**Solutions:**
- Step back to fit all markers in frame
- Check all markers are visible
- Remove obstructions
- Verify all markers printed correctly

---

## Detection Mode Comparison

| Mode | Markers Needed | Use Case | Accuracy | Setup Time |
|------|---------------|----------|----------|------------|
| **Single** | 1 | Quick checks, portable use | Good | Fast ⚡ |
| **4-Marker** | 4 | Boiler installations | Very Good | Medium 🕐 |
| **5-Marker** | 5 | Window + flue installations | Excellent | Slower 🕐🕐 |

**Recommendation:** 
- Start with **single marker** for learning
- Use **4-marker** for production installations
- Use **5-marker** for complex outdoor setups

---

## Maintenance & Storage

### Caring for Markers
- Store flat in protective sleeve
- Avoid folding or creasing
- Keep clean and dry
- Laminate for outdoor use
- Create backups (print extras)

### Marker Lifespan
- **Indoor use**: 6-12 months (with care)
- **Outdoor use**: 1-3 months (weatherproofing recommended)
- **Heavy use**: Replace when detection degrades

---

## Advanced Tips

### Multi-Marker Precision
For maximum accuracy with 4-marker or 5-marker modes:
1. Use consistent marker size (all 90mm)
2. Measure black area precisely
3. Position markers in precise rectangle
4. Verify with measuring tape
5. Take multiple measurements

### Distance Optimization
```
Marker Size → Detection Distance
45mm → 1m max (close-up only)
90mm → 2m optimal
148mm → 3m optimal
190mm → 4-5m optimal (best for stepping back)
```

### Angle Tolerance
- **Best**: 0-30° from perpendicular
- **Good**: 30-45° angle
- **Fair**: 45-60° angle
- **Poor**: > 60° angle (may fail)

**Tip:** ArUco detection degrades at steep angles. AprilTag (coming soon) performs better at angles!

---

## FAQ

**Q: Can I use QR codes instead?**
A: QR codes work but ArUco markers are optimized for pose estimation. QR codes lack the corner detection features needed for accurate 3D positioning.

**Q: Do I need high-quality printing?**
A: Standard office printers work fine. High contrast (black vs white) is more important than print resolution.

**Q: Can I use colored markers?**
A: Not recommended. Black on white provides the best contrast for detection. Colored markers may reduce accuracy.

**Q: How do I know if my marker size is correct?**
A: The app will show tracking stability. If the AR overlay is jumpy or unstable, your marker may be too small for the viewing distance.

**Q: Can I reuse markers for different projects?**
A: Yes! Markers are universal. The same marker can be used for any appliance type or size configuration.

**Q: What's the difference between ArUco and AprilTag?**
A: AprilTag offers better detection at angles and distances, with fewer false positives. See [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) for details on upcoming AprilTag support.

---

## Resources

### Marker Generators
- [ArUco Generator](https://chev.me/arucogen/) - Online, easy to use
- [AprilTag Generator](https://github.com/AprilRobotics/apriltag-generation) - Coming soon

### Learning Resources
- [OpenCV ArUco Documentation](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html)
- [ArUco Marker Patterns](https://docs.opencv.org/4.x/d9/d6a/group__aruco.html)

### Support
- Open an issue on GitHub for help
- Share your marker setup photos for troubleshooting

---

**Last Updated:** 2025-12-13  
**App Version:** 2.0+
