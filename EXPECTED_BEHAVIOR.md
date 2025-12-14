# Expected Behavior After Pose Alignment Fix

## Quick Visual Guide

### Before the Fix ❌
- 3D objects appear "standing up" when marker is flat
- Clearance zones extend in wrong direction
- Objects don't follow marker orientation when tilted
- AR content appears disconnected from marker

### After the Fix ✅
- 3D objects lie flat on flat markers
- Clearance zones extend perpendicular to marker surface
- Objects perfectly follow marker orientation (tilt, rotation)
- AR content appears "glued" to marker surface

## Testing Scenarios

### 1. Flat Marker on Table 📐

**Setup:**
- Print marker, place on table
- Enable "🎯 Debug Plane" in settings
- Point camera at marker

**What You Should See:**
```
Camera View (from above):
     [You]
       ↓ (looking down)
    
   ┌─────────┐  ← Green plane lies flat
   │  Marker │
   │ [●] Cube│  ← Cube sits on plane
   └─────────┘
   
Axis orientation:
- Red (X): Points right
- Green (Y): Points up (away from table)  
- Blue (Z): Points toward you (camera)
```

**If Wrong:**
- Plane is vertical instead of flat → coordinate transform issue
- Cube penetrates plane → Z-offset problem
- Axes pointing wrong way → rotation matrix issue

### 2. Tilted Marker (45°) 📐↗️

**Setup:**
- Prop marker at 45° angle with book/stand
- Enable debug plane
- Point camera at marker

**What You Should See:**
```
Side View:
       [You]
         ↓
      
      /Green plane/ ← Plane tilted at 45°
     /            /
    /   Marker   /
   /   [●] Cube / ← Cube stays on tilted plane
  /____________/
  
The plane should:
✓ Follow marker tilt exactly
✓ Not rotate independently
✓ Maintain "glued to surface" appearance
```

**If Wrong:**
- Plane doesn't tilt with marker → transformation not being applied
- Plane tilts but wrong angle → rotation matrix issues
- Objects slide on plane → smoothing/tracking issue

### 3. Vertical Marker on Wall 📐↑

**Setup:**
- Tape marker to wall vertically
- Enable debug plane
- Point camera at marker

**What You Should See:**
```
Front View (looking at wall):
      Wall
   ┌────────┐
   │ Marker │
   │  [●]   │ ← Sphere at center
   │   ▣    │ ← Cube on vertical plane
   │┃┃┃┃┃┃┃┃│ ← Green plane (vertical)
   └────────┘
   
The plane should:
✓ Be perfectly vertical (parallel to wall)
✓ Not appear to "fall down"
✓ Stay aligned when you move camera
```

**If Wrong:**
- Plane appears horizontal → major coordinate issue
- Plane wobbles/unstable → tracking/smoothing problem
- Objects "fall" away from wall → gravity perception but should stay fixed

### 4. Rotating Marker 🔄

**Setup:**
- Hold marker and slowly rotate it
- Keep debug plane enabled
- Observe transitions

**What You Should See:**
- Smooth rotation following marker
- No sudden jumps or flips
- Consistent alignment throughout
- Interpolation appears natural

**Typical Rotation Path:**
```
Flat → Tilted → Vertical → Upside-down
  ═      ╱         ║           ═
        
Each transition should be smooth and continuous.
```

## Debug Plane Components

When "🎯 Debug Plane" is enabled, you see:

1. **Green Plane** (200mm square)
   - Semi-transparent (50% opacity)
   - Should lie perfectly flat on marker surface
   - Primary indicator of alignment

2. **Yellow Sphere** (20mm radius)
   - Marks exact center of marker (origin point)
   - Should be at intersection of axis lines

3. **Magenta Cube** (100mm)
   - Semi-transparent (70% opacity)
   - Bottom face should sit on green plane
   - Should not penetrate plane or float above it

4. **Colored Axis Lines** (300mm each)
   - **Red (X)**: Points right relative to marker
   - **Green (Y)**: Points up/away from marker surface
   - **Blue (Z)**: Points toward camera/forward from marker
   - Small spheres mark 100mm intervals

## Real Appliance Visualization

After verifying with debug plane, test with actual appliance:

### Radiator Example
```
With marker flat on table:
    ┌─────────┐
    │         │ ← Radiator stands upright
    │ Radiator│
    │         │
    └─────────┘
   ┌───────────┐ ← Marker on table
   │   Marker  │
   └───────────┘

Clearance zones should extend:
- Top: Upward from radiator
- Sides: Outward horizontally
- Front: Away from marker toward camera
```

### Flue Pipe Example
```
With marker vertical on wall:
    
    Wall │ Flue pipe │ ← Pipe extends from wall
         │     ═     │
         │  Marker   │
         │           │

Clearance rings should extend:
- Perpendicular to wall
- Around pipe circumference
```

## Coordinate System Verification

When testing, verify each axis points correctly:

### X Axis (Red Line)
- **Flat marker**: Points right
- **Vertical marker**: Points right
- **Should NOT**: Point up, down, or backward

### Y Axis (Green Line)  
- **Flat marker**: Points up (away from surface)
- **Vertical marker**: Points up
- **Should NOT**: Point down or sideways

### Z Axis (Blue Line)
- **Flat marker**: Points toward camera
- **Vertical marker**: Points away from wall
- **Should NOT**: Point at surface or away from camera

## Common Misalignments (What NOT to See)

### ❌ Wrong: "Standing Up" Plane
```
Should be:        Not this:
    ═══              ║║║
  (flat)          (vertical)
```

### ❌ Wrong: Penetrating Objects
```
Should be:        Not this:
   ▣                 ▣
   ═══            ═══▣═══
 (on top)       (penetrating)
```

### ❌ Wrong: Rotated Axes
```
Should be:        Not this:
   Y↑               Y→
   |                |
   └→X             ↑Z
  Z↙              X↓
```

## Performance Indicators

Even with debug plane enabled, you should see:
- **60 FPS** on modern devices
- **30 FPS** on older devices
- Smooth tracking with no stuttering
- Quick detection (< 100ms)

If performance drops:
- Disable debug plane (use Testing Mode axes instead)
- Check device specs
- Reduce browser tab count

## Success Checklist

✅ Debug plane lies flat on flat marker  
✅ Debug plane follows tilt correctly  
✅ Debug plane stays vertical on wall  
✅ Smooth transitions during rotation  
✅ Cube sits on plane, no penetration  
✅ Axes point in correct directions  
✅ Real appliances align properly  
✅ Clearance zones extend correctly  
✅ No jitter or instability  
✅ Works with AprilTag and ArUco  
✅ Multi-marker mode maintains alignment  
✅ No performance degradation  

## Troubleshooting

### Issue: Plane is rotated 90° off
**Possible cause:** Additional rotation needed  
**Fix:** May need to add `anchor.rotation.x += Math.PI/2` in some cases  
**Next step:** Report to developer with device details

### Issue: Objects jitter/shake
**Possible cause:** Poor lighting, out of focus, or tracking issues  
**Fix:** 
- Improve lighting
- Hold camera steadier
- Ensure marker is in focus
- Reduce smoothing factors if needed

### Issue: Wrong scale/size
**Possible cause:** Incorrect marker size measurement  
**Fix:** 
- Measure BLACK SQUARE only (not white border)
- Use ruler or calipers
- Double-check marker size in settings

### Issue: Plane alignment changes when moving camera
**Possible cause:** Normal behavior or camera intrinsics issue  
**Note:** Some variation is expected without full camera calibration  
**Improvement:** Future enhancement with calibration wizard

## Next Steps After Verification

1. **If tests pass**: Mark feature as complete, merge PR
2. **If tests fail**: Document specific failures with screenshots
3. **If partial success**: Note which scenarios work/don't work
4. **Report findings**: Include device, browser, marker type details

## Contact

If you encounter issues not covered here:
1. Check browser console for errors (F12)
2. Enable Testing Mode for position data
3. Take screenshot showing the issue
4. Note device/browser/marker configuration
5. Report via GitHub issue with details
