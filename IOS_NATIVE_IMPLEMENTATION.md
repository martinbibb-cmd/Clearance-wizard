# iOS Native Clearance Wizard - Implementation Summary

## Overview

This repository now contains a **native iOS Clearance Wizard application** built with React Native and Swift ARKit. This is a complete standalone app designed to deliver stable AR measurements and local-first data management.

## What's New

### Monorepo Structure
The repository has been reorganized as a monorepo to support multiple apps and shared packages:

```
clearance-wizard/
├── apps/
│   └── clearance-wizard/          # NEW: React Native iOS app
│       ├── ios/                   # Swift ARKit native module
│       ├── src/                   # React Native screens & logic
│       └── package.json
├── packages/
│   ├── clearance-core/           # NEW: Shared TypeScript types
│   └── api/                      # (Reserved for future API sync)
├── python-dev/                   # Existing: VIO research code
├── src/                          # Existing: Web PWA detector modules
├── index.html                    # Existing: Web PWA application
└── package.json                  # NEW: Monorepo workspace root
```

### Two Applications in One Repo

#### 1. **Web PWA** (Existing - Unchanged)
- Browser-based AR using ArUco/AprilTag markers
- OpenCV.js for marker detection
- THREE.js for 3D rendering
- Works on any device with a camera
- Location: Root directory (`index.html`, `src/`, etc.)

#### 2. **iOS Native App** (New)
- Native ARKit implementation
- React Native UI
- Swift native module for AR
- Local SQLite storage
- Location: `apps/clearance-wizard/`

## Key Features of iOS Native App

### 1. Stable AR Tracking
- **ARKit World Tracking** - 6DOF camera pose estimation
- **Tap-to-place anchor** - Single stable reference point
- **No marker flicker** - Measurements relative to anchor, not per-frame re-solving

### 2. Accurate Measurements
- **Point-to-point measurement** - Tap two points, get distance in mm
- **Confidence scoring** - Based on plane detection vs feature points
- **Real-world units** - Millimeters with conversion to cm/m

### 3. Local-First Storage
- **Pack structure** - Self-contained measurement sessions
- **SQLite database** - Packs, captures, measurements, attachments
- **Filesystem storage** - Photos stored locally with paths in DB
- **Export options** - JSON (data only) or ZIP (data + images)

### 4. Complete Workflow
- **Home** - Create new pack, continue existing, or export
- **Site Details** - Optional metadata (address, boiler model, etc.)
- **AR Measure** - Live camera, anchor placement, measurements
- **Export** - Review and export pack for sharing/archiving

## Architecture Details

### Swift ARKit Native Module

**Location:** `apps/clearance-wizard/ios/ClearanceWizard/ARKitBridge.swift`

**Key Methods:**
- `startSession()` - Initialize AR world tracking
- `stopSession()` - Pause session and cleanup
- `hitTest(x, y)` - Ray cast from screen coordinates
- `createAnchor(transform)` - Place world anchor
- `measureRay(x1, y1, x2, y2)` - Measure distance between points
- `capturePhoto()` - Save current AR frame
- `getTrackingState()` - Monitor tracking quality

**Events:**
- `onFrame` - Camera intrinsics and transform updates
- `onAnchorUpdate` - Anchor added/updated
- `onError` - Error notifications

### TypeScript Bridge

**Location:** `apps/clearance-wizard/src/native/ARKitBridge.ts`

Provides typed interface from JavaScript to Swift:
```typescript
import { ARKitBridge } from '../native/ARKitBridge';

// Start AR session
await ARKitBridge.startSession();

// Measure distance
const result = await ARKitBridge.measureRay(x1, y1, x2, y2);
// { distanceMm: 1523.4, pointA: {x,y,z}, pointB: {x,y,z}, confidence: 0.95 }

// Subscribe to events
const unsubscribe = ARKitBridge.onFrame(event => {
  console.log('Tracking state:', event.trackingState);
});
```

### Shared Type Definitions

**Location:** `packages/clearance-core/src/types.ts`

Core types used across the application:
- `Pack` - Complete measurement session
- `Capture` - Individual photo/measurement/annotation
- `Measurement` - Distance measurement with confidence
- `ARContext` - AR metadata (anchor, intrinsics, tracking state)
- `CameraIntrinsics` - Camera focal length and principal point
- `Transform` - 4x4 transformation matrix

These types are shared between:
1. React Native app
2. Swift native module (through JSON serialization)
3. Future API backend (for sync)

### Local Storage

**Location:** `apps/clearance-wizard/src/storage/database.ts`

SQLite schema (to be implemented):
- **packs** - Pack metadata
- **captures** - Individual captures within packs
- **measurements** - Measurements within captures
- **attachments** - Photos and other files

## Development Setup

### Prerequisites
- macOS 12.0+ (for iOS development)
- Xcode 14.0+
- Node.js 18.0+
- CocoaPods 1.12+

### Installation
```bash
# From repository root
npm install

# Build shared types package
cd packages/clearance-core
npm run build

# Install iOS dependencies
cd ../../apps/clearance-wizard/ios
pod install
```

### Running
```bash
# Start Metro bundler
cd apps/clearance-wizard
npm start

# Run on iOS device (in another terminal)
npm run ios
```

**Note:** ARKit requires a physical iOS device. It does not work in the simulator.

## Migration Path

### Web PWA → iOS Native

The iOS native app is a **separate application**, not a replacement:

1. **Web PWA** - Quick deployment, works everywhere, good for demos
2. **iOS Native** - Production quality, stable tracking, better UX

Users can:
- Use web PWA for quick checks
- Use iOS app for official clearance measurements
- Export packs from iOS app for processing by Hail Mary

### Future: API Sync

Phase 1 (Current): **Local-only**
- All data stored in SQLite
- Export as JSON/ZIP
- No network dependencies

Phase 2 (Future): **API Sync**
- Push packs to Hail Mary API
- Download packs from API
- Offline-first with background sync
- Conflict resolution

## Milestones

### M1: ARKit Bridge ✅
- [x] Swift native module
- [x] TypeScript wrapper
- [x] Session management
- [x] Hit testing and anchors
- [x] Event system

### M2: Measurement Tools 🚧
- [x] Basic measureRay
- [ ] Confidence gating
- [ ] Repeatability validation
- [ ] Visual feedback

### M3: Pack Storage 📋
- [ ] SQLite implementation
- [ ] CRUD operations
- [ ] Photo management
- [ ] ZIP export

### M4: Polish 📋
- [ ] Error handling
- [ ] Performance optimization
- [ ] User testing
- [ ] Documentation

## Non-Goals (for v1)

To keep the initial release focused:
- ❌ Full Hail Mary workflow integration
- ❌ Multi-device sync/conflict resolution
- ❌ Android support (ARCore)
- ❌ Marker-based anchors (tap-to-place is simpler)

These can be added after v1 is stable.

## Comparison: Web PWA vs iOS Native

| Feature | Web PWA | iOS Native |
|---------|---------|------------|
| **Platform** | Any browser | iOS only |
| **AR Engine** | OpenCV markers | ARKit world tracking |
| **Tracking** | Marker-based | Markerless |
| **Stability** | Good (marker dependent) | Excellent (ARKit) |
| **Accuracy** | Good | Excellent |
| **Setup** | Print markers | No markers needed |
| **Offline** | Yes (after first load) | Yes (fully offline) |
| **Storage** | Browser storage | SQLite + filesystem |
| **Export** | Screenshots | JSON + ZIP with images |
| **Installation** | PWA install | App Store |

## Testing

### Web PWA Testing
```bash
# From repository root
python -m http.server 8000
# Open http://localhost:8000
```

### iOS Native Testing
```bash
# From apps/clearance-wizard
npm run ios
# Requires physical iOS device
```

## Documentation

- **iOS App:** `apps/clearance-wizard/README.md`
- **Shared Types:** `packages/clearance-core/src/types.ts`
- **Web PWA:** `README.md` (root)
- **Python VIO:** `python-dev/README.md`

## Contributing

When contributing:
1. **Type changes** - Update `packages/clearance-core/src/types.ts`
2. **Native features** - Implement in Swift, wrap in TypeScript
3. **UI changes** - React Native screens in `apps/clearance-wizard/src/screens/`
4. **Web PWA** - Continue using root directory files

## Next Steps

1. **Complete M2** - Measurement tools with confidence gating
2. **Implement M3** - SQLite storage and export
3. **User testing** - Real-world validation with field engineers
4. **API design** - Plan Hail Mary integration

## Questions?

See detailed documentation in:
- `apps/clearance-wizard/README.md` - iOS app specifics
- `README.md` - Web PWA documentation
- `ARCHITECTURE.md` - Web PWA architecture
