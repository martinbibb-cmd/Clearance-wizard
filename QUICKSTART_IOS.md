# Quick Start Guide - iOS Native Clearance Wizard

## What You're Building

A native iOS app that uses ARKit to:
1. Place a stable anchor in the real world
2. Measure distances between points
3. Capture photos with AR context
4. Store everything locally as "packs"
5. Export packs as JSON or ZIP

## Prerequisites

### Required
- **macOS** 12.0 or later
- **Xcode** 14.0 or later
- **Node.js** 18.0 or later
- **CocoaPods** 1.12 or later
- **iOS device** with ARKit support (iPhone 6S or later)

### Installation Commands
```bash
# Check versions
node --version    # Should be >= 18.0.0
pod --version     # Should be >= 1.12.0

# Install Node.js (if needed)
# Download from https://nodejs.org/

# Install CocoaPods (if needed)
sudo gem install cocoapods
```

## Setup (5 Minutes)

### 1. Clone and Install
```bash
# Clone repository
git clone https://github.com/martinbibb-cmd/Clearance-wizard.git
cd Clearance-wizard

# Install Node dependencies
npm install

# Build shared types package
cd packages/clearance-core
npm run build
cd ../..

# Install iOS dependencies
cd apps/clearance-wizard/ios
pod install
cd ../../..
```

### 2. Open in Xcode
```bash
# Open workspace (NOT .xcodeproj)
open apps/clearance-wizard/ios/ClearanceWizard.xcworkspace
```

### 3. Configure Signing
In Xcode:
1. Select **ClearanceWizard** target
2. Go to **Signing & Capabilities** tab
3. Select your **Team** from dropdown
4. Xcode will automatically create a provisioning profile

### 4. Connect Device
1. Connect your iPhone via USB
2. Trust computer on device if prompted
3. Select your device in Xcode's device menu (top bar)

### 5. Build & Run
- Click the ▶️ Play button in Xcode, or
- Press **Cmd+R**

First build may take 3-5 minutes (compiling React Native).

## Usage

### First Launch
1. **Grant camera permission** when prompted (required for AR)
2. **Grant photo library permission** (required to save images)

### Creating Your First Pack
1. Tap **"+ New Pack"** on home screen
2. (Optional) Enter site details and boiler info
3. Tap **"Continue to AR"**

### AR Measurement
1. **Point camera at flat surface** (floor, table, wall)
2. **Tap to place anchor** (one time only)
   - Look for detected planes (shown by ARKit)
   - Anchor should turn green when stable
3. **Tap first measurement point**
4. **Tap second measurement point**
5. **Review measurement** in alert
   - Distance shown in cm
   - Confidence percentage (aim for >70%)
6. **Save or discard** measurement
7. **Repeat** for more measurements
8. **Tap 📷** to capture photos

### Exporting Pack
1. Return to home screen (✓ Done)
2. Tap **"Export"** on pack card
3. Choose format:
   - **JSON** - Pack data only (small, fast)
   - **ZIP** - Pack data + all images (complete)

## Troubleshooting

### "ARKit not supported"
- ARKit only works on **physical iOS devices**
- iPhone 6S or later, iPad Pro, iPad (2017) or later
- Does **NOT** work in iOS Simulator

### Build Errors in Xcode
```bash
# Clean and rebuild
cd apps/clearance-wizard/ios
rm -rf Pods/ Podfile.lock
pod install
# Then rebuild in Xcode (Cmd+Shift+K, then Cmd+B)
```

### "Metro Bundler Not Found"
```bash
# Start Metro manually
cd apps/clearance-wizard
npm start

# In another terminal, run app
npm run ios
```

### Poor Tracking
- **Initializing** - Move device slowly side-to-side
- **Insufficient Features** - Point at textured surfaces (not blank walls)
- **Excessive Motion** - Move device more slowly
- **Lighting** - Ensure good lighting (not too dark, not too bright)

### Low Measurement Confidence
- Use detected planes (confidence closer to 100%)
- Avoid feature points (confidence ~70%)
- Keep measurements < 5 meters
- Ensure stable tracking before measuring

## Project Structure

```
apps/clearance-wizard/
├── ios/
│   └── ClearanceWizard/
│       ├── ARKitBridge.swift      # AR logic (Swift)
│       └── ARKitBridge.m          # Bridge to React Native
├── src/
│   ├── native/
│   │   └── ARKitBridge.ts         # TypeScript interface
│   ├── screens/
│   │   ├── HomeScreen.tsx         # Main menu
│   │   ├── SiteDetailsScreen.tsx  # Metadata entry
│   │   ├── ARMeasureScreen.tsx    # AR interface
│   │   └── ExportScreen.tsx       # Export options
│   ├── storage/
│   │   └── database.ts            # SQLite (TODO)
│   └── App.tsx                    # Navigation setup
└── package.json
```

## Key Files to Understand

### 1. `ARKitBridge.swift`
Native Swift code that:
- Starts/stops AR session
- Performs hit testing
- Creates anchors
- Measures distances
- Captures photos

### 2. `ARKitBridge.ts`
TypeScript wrapper that:
- Provides typed interface to Swift
- Handles async calls
- Manages event subscriptions

### 3. `ARMeasureScreen.tsx`
Main AR interface that:
- Shows live camera view
- Handles tap gestures
- Displays measurements
- Shows tracking state

### 4. `packages/clearance-core/src/types.ts`
Shared type definitions:
- `Pack` - Complete session
- `Capture` - Photo/measurement
- `ARContext` - AR metadata

## Next Steps

### For Users
1. Practice anchor placement on different surfaces
2. Take measurements at various distances
3. Compare measurements with physical tape measure
4. Export packs and verify data

### For Developers
1. Implement SQLite storage (see `src/storage/database.ts`)
2. Add ZIP export functionality
3. Improve measurement confidence gating
4. Add visual feedback for anchor placement
5. Implement pack sync to API (future)

## Common Questions

### Why iOS only?
- ARKit provides excellent tracking out-of-the-box
- Android (ARCore) can be added later
- Focus on getting iOS right first

### Why React Native?
- Cross-platform UI (future Android support)
- Fast development
- Hot reload for rapid iteration
- Native performance where it matters (AR in Swift)

### Why local-first?
- Works offline (construction sites often have poor connectivity)
- Fast and reliable
- No server dependencies for v1
- API sync can be added later

### Can I use markers?
- v1 uses tap-to-place (no markers needed)
- AprilTag anchor support can be added in v2
- Markerless is simpler and more flexible

## Support

- **Issues:** https://github.com/martinbibb-cmd/Clearance-wizard/issues
- **Documentation:** See `apps/clearance-wizard/README.md`
- **Architecture:** See `IOS_NATIVE_IMPLEMENTATION.md`

## License

See repository LICENSE file.
