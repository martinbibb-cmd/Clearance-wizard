# Clearance Wizard - iOS Native ARKit App

A standalone iOS application for AR-based clearance measurements using ARKit, built with React Native and Swift.

## Overview

This is a native iOS implementation of Clearance Wizard that provides:
- **Stable AR tracking** using ARKit
- **Accurate measurements** in real-world units
- **Local-first data storage** as "packs" (JSON + images)
- **Evidence capture** (photos + measurements + notes)
- **Offline operation** with no API dependencies

## Architecture

### Tech Stack
- **React Native 0.73** - Cross-platform UI framework (iOS-first)
- **Swift ARKit** - Native AR tracking and measurements
- **TypeScript** - Type-safe JavaScript
- **SQLite** - Local database for packs
- **React Navigation** - Screen navigation

### Project Structure
```
apps/clearance-wizard/
├── ios/                      # iOS native code
│   ├── Podfile              # CocoaPods dependencies
│   └── ClearanceWizard/
│       ├── ARKitBridge.swift    # Swift ARKit native module
│       ├── ARKitBridge.m        # Objective-C bridge
│       └── Info.plist           # iOS app configuration
├── src/
│   ├── native/              # TypeScript wrappers for native modules
│   │   └── ARKitBridge.ts   # ARKit bridge interface
│   ├── screens/             # React Native screens
│   │   ├── HomeScreen.tsx           # Main entry point
│   │   ├── SiteDetailsScreen.tsx    # Site metadata entry
│   │   ├── ARMeasureScreen.tsx      # AR measurement interface
│   │   └── ExportScreen.tsx         # Pack review and export
│   ├── storage/             # Local storage layer
│   │   └── database.ts      # SQLite pack database
│   └── App.tsx              # Main app component with navigation
├── package.json
└── tsconfig.json
```

## Core Concepts

### 1. Pack (Local-First Data Structure)
A "pack" represents a complete site visit:
```typescript
{
  packId: string;          // UUID
  createdAt: number;       // Unix timestamp
  updatedAt: number;
  site: {                  // Optional metadata
    address?: string;
    leadRef?: string;
    customerRef?: string;
  };
  boiler: {                // Optional boiler context
    model?: string;
    location?: string;
  };
  captures: [              // Evidence items
    {
      captureId: string;
      type: "photo" | "measurement" | "annotation";
      timestamp: number;
      photoPath?: string;   // Local filesystem path
      measurements: [...];  // Array of measurements
      notes?: string;
      ar: {                 // AR context
        anchorTransform: number[];  // 4x4 matrix
        cameraIntrinsics: {...};
        trackingState: string;
        timestamp: number;
      }
    }
  ]
}
```

### 2. AR Session Behavior
**Stable Anchor-Based Tracking:**
1. User taps a detected plane to place world anchor
2. All measurements are relative to this stable anchor
3. No per-frame pose re-solving (prevents flicker)

**ARKit Configuration:**
- `ARWorldTrackingConfiguration` for 6DOF tracking
- Horizontal and vertical plane detection
- Light estimation enabled
- High-quality frame semantics

### 3. Native Module API (Swift → JavaScript)

#### Session Management
- `startSession()` - Initialize ARKit world tracking
- `stopSession()` - Pause session and clear anchors

#### Hit Testing & Anchors
- `hitTest(x, y)` - Ray cast from screen coordinates
- `createAnchor(transform)` - Place world anchor

#### Measurements
- `measureRay(x1, y1, x2, y2)` - Measure distance between points
- Returns: `{ distanceMm, pointA, pointB, confidence }`

#### Capture
- `capturePhoto()` - Save current AR frame
- Returns: `{ localPath, width, height }`

#### State Monitoring
- `getTrackingState()` - Current tracking quality
- Events: `onFrame`, `onAnchorUpdate`, `onError`

## Installation & Setup

### Prerequisites
- macOS 12.0 or later
- Xcode 14.0 or later
- Node.js 18.0 or later
- CocoaPods 1.12 or later
- iOS device with ARKit support (iPhone 6S or later)

### Install Dependencies
```bash
# Install Node dependencies (from repository root)
npm install

# Navigate to iOS app
cd apps/clearance-wizard

# Install iOS dependencies
cd ios && pod install && cd ..
```

### Build Shared Packages
```bash
# From repository root
cd packages/clearance-core
npm run build
```

## Running the App

### Development Mode
```bash
# Start Metro bundler
npm start

# In another terminal, run on iOS
npm run ios
```

### Build for Device
1. Open `ios/ClearanceWizard.xcworkspace` in Xcode
2. Select your development team
3. Select your device
4. Build and run (Cmd+R)

## Usage Flow

### 1. Home Screen
- View existing packs
- Create new pack
- Continue working on pack
- Export pack

### 2. Site Details (Optional)
- Enter site address
- Add lead/customer references
- Enter boiler model and location
- Add general notes

### 3. AR Measure
1. Point camera at flat surface
2. Tap to place anchor (one-time)
3. Tap first point to start measurement
4. Tap second point to complete measurement
5. Review distance and confidence
6. Save measurement to pack
7. Capture photos as needed

### 4. Export
- Review pack summary
- Export as JSON (data only)
- Export as ZIP (data + images)

## Development

### Type Safety
All core types are defined in `@clearance-wizard/core`:
- `Pack`, `Capture`, `Measurement`
- `CameraIntrinsics`, `Transform`, `Point3D`
- `TrackingState`, `ARContext`

### Adding New Features
1. Update types in `packages/clearance-core/src/types.ts`
2. Rebuild core package: `npm run build`
3. Implement in Swift if native functionality needed
4. Create TypeScript wrapper in `src/native/`
5. Use in React Native screens

### Testing on Device
ARKit requires a physical iOS device. The simulator does not support ARKit.

## Milestones

### ✅ M1: ARKit Bridge (Complete)
- [x] Swift native module skeleton
- [x] Session start/stop
- [x] Hit testing and anchor placement
- [x] Tracking state monitoring
- [x] Event bridge to JavaScript

### 🚧 M2: Measurement Tools (In Progress)
- [x] Basic measureRay implementation
- [ ] Confidence gating logic
- [ ] Measurement repeatability validation
- [ ] Visual feedback for measurements

### 📋 M3: Pack Storage (Planned)
- [ ] SQLite schema implementation
- [ ] Pack CRUD operations
- [ ] Photo storage and management
- [ ] ZIP export functionality

### 📋 M4: Polish & Testing (Planned)
- [ ] Error handling and recovery
- [ ] Offline operation validation
- [ ] Performance optimization
- [ ] User testing and feedback

## Future Enhancements (Post-v1)

### Optional Features
- **AprilTag anchor support** - Known origin for repeatability
- **API sync** - Push packs to Hail Mary backend
- **Multi-device sync** - Conflict resolution
- **Android support** - ARCore implementation

## Troubleshooting

### Common Issues

**"ARKit not supported" error**
- Ensure you're running on a physical device (iPhone 6S or later)
- ARKit does not work in iOS Simulator

**Build errors in Xcode**
- Run `pod install` in ios/ directory
- Clean build folder (Cmd+Shift+K)
- Ensure development team is selected

**Metro bundler connection issues**
- Reset Metro: `npm start -- --reset-cache`
- Check firewall settings
- Ensure device and Mac are on same network

## Contributing

This is a standalone iOS app that will eventually integrate with the Hail Mary platform. For now, focus on:
1. Stable AR tracking
2. Reliable measurements
3. Robust local storage
4. Excellent offline experience

## License

See repository LICENSE file.
