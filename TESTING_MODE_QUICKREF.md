# Testing Mode Quick Reference Card

A one-page reference for developers and testers working with the testing mode feature.

## Activation Methods

```javascript
// Method 1: URL Parameter
http://localhost:8000/?testMode=true

// Method 2: JavaScript Console
App.testingMode = true;
App.toggleTestingMode();

// Method 3: UI Checkbox
// Check "🔬 Testing Mode" in welcome panel or advanced settings
```

## API Methods

```javascript
// Initialize (called automatically on page load)
App.initTestingMode();

// Toggle on/off
App.toggleTestingMode();

// Update device info display
App.updateDeviceInfo();

// Show/hide axes
App.graphics.showCalibrationAxes();
App.graphics.hideCalibrationAxes();

// Check current state
console.log('Testing mode:', App.testingMode);
console.log('Position:', App.graphics.root.position);
```

## Visual Elements

### Axis Colors (Standard Convention)
- **X-Axis**: 🔴 Red (horizontal right)
- **Y-Axis**: 🟢 Green (vertical up)
- **Z-Axis**: 🔵 Blue (depth forward)
- **Origin**: 🟡 Yellow sphere at (0,0,0)

### Measurements
- **Axis Length**: 1000mm (1 meter)
- **Tick Spacing**: 100mm (10cm)
- **Label Interval**: 200mm (20cm)
- **Tick Height**: 20mm

### Device Overlay
- **Position**: Top-left corner
- **Background**: Black with 80% opacity
- **Text**: White monospace
- **Update Rate**: Every 30 frames (~0.5s)

## Configuration Constants

```javascript
// In GraphicsEngine.showCalibrationAxes()
const axisLength = 1000;      // Total axis length (mm)
const tickSpacing = 100;      // Distance between ticks (mm)
const labelInterval = 2;      // Label every N ticks
const tickHeight = 20;        // Height of tick marks (mm)

// Arrow dimensions
const arrowSize = 40;         // Cone size at axis end (mm)

// Origin marker
const originRadius = 25;      // Sphere radius (mm)
```

## LocalStorage

```javascript
// Key name
'testingMode'

// Values
'true'  // Enabled
'false' // Disabled

// Access
localStorage.getItem('testingMode')
localStorage.setItem('testingMode', 'true')
```

## DOM Elements

```html
<!-- Checkboxes -->
#testing-mode-toggle          <!-- Welcome panel -->
#testing-mode-toggle-menu     <!-- Advanced settings -->

<!-- Overlays -->
#device-info-overlay          <!-- Container -->
#device-info-content          <!-- Dynamic content -->
```

## Coordinate System

```
       Y+ (Green)
        ↑
        |
        |
        O----→ X+ (Red)
       /
      /
     ↙ Z+ (Blue)
```

**Right-handed system:**
- X: Right from marker
- Y: Up from marker  
- Z: Forward from camera/marker

## Common Debugging Commands

```javascript
// Toggle testing mode
App.toggleTestingMode();

// Force device info update
App.updateDeviceInfo();

// Check if axes are visible
console.log('Axes visible:', App.graphics.calibrationAxes?.visible);

// Get current position
const pos = App.graphics.root.position;
console.log(`Position: (${pos.x}, ${pos.y}, ${pos.z})`);

// Check marker size
console.log('Marker size:', App.markerSize, 'mm');

// Check detection mode
console.log('Detection mode:', App.detectionMode);

// Check marker type
console.log('Marker type:', App.markerType);
```

## Browser Console Snippets

```javascript
// Enable with detailed logging
App.testingMode = true;
App.toggleTestingMode();
console.log('Testing mode enabled');
console.log('Graphics:', App.graphics);
console.log('Vision:', App.vision);

// Capture current state
const state = {
    testingMode: App.testingMode,
    markerSize: App.markerSize,
    markerType: App.markerType,
    detectionMode: App.detectionMode,
    position: App.graphics?.root?.position,
    locked: App.locked
};
console.table(state);

// Monitor position updates
let lastPos = null;
setInterval(() => {
    if (App.graphics?.root) {
        const pos = App.graphics.root.position;
        if (!lastPos || pos.x !== lastPos.x || pos.y !== lastPos.y || pos.z !== lastPos.z) {
            console.log(`Position: (${pos.x.toFixed(1)}, ${pos.y.toFixed(1)}, ${pos.z.toFixed(1)})mm`);
            lastPos = {x: pos.x, y: pos.y, z: pos.z};
        }
    }
}, 1000);
```

## Quick Tests

### Verify Installation
```javascript
// Check if methods exist
console.log('initTestingMode:', typeof App.initTestingMode);
console.log('toggleTestingMode:', typeof App.toggleTestingMode);
console.log('showCalibrationAxes:', typeof App.graphics?.showCalibrationAxes);
```

### Visual Check
1. Enable testing mode
2. Detect marker
3. Verify:
   - ✅ Three colored axes visible
   - ✅ Yellow origin sphere
   - ✅ Tick marks every 10cm
   - ✅ Labels every 20cm
   - ✅ Device info overlay top-left

### Accuracy Check
1. Print 190mm marker
2. Enable testing mode
3. Detect marker
4. Place ruler from origin:
   - 10cm should align with first large tick
   - 20cm should align with "2cm" label
   - 50cm should align with "5cm" label

## Troubleshooting Quick Fixes

### Axes Not Showing
```javascript
// Force show
if (App.graphics) {
    App.graphics.showCalibrationAxes();
    console.log('Axes forced visible');
}
```

### Device Info Not Updating
```javascript
// Force update
App.updateDeviceInfo();
console.log('Device info updated');
```

### Reset Testing Mode
```javascript
// Clear localStorage and disable
localStorage.removeItem('testingMode');
App.testingMode = false;
App.toggleTestingMode();
console.log('Testing mode reset');
```

### Check THREE.js Scene
```javascript
// Inspect scene hierarchy
console.log('Scene children:', App.graphics.scene.children);
console.log('Root children:', App.graphics.root.children);
console.log('Axes object:', App.graphics.calibrationAxes);
```

## Performance Monitoring

```javascript
// Simple FPS counter
let lastTime = performance.now();
let frames = 0;
const checkFPS = () => {
    frames++;
    const now = performance.now();
    if (now >= lastTime + 1000) {
        console.log('FPS:', Math.round(frames * 1000 / (now - lastTime)));
        frames = 0;
        lastTime = now;
    }
    requestAnimationFrame(checkFPS);
};
checkFPS();

// Memory usage (Chrome only)
if (performance.memory) {
    setInterval(() => {
        const mem = performance.memory;
        console.log('Memory:', 
            (mem.usedJSHeapSize / 1048576).toFixed(2), 'MB used,',
            (mem.totalJSHeapSize / 1048576).toFixed(2), 'MB total'
        );
    }, 5000);
}
```

## Files Modified

- `index.html` - Main implementation
- `README.md` - Feature documentation
- `TESTING_MODE_GUIDE.md` - Comprehensive guide
- `TESTING_MODE_VERIFICATION.md` - Test checklist
- `TESTING_MODE_QUICKREF.md` - This file

## Related Documentation

- [TESTING_MODE_GUIDE.md](TESTING_MODE_GUIDE.md) - Complete usage guide
- [TESTING_MODE_VERIFICATION.md](TESTING_MODE_VERIFICATION.md) - Test checklist
- [README.md](README.md) - Main application docs
- [MARKER_GUIDE.md](MARKER_GUIDE.md) - Marker setup guide

## Support

For issues or questions:
1. Check console for errors (F12)
2. Verify OpenCV.js is loaded
3. Ensure marker is detected (status pill)
4. Check browser compatibility
5. Report issues on GitHub with:
   - Device info from overlay
   - Console errors
   - Screenshots
   - Steps to reproduce
