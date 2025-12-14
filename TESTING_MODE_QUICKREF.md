# Testing Mode Quick Reference

## Quick Start

### Enable Testing Mode

**Method 1 - URL Parameter:**
```
http://localhost:8000/?testMode=true
```

**Method 2 - Welcome Panel:**
```
☑️ Enable Testing Mode (show calibration axes)
```

**Method 3 - Advanced Settings:**
```
⚙️ Advanced Settings → ☑️ Testing Mode
```

## Visual Elements

### Calibration Axes
| Axis | Color | Direction | Length |
|------|-------|-----------|--------|
| X    | Red   | Right     | 1000mm |
| Y    | Green | Up        | 1000mm |
| Z    | Blue  | Forward   | 1000mm |

### Markers & Labels
- **Tick Marks**: Every 100mm (10 ticks per axis)
- **Labels**: Every 200mm (20cm, 40cm, 60cm, 80cm, 100cm)
- **Origin**: Yellow sphere at (0,0,0)

## Device Overlay

Located in top-right corner:

```
Position:     X:123.4 Y:56.7 Z:890.1mm
Device:       iPhone 13 Pro
Screen:       1170x2532
Pixel Ratio:  3.00
Marker Size:  190mm
Marker Type:  AprilTag
Detection:    Single
```

**Update Rate**: Every 30 frames (~1 second)

## Coordinate System

```
Right-Handed System:
      Y (Green, Up)
      |
      |_____ X (Red, Right)
     /
    Z (Blue, Forward)

Origin: Marker center (0,0,0)
```

## API Reference

### localStorage Key
```javascript
localStorage.getItem('testingMode')  // 'true' or 'false'
localStorage.setItem('testingMode', 'true')
```

### URL Parameter
```javascript
const urlParams = new URLSearchParams(window.location.search);
const testMode = urlParams.get('testMode') === 'true';
```

### App Methods

#### Toggle Testing Mode
```javascript
App.toggleTestingMode(event)
// event.target.checked = true/false
```

#### Initialize Testing Mode
```javascript
App.initTestingMode()
// Called automatically on page load
// Checks URL params and localStorage
```

#### Update Device Info
```javascript
App.updateDeviceInfo(pose)
// pose: { x, y, z, ... } or null
// Throttled to every 30 frames
```

### GraphicsEngine Methods

#### Show Calibration Axes
```javascript
graphicsEngine.showCalibrationAxes()
```

**Parameters**: None

**Returns**: void

**Creates**:
- 3 colored axes (X=red, Y=green, Z=blue)
- Tick marks every 100mm
- Labels every 200mm
- Yellow origin sphere
- Axis direction cones

#### Hide Calibration Axes
```javascript
graphicsEngine.hideCalibrationAxes()
```

**Parameters**: None

**Returns**: void

**Effect**: Removes all calibration geometry from scene

## Configuration Constants

### GraphicsEngine
```javascript
const axisLength = 1000;      // 1m per axis (mm)
const tickSpacing = 100;      // 100mm intervals
const labelInterval = 2;      // Label every 200mm
const MM_TO_CM = 10;          // Unit conversion
```

### App
```javascript
frameCounter: 0               // Frame counter for throttling
testingMode: false            // Testing mode state
```

## Console Commands

### Check Testing Mode Status
```javascript
console.log('Testing Mode:', App.testingMode);
```

### Manually Toggle Testing Mode
```javascript
App.testingMode = true;
if (App.graphics) {
    App.graphics.showCalibrationAxes();
    document.getElementById('device-info-overlay').classList.remove('hidden');
}
localStorage.setItem('testingMode', 'true');
```

### Clear Testing Mode State
```javascript
localStorage.removeItem('testingMode');
location.reload();
```

### Get Current Position
```javascript
console.log('Position:', App.graphics.root.position);
```

### Inspect Calibration Axes
```javascript
console.log('Calibration Axes:', App.graphics.calibrationAxes);
console.log('Children:', App.graphics.calibrationAxes.children.length);
```

## Troubleshooting

### Issue: Axes Not Showing
```javascript
// Check if testing mode is enabled
console.log(App.testingMode);

// Check if graphics engine exists
console.log(App.graphics);

// Manually show axes
App.graphics.showCalibrationAxes();
```

### Issue: Device Overlay Not Updating
```javascript
// Check frame counter
console.log(App.frameCounter);

// Check if overlay is visible
console.log(document.getElementById('device-info-overlay').classList);

// Force update
App.frameCounter = 30;
App.updateDeviceInfo({ x: 0, y: 0, z: -500 });
```

### Issue: State Not Persisting
```javascript
// Check localStorage
console.log(localStorage.getItem('testingMode'));

// Set manually
localStorage.setItem('testingMode', 'true');

// Check URL param
console.log(new URLSearchParams(window.location.search).get('testMode'));
```

## Performance Tips

- **FPS Impact**: <5% (static geometry, no per-frame calculations)
- **Memory**: ~2MB for calibration geometry
- **Throttling**: Device info updates every 30 frames
- **Optimization**: Use `requestAnimationFrame` for smooth rendering

## Color Reference (Hex)

| Element | Color | Hex |
|---------|-------|-----|
| X-axis | Red | #FF0000 |
| Y-axis | Green | #00FF00 |
| Z-axis | Blue | #0000FF |
| Origin | Yellow | #FFFF00 |
| Overlay Background | Black (80% opacity) | rgba(0,0,0,0.8) |
| Overlay Text | White | #FFFFFF |
| Info Labels | Gray | #AAAAAA |
| Info Values | Green | #00FF00 |

## Geometry Details

### Axis Lines
- **Type**: THREE.Line
- **Material**: THREE.LineBasicMaterial
- **Width**: 2px

### Tick Marks
- **Type**: THREE.Mesh (PlaneGeometry)
- **Size**: 20x20 for labeled ticks, 10x10 for others
- **Material**: THREE.MeshBasicMaterial (semi-transparent)
- **Opacity**: 0.6

### Labels
- **Type**: THREE.Sprite
- **Texture**: Canvas (128x64px)
- **Font**: Bold 32px Arial
- **Scale**: 60x30x1

### Origin Sphere
- **Type**: THREE.Mesh (SphereGeometry)
- **Radius**: 15mm
- **Segments**: 16x16
- **Material**: THREE.MeshBasicMaterial

### Direction Cones
- **Type**: THREE.Mesh (ConeGeometry)
- **Radius**: 10mm
- **Height**: 30mm
- **Segments**: 8

## Browser Compatibility

| Browser | Desktop | Mobile | Notes |
|---------|---------|--------|-------|
| Chrome | ✅ | ✅ | Full support |
| Safari | ✅ | ✅ | Full support |
| Firefox | ✅ | ✅ | Full support |
| Edge | ✅ | ✅ | Full support |
| Opera | ✅ | ✅ | Full support |

## Related Files

- `index.html` - Main application file with Testing Mode implementation
- `TESTING_MODE_GUIDE.md` - Detailed user guide
- `TESTING_MODE_VERIFICATION.md` - QA testing checklist
- `TESTING_MODE_IMPLEMENTATION_SUMMARY.md` - Technical architecture
- `README.md` - Main project documentation

## Version History

- **v1.0.0** - Initial Testing Mode implementation
  - 3D calibration axes with tick marks and labels
  - Device info overlay with real-time updates
  - URL parameter, localStorage, and UI toggle support
  - Cross-device calibration support
