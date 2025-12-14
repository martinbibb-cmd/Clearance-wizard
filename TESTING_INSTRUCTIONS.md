# Quick Testing Instructions

## ⚡ Quick Start

1. **Open the app** in a mobile browser (Safari/Chrome)
2. **Go to Advanced Settings** (expand ⚙️)
3. **Enable "🎯 Debug Plane (test alignment)"**
4. **Start Camera**
5. **Point at a printed AprilTag or ArUco marker**

## 🎯 What You Should See

### With Debug Plane Enabled

You should see these test objects overlaid on the marker:

- 🟢 **Green semi-transparent plane** - This should lie perfectly flat on your marker
- 🟡 **Yellow sphere** - Marks the exact center of the marker
- 🟣 **Magenta cube** - Should sit on the plane, not penetrate it
- **Colored axis lines:**
  - 🔴 Red (X axis) - Points right
  - 🟢 Green (Y axis) - Points up/away from marker surface
  - 🔵 Blue (Z axis) - Points toward camera

## ✅ Success Tests

### Test 1: Flat Marker (EASIEST)
1. Place marker flat on a table
2. The green plane should lie flat on the marker
3. The cube should sit upright on the plane
4. ✅ **PASS**: Plane is flat, cube doesn't penetrate

### Test 2: Tilted Marker (IMPORTANT)
1. Prop marker at a 45° angle (use a book)
2. The green plane should tilt with the marker
3. Everything should stay "glued" to the marker surface
4. ✅ **PASS**: Plane follows the tilt perfectly

### Test 3: Vertical Marker (CRITICAL)
1. Tape marker to a wall
2. The green plane should be vertical
3. Objects should "stick" to the wall
4. ✅ **PASS**: No "falling down" effect

### Test 4: Rotation
1. Slowly rotate the marker
2. Objects should smoothly follow the rotation
3. No sudden jumps or jitter
4. ✅ **PASS**: Smooth tracking throughout

## ❌ What "Broken" Looks Like

### Before the fix:
- Green plane stands **upright** when marker is **flat** ❌
- Cube appears to be "standing on edge" ❌
- Objects don't follow marker orientation ❌
- Everything looks disconnected from the marker ❌

### After the fix (what you should see):
- Green plane lies **flat** when marker is **flat** ✅
- Cube sits properly on the plane ✅
- Objects perfectly follow marker orientation ✅
- Everything appears "glued" to the marker ✅

## 📸 Taking Screenshots

If something doesn't work:
1. Take a screenshot showing the issue
2. Note which test failed (flat, tilted, vertical, rotation)
3. Include in your feedback:
   - Device (iPhone 13, Samsung Galaxy S21, etc.)
   - Browser (Safari, Chrome, Firefox)
   - Marker type (AprilTag or ArUco)

## 🔧 Troubleshooting

### "I don't see the debug objects"
- Make sure you checked "🎯 Debug Plane" in Advanced Settings
- Try restarting the camera
- Check browser console (F12) for errors

### "Objects are jittery"
- Improve lighting
- Hold camera steadier
- Make sure marker is in focus
- This is normal behavior, not a bug

### "Wrong size/scale"
- Measure the BLACK SQUARE area only (not white border)
- Enter correct size in settings
- Use mm (millimeters), not cm or inches

### "Plane is rotated 90°"
- Report this with device/browser details
- May need additional rotation adjustment
- Include screenshot

## 📚 More Information

- **EXPECTED_BEHAVIOR.md** - Visual guide with diagrams
- **POSE_FIX_TESTING.md** - Detailed technical guide
- **POSE_ALIGNMENT_FIX_SUMMARY.md** - Implementation details

## 🎉 If All Tests Pass

Congratulations! The fix is working correctly. You should now see properly aligned AR overlays in your app:
- Radiators will stand upright on flat markers
- Clearance zones will extend in the correct directions
- Multi-marker mode will maintain proper alignment
- Everything will track smoothly as you move

Feel free to disable "Debug Plane" and use the app normally!

## 📝 Reporting Results

Please report back with:
- ✅ Which tests passed
- ❌ Which tests failed (with screenshots)
- 📱 Device and browser info
- 🏷️ Marker type used

Thank you for testing! 🙏
