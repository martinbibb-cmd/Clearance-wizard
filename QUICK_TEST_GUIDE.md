# Quick Test Guide - AR Stability Fix

## 🚀 Quick Start (5 Minutes)

### What Was Fixed?
1. ✅ **Scale Issue**: AR objects appearing oversized
2. ✅ **Erratic Movement**: Objects jumping or moving rapidly
3. ✅ **Sluggish Tracking**: Delayed response to marker movement

### Quick Validation Test

**You'll Need:**
- Printed AprilTag marker (any size, but measure it accurately)
- Stable surface (table or floor)

**Steps:**
1. Open the app and start AR session
2. Enter your marker size EXACTLY (measure the black square only)
3. Enable "🎯 Debug Plane" in settings
4. Place marker on table, point camera at it

**Success Criteria:**
- ✅ Green debug plane matches marker size (should be same size)
- ✅ Objects don't jump around when marker is still
- ✅ Tracking responds quickly when you move marker

**If Something's Wrong:**
- Debug plane much bigger than marker? → Report scale issue
- Objects jump/shake when still? → Report stability issue
- Slow response to movement? → Report responsiveness issue

## 📊 Automated Tests (2 Minutes)

### Run Tests
```bash
# Python tests (needs: pip install numpy opencv-python)
cd python-dev
python3 test_ar_stability.py

# Browser tests
open ../test_ar_alignment.html
```

**Expected**: All tests should pass (100%)

## 🔍 What to Check

### 1. Size Check (Most Important)
Place marker on table, enable debug plane:
- Green plane should match marker size ✅
- Cube should look proportional ✅
- Not giant-sized ❌

### 2. Stability Check
Keep marker and camera still for 10 seconds:
- Objects should barely move (<5mm) ✅
- No sudden jumps ✅
- Smooth, minimal drift ✅

### 3. Response Check
Move marker slowly left/right:
- Objects follow smoothly ✅
- No lag >0.3 seconds ✅
- Feels "connected" ✅

## 🐛 Common Issues

### "Debug plane is huge!"
→ This is the main bug we fixed. If you see this, the fix didn't work.
→ Check browser console (F12) for errors

### "Objects are shaking"
→ Check lighting (needs good, even lighting)
→ Check marker print quality (should be crisp and flat)
→ Try cleaning camera lens

### "Tracking is slow"
→ Should be fixed by new smoothing factors
→ If still slow, check device performance

## 📝 Report Issues

If problems occur:

1. **Open browser console** (Press F12, go to Console tab)
2. **Look for warnings** like:
   - "Position jump too large"
   - "Invalid pose values detected"
3. **Copy the warning messages**
4. **Report with**:
   - Device/browser info
   - Marker size used
   - Console warnings
   - What you were doing

## 📚 Full Documentation

- **Detailed Testing**: AR_STABILITY_TESTING_GUIDE.md (7 scenarios)
- **Technical Details**: AR_ALIGNMENT_FIX_SUMMARY.md
- **Visual Guide**: EXPECTED_BEHAVIOR.md

## ✅ Quick Checklist

Before reporting as "working":
- [ ] Debug plane matches marker size
- [ ] No jumping when marker is still
- [ ] Tracking responds quickly to movement
- [ ] Works with your marker size
- [ ] Automated tests pass

**Estimated Time**: 5-10 minutes for quick validation

---

**Need Help?** Check full guides or report issue with console logs
