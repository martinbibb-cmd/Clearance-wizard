# Clearance Wizard iOS - SwiftUI + ARKit Starter

## Overview

This is a native iOS app built with SwiftUI and ARKit that demonstrates:
- Live AR camera view
- Marker detection (MVP uses QR codes via Vision framework)
- Raycast-based anchor placement from detected markers
- Stable tracking using ARTrackedRaycast
- 3D overlay visualization (semi-transparent blue box)

## Requirements

- **Xcode**: 15.0 or later
- **iOS Deployment Target**: 17.0
- **Device**: Physical iPhone/iPad with ARKit support (ARKit doesn't work in Simulator)
- **Languages**: Swift, SwiftUI

## Project Structure

```
apps/clearance-wizard-ios/
├── ClearanceWizardApp.swift    # App entry point
├── ContentView.swift            # Main SwiftUI view with UI overlay
├── ARViewContainer.swift        # ARKit + Vision integration
├── Info.plist                   # App configuration with camera permissions
└── README.md                    # This file
```

## Setup Instructions

### Option 1: Create Xcode Project Manually

1. **Create New Xcode Project**:
   - Open Xcode
   - File → New → Project
   - Choose "iOS" → "App"
   - Product Name: `Clearance Wizard`
   - Interface: SwiftUI
   - Language: Swift
   - Organization Identifier: `com.clearancewizard` (or your preference)
   - iOS Deployment Target: 17.0

2. **Add Source Files**:
   - Delete the default `ContentView.swift` that Xcode creates
   - Add the following files from this directory to your Xcode project:
     - `ClearanceWizardApp.swift` (replace default App file if needed)
     - `ContentView.swift`
     - `ARViewContainer.swift`

3. **Configure Info.plist**:
   - The `Info.plist` in this directory contains the required camera permission
   - Ensure your project's Info.plist includes:
     - `NSCameraUsageDescription`: "Camera is required for AR measurements."
     - `UIRequiredDeviceCapabilities`: Include "arkit"

4. **Build and Run**:
   - Connect a physical iOS device (ARKit requires real device)
   - Select your device as the build target
   - Build and run (⌘R)

### Option 2: Using Existing Xcode Project

If you already have an Xcode project:

1. Add the three Swift files to your project
2. Update your Info.plist with camera permissions
3. Ensure iOS Deployment Target is 17.0 or later
4. Build and run on a physical device

## Features

### Marker Detection (MVP)

The current implementation uses **QR code detection** via Apple's Vision framework to demonstrate the marker detection → raycast → anchor pipeline. This is the MVP approach.

**Why QR codes for MVP?**
- Built into iOS (no additional libraries needed)
- Fast and reliable
- Proves the detection and anchoring pipeline works

**Future Enhancement:**
Later, we can swap the QR detector for AprilTag or ArUco detection without changing the anchoring logic:
- Add OpenCV or a native AprilTag library
- Replace the `detectQRCodes` method in `ARViewContainer.swift`
- Keep the rest of the raycast/anchor pipeline unchanged

### ARKit Features

- **ARWorldTrackingConfiguration**: 6DOF camera tracking
- **Plane Detection**: Horizontal and vertical surfaces
- **Raycast**: Projects from marker center to place anchors on detected planes
- **ARTrackedRaycast**: Continuously updates anchor position for stability
- **Visual Indicator**: Semi-transparent blue box shows where marker is detected

### UI Features

- **Live Camera View**: Full-screen AR camera
- **Status Overlay**: Shows detection status and marker info
- **Anchor Count**: Displays number of placed anchors
- **Info Button**: Explains app functionality

## Usage

1. **Launch the app** on a physical iOS device
2. **Point camera** at a QR code
3. **Watch for detection**: Status will change from "Scanning..." to "Marker Detected"
4. **See the anchor**: A blue semi-transparent box appears where the QR code is detected
5. **Move around**: The anchor stays stable thanks to ARTrackedRaycast

## Testing

### Test with QR Codes

You can generate QR codes online or use existing ones:
- Visit: https://www.qr-code-generator.com/
- Create a simple text QR code
- Print it or display on another screen
- Point the app at it

### What to Look For

✅ **Good behavior:**
- QR code is detected quickly
- Blue box appears at QR code location
- Anchor stays stable when moving the device
- Detection info updates in real-time

❌ **Issues to note:**
- If detection is slow, ensure good lighting
- If anchor drifts, the surface might not have good tracking features
- If no detection occurs, try a different QR code or print size

## Architecture Notes

### Vision Framework

The `VNDetectBarcodesRequest` is used for QR detection:
- Runs on a background queue to avoid blocking AR rendering
- Throttled to 0.5 seconds to balance performance and responsiveness
- Returns normalized coordinates [0,1] with origin at bottom-left

### Coordinate Conversion

Vision uses normalized coordinates (0,0 at bottom-left), while ARKit screen space has origin at top-left:
```swift
let screenCenter = CGPoint(
    x: centerX,           // Same
    y: 1.0 - centerY      // Flip Y axis
)
```

### Raycast Strategy

1. **Preferred**: Raycast against existing detected planes
2. **Fallback**: Raycast against estimated planes if no planes detected yet
3. **Tracked**: Use ARTrackedRaycast for continuous position updates

### Anchor Management

- Only keeps the most recent anchor (removes old ones)
- Each anchor is named with the QR code payload
- Visual indicator (blue box) is created at anchor location

## Migration Path to AprilTag/ArUco

To upgrade from QR to AprilTag/ArUco:

1. **Add detection library**:
   - For OpenCV: Add via CocoaPods or SPM
   - For native AprilTag: Use a Swift wrapper

2. **Replace detection method**:
   - Keep the same `session(_:didUpdate:)` structure
   - Replace `detectQRCodes` with `detectAprilTags` or `detectArUco`
   - Return the same information (bounds, center point)

3. **Keep everything else**:
   - Coordinate conversion logic stays the same
   - Raycast logic stays the same
   - Anchor placement stays the same
   - UI updates stay the same

## Troubleshooting

### App won't build
- Ensure Xcode 15.0 or later
- Check iOS Deployment Target is 17.0+
- Verify all files are added to the target

### Camera permission denied
- Check Settings → Privacy & Security → Camera
- Ensure "Clearance Wizard" has camera access

### ARKit not working
- **Must use physical device** - Simulator not supported
- Device must support ARKit (iPhone 6S or later)
- Ensure good lighting conditions

### QR not detected
- Ensure QR code is clear and well-lit
- Try adjusting distance (20-50cm usually works well)
- Move device slowly to give Vision time to process

## Next Steps

Potential enhancements:
- [ ] Add AprilTag detection (replace QR)
- [ ] Support multiple simultaneous anchors
- [ ] Add measurement tools (distance, area)
- [ ] Persist anchors across sessions
- [ ] Add AR coach overlay for plane detection
- [ ] Improve visual indicators (different colors/shapes)
- [ ] Add gesture controls (tap to place, pinch to scale)

## License

See main repository LICENSE file.
