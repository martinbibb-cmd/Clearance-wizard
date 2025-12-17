# Testing Guide - Clearance Wizard iOS

Comprehensive testing procedures for validating AR measurement accuracy and app functionality.

## Prerequisites

- Physical iOS device (iPhone 6S or later)
- Tape measure (3m or longer)
- Well-lit indoor space
- Flat surfaces (floor, table, wall)
- Printed test pattern (optional)

## Test Environment Setup

### Ideal Testing Conditions
- **Lighting:** Bright, even lighting (avoid direct sunlight)
- **Surface:** Textured (carpet, wood floor, patterned table)
- **Space:** 3m x 3m minimum clear area
- **Temperature:** Normal room temperature

### Poor Testing Conditions (for validation)
- Dark or very bright lighting
- Reflective surfaces (glass, polished metal)
- Plain white walls
- Moving objects in frame

## Test Categories

### 1. Installation & Setup Tests

#### T1.1: First Install
**Steps:**
1. Install app via Xcode
2. Launch app
3. Grant camera permission
4. Grant photo library permission

**Expected:**
- App launches successfully
- Permissions requested clearly
- Home screen loads

**Pass Criteria:**
- ✅ No crashes
- ✅ Permissions granted
- ✅ UI responsive

---

#### T1.2: ARKit Support Check
**Steps:**
1. Launch app on various devices
2. Navigate to AR screen

**Test Devices:**
- iPhone 6S (minimum supported)
- iPhone 12/13/14 (common)
- iPhone 15 Pro (latest with LiDAR)
- iPad Pro (2017+)

**Expected:**
- ARKit starts successfully
- Appropriate error on unsupported device

**Pass Criteria:**
- ✅ Supported devices work
- ✅ Clear error message on unsupported

---

### 2. AR Session Tests

#### T2.1: Session Initialization
**Steps:**
1. Navigate to AR Measure screen
2. Observe tracking state indicator

**Expected:**
- Tracking state: "Initializing" → "Limited" → "Normal"
- Time to "Normal": < 5 seconds

**Pass Criteria:**
- ✅ Achieves "Normal" tracking
- ✅ No crashes or freezes

---

#### T2.2: Tracking Recovery
**Steps:**
1. Achieve "Normal" tracking
2. Cover camera with hand (5 seconds)
3. Uncover camera
4. Move device slowly

**Expected:**
- Tracking state: "Normal" → "Limited" → "Normal"
- Recovery time: < 3 seconds

**Pass Criteria:**
- ✅ Tracking recovers automatically
- ✅ UI shows appropriate guidance

---

#### T2.3: Plane Detection
**Steps:**
1. Point camera at floor
2. Move device side-to-side slowly
3. Observe plane detection

**Expected:**
- Horizontal plane detected within 3 seconds
- Plane remains stable

**Pass Criteria:**
- ✅ Plane detected
- ✅ High confidence (visualized by ARKit)

---

### 3. Anchor Placement Tests

#### T3.1: First Anchor Placement
**Steps:**
1. Achieve "Normal" tracking
2. Point at floor
3. Tap screen when plane detected

**Expected:**
- Anchor placed at tap location
- UI confirms: "Anchor Set"
- Anchor visible and stable

**Pass Criteria:**
- ✅ Anchor placed successfully
- ✅ Anchor doesn't drift
- ✅ UI updates correctly

---

#### T3.2: Anchor Stability
**Steps:**
1. Place anchor
2. Move device around anchor (360°)
3. Move 1m away, then return
4. Observe anchor position

**Expected:**
- Anchor remains at same world position
- No visible drift or jitter
- Tracking state remains "Normal"

**Pass Criteria:**
- ✅ Anchor drift < 5mm
- ✅ No flicker or jump
- ✅ Stable through movement

---

#### T3.3: Multiple Session Test
**Steps:**
1. Place anchor
2. Note anchor position (mark with tape)
3. Stop session (back button)
4. Start new session
5. Place new anchor at same location

**Expected:**
- Cannot compare across sessions (no persistence yet)
- Each session independent

**Pass Criteria:**
- ✅ Clean session restart
- ✅ New anchor independent

---

### 4. Measurement Accuracy Tests

#### T4.1: Short Distance (0.5m)
**Setup:**
- Place two marks 50cm apart (tape measure)
- Measure with app

**Steps:**
1. Place anchor near first mark
2. Tap first mark
3. Tap second mark
4. Record measurement

**Expected:**
- App measurement: 495-505mm
- Confidence: > 90%

**Pass Criteria:**
- ✅ Accuracy: ±1cm (±2%)
- ✅ High confidence

**Repeat:** 5 times, calculate average and std dev

---

#### T4.2: Medium Distance (1.5m)
**Setup:**
- Marks 150cm apart

**Steps:**
- Same as T4.1

**Expected:**
- App measurement: 1485-1515mm
- Confidence: > 80%

**Pass Criteria:**
- ✅ Accuracy: ±3cm (±2%)
- ✅ Reasonable confidence

**Repeat:** 5 times

---

#### T4.3: Long Distance (3.0m)
**Setup:**
- Marks 300cm apart

**Steps:**
- Same as T4.1

**Expected:**
- App measurement: 2970-3030mm
- Confidence: > 70%

**Pass Criteria:**
- ✅ Accuracy: ±6cm (±2%)
- ✅ Acceptable confidence

**Repeat:** 5 times

---

#### T4.4: Vertical Measurement
**Setup:**
- Measure wall height or door

**Steps:**
1. Place anchor at floor level
2. Tap floor point
3. Tap ceiling/top point

**Expected:**
- Accurate measurement
- Confidence varies with plane detection

**Pass Criteria:**
- ✅ Reasonable accuracy
- ✅ Consistent across attempts

---

#### T4.5: Diagonal Measurement
**Setup:**
- Measure corner to corner of table

**Steps:**
1. Place anchor
2. Tap corner A
3. Tap corner B (diagonal)

**Expected:**
- Calculates 3D distance correctly
- Matches physical measurement

**Pass Criteria:**
- ✅ Accuracy within ±3%
- ✅ Confidence reported

---

### 5. Measurement Repeatability Tests

#### T5.1: Same Distance, Multiple Measurements
**Setup:**
- Two marks 1m apart

**Steps:**
1. Measure 10 times without moving device
2. Record all measurements

**Expected:**
- Mean: 1000mm ±20mm
- Standard deviation: < 10mm
- All confidence > 80%

**Pass Criteria:**
- ✅ Consistent results
- ✅ Low standard deviation

---

#### T5.2: Same Distance, Different Angles
**Setup:**
- Two marks 1m apart

**Steps:**
1. Measure from straight on
2. Measure from 45° left
3. Measure from 45° right
4. Measure from above

**Expected:**
- All measurements: 1000mm ±30mm
- Confidence may vary

**Pass Criteria:**
- ✅ Angle doesn't affect accuracy significantly
- ✅ Confidence reported appropriately

---

### 6. Confidence Scoring Tests

#### T6.1: Plane vs Feature Points
**Steps:**
1. Measure on detected plane (high confidence)
2. Measure on feature points only (lower confidence)
3. Compare confidence scores

**Expected:**
- Plane: confidence ≈ 1.0 (100%)
- Features: confidence ≈ 0.7 (70%)

**Pass Criteria:**
- ✅ Confidence reflects detection method
- ✅ Scores are reasonable

---

#### T6.2: Distance vs Confidence
**Steps:**
1. Measure at 0.5m, 1m, 2m, 3m, 5m
2. Record confidence for each

**Expected:**
- Confidence decreases with distance
- Still usable at 3m

**Pass Criteria:**
- ✅ Trend is logical
- ✅ Confidence > 60% up to 3m

---

### 7. Photo Capture Tests

#### T7.1: Single Photo Capture
**Steps:**
1. Place anchor
2. Tap 📷 button
3. Check photo saved

**Expected:**
- Photo saved to temp directory
- Path returned
- File exists and is valid JPEG

**Pass Criteria:**
- ✅ Photo captured
- ✅ File accessible
- ✅ Resolution appropriate

---

#### T7.2: Multiple Photo Capture
**Steps:**
1. Capture 10 photos in quick succession
2. Check all saved

**Expected:**
- All photos saved
- Unique filenames (timestamp)
- No crashes or memory issues

**Pass Criteria:**
- ✅ All photos saved
- ✅ No duplicate filenames
- ✅ Stable performance

---

### 8. Pack Management Tests

#### T8.1: Create New Pack
**Steps:**
1. Tap "New Pack"
2. Enter site details
3. Continue to AR

**Expected:**
- Pack created with UUID
- Details stored
- AR session starts

**Pass Criteria:**
- ✅ Pack created
- ✅ Details persisted
- ✅ Smooth transition

---

#### T8.2: Save Measurements to Pack
**Steps:**
1. Create pack
2. Take 5 measurements
3. Save each
4. Return to home

**Expected:**
- Measurements stored in pack
- Pack visible on home screen
- Count shows "5 captures"

**Pass Criteria:**
- ✅ Measurements saved
- ✅ Count accurate
- ✅ Data intact

---

### 9. UI/UX Tests

#### T9.1: Tracking State Feedback
**Steps:**
1. Observe tracking state indicator during various conditions

**Expected:**
- ✓ Green for "Normal"
- ⚠ Yellow for "Limited"
- ✗ Red for "Not Available"
- Updates in real-time

**Pass Criteria:**
- ✅ Clear visual feedback
- ✅ Color coding intuitive
- ✅ Updates smoothly

---

#### T9.2: Measurement Display
**Steps:**
1. Take measurement
2. Observe display

**Expected:**
- Large, readable distance (cm)
- Confidence percentage
- Clear save/discard options

**Pass Criteria:**
- ✅ Easy to read
- ✅ All info visible
- ✅ Actions clear

---

#### T9.3: Error Messages
**Steps:**
1. Trigger various errors:
   - Tap without plane
   - Try to measure before anchor
   - Measure at invalid points

**Expected:**
- Clear, helpful error messages
- Guidance on how to fix
- No crashes

**Pass Criteria:**
- ✅ Errors caught gracefully
- ✅ Messages helpful
- ✅ Recovery possible

---

### 10. Performance Tests

#### T10.1: Frame Rate
**Steps:**
1. Run AR session for 5 minutes
2. Monitor frame rate
3. Perform various operations

**Expected:**
- Frame rate: ~60fps
- No significant drops
- Smooth camera view

**Pass Criteria:**
- ✅ Maintains 50+ fps
- ✅ No stuttering
- ✅ Responsive touch

---

#### T10.2: Memory Usage
**Steps:**
1. Launch app
2. Create 5 packs
3. Take 20 measurements each
4. Capture 10 photos per pack
5. Monitor memory

**Expected:**
- Memory stable
- No memory leaks
- No crashes

**Pass Criteria:**
- ✅ Memory < 200MB
- ✅ No growth over time
- ✅ Stable operation

---

#### T10.3: Battery Impact
**Steps:**
1. Fully charge device
2. Run AR session for 30 minutes
3. Check battery drain

**Expected:**
- Battery drain: ~15-20%
- Device warm but not hot

**Pass Criteria:**
- ✅ Reasonable battery usage
- ✅ No overheating

---

### 11. Edge Case Tests

#### T11.1: Low Light
**Steps:**
1. Test in dim lighting
2. Attempt measurements

**Expected:**
- Tracking may be limited
- Clear feedback to user
- Measurements still possible with lower confidence

**Pass Criteria:**
- ✅ Graceful degradation
- ✅ Clear feedback

---

#### T11.2: Bright Sunlight
**Steps:**
1. Test in bright direct sunlight
2. Attempt measurements

**Expected:**
- Tracking may be affected
- Measurements may be less accurate

**Pass Criteria:**
- ✅ No crashes
- ✅ Warnings shown

---

#### T11.3: Fast Motion
**Steps:**
1. Move device quickly
2. Observe tracking recovery

**Expected:**
- Tracking state: "Excessive Motion"
- Quick recovery when slowed

**Pass Criteria:**
- ✅ Handles gracefully
- ✅ Recovers quickly

---

## Test Data Recording

### Measurement Accuracy Template

| Test | Expected (mm) | Measured (mm) | Error (mm) | Error (%) | Confidence | Pass/Fail |
|------|---------------|---------------|------------|-----------|------------|-----------|
| T4.1-1 | 500 | | | | | |
| T4.1-2 | 500 | | | | | |
| T4.1-3 | 500 | | | | | |
| T4.2-1 | 1500 | | | | | |
| T4.3-1 | 3000 | | | | | |

### Repeatability Template

| Attempt | Measurement (mm) | Confidence | Notes |
|---------|------------------|------------|-------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| **Mean** | | | |
| **Std Dev** | | | |

## Acceptance Criteria

For MVP release, the following must pass:

### Critical (Must Pass)
- ✅ Anchors stable with normal hand movement
- ✅ Measurements accurate within ±3% at 1-2m
- ✅ No crashes during normal usage
- ✅ Sessions start/stop cleanly
- ✅ Confidence scores reasonable

### Important (Should Pass)
- ✅ Measurements repeatable (std dev < 2%)
- ✅ Tracking state feedback clear
- ✅ Photos capture successfully
- ✅ Pack creation works
- ✅ Export to JSON works

### Nice to Have
- ✅ Accurate at 3m+ distances
- ✅ Works in various lighting
- ✅ Handles edge cases gracefully

## Regression Testing

When making changes, re-run:
- T3.2 (Anchor Stability)
- T4.1-4.3 (Measurement Accuracy)
- T5.1 (Repeatability)

## Bug Reporting

When filing bugs, include:
1. Test case ID
2. Device model and iOS version
3. Steps to reproduce
4. Expected vs actual result
5. Screenshots/video
6. Measurement data (if applicable)
7. Lighting conditions
8. Surface type

## Next Steps

After MVP validation:
1. Field testing with actual users
2. Extended accuracy testing (5m+)
3. Various device testing
4. Real-world scenario validation
5. Performance profiling
