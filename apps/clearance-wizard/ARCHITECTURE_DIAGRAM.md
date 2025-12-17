# Clearance Wizard iOS - Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Native Layer                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                     Navigation                             │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │  Home    │→ │   Site   │→ │    AR    │→ │  Export  │  │  │
│  │  │  Screen  │  │ Details  │  │  Measure │  │  Screen  │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │               TypeScript Business Logic                    │  │
│  │  • Pack management                                         │  │
│  │  • Measurement workflow                                    │  │
│  │  • UI state management                                     │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Native Module Bridge                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         ARKitBridge.ts (TypeScript Wrapper)               │  │
│  │  • Type-safe async methods                                │  │
│  │  • Event subscriptions                                    │  │
│  │  • Error handling                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↕                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │      ARKitBridge.m (Objective-C Bridge)                   │  │
│  │  • RCT_EXTERN_METHOD declarations                         │  │
│  │  • Event emitter setup                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Swift ARKit Layer                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         ARKitBridge.swift (Native Module)                 │  │
│  │                                                            │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │         ARSession (ARKit Core)                   │    │  │
│  │  │  • ARWorldTrackingConfiguration                  │    │  │
│  │  │  • ARSessionDelegate                             │    │  │
│  │  │  • Plane detection                               │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                            │  │
│  │  Public API:                                               │  │
│  │  • startSession() / stopSession()                         │  │
│  │  • hitTest(x, y) → surface detection                     │  │
│  │  • createAnchor(transform) → stable reference            │  │
│  │  • measureRay(x1,y1, x2,y2) → distance                   │  │
│  │  • capturePhoto() → JPEG image                           │  │
│  │  • getTrackingState() → quality monitoring               │  │
│  │                                                            │  │
│  │  Events:                                                   │  │
│  │  • onFrame → camera data @ 60fps                          │  │
│  │  • onAnchorUpdate → anchor changes                        │  │
│  │  • onError → error notifications                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                      iOS ARKit Framework                         │
│  • Camera tracking (6DOF)                                       │
│  • Plane detection (horizontal + vertical)                      │
│  • Feature point tracking                                       │
│  • Light estimation                                             │
│  • Device motion fusion (IMU + camera)                          │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Session Initialization

```
User Opens App
    ↓
HomeScreen.tsx
    ↓
User taps "New Pack"
    ↓
SiteDetailsScreen.tsx
    ↓
User taps "Continue to AR"
    ↓
ARMeasureScreen.tsx
    ↓
useEffect() → ARKitBridge.startSession()
    ↓
TypeScript Bridge → Native Bridge → Swift
    ↓
ARSession.run(configuration)
    ↓
ARKit starts tracking
    ↓
Events flow back:
    Swift → Native Bridge → TypeScript → React
```

### 2. Anchor Placement

```
User taps screen
    ↓
TouchableOpacity.onPress(x, y)
    ↓
ARKitBridge.hitTest(x, y)
    ↓
Swift: frame.hitTest(point, types: [.existingPlaneUsingExtent])
    ↓
Returns: { worldTransform, planeDetected, confidence }
    ↓
ARKitBridge.createAnchor(worldTransform)
    ↓
Swift: session.add(anchor: ARAnchor(transform))
    ↓
ARKit maintains anchor pose
    ↓
onAnchorUpdate event fires
    ↓
UI updates: "Anchor placed ✓"
```

### 3. Distance Measurement

```
User taps first point (x1, y1)
    ↓
Store in state: measurementStart
    ↓
User taps second point (x2, y2)
    ↓
ARKitBridge.measureRay(x1, y1, x2, y2)
    ↓
Swift: 
  1. hitTest(point1) → worldPos1
  2. hitTest(point2) → worldPos2
  3. distance = sqrt((x2-x1)² + (y2-y1)² + (z2-z1)²)
  4. distanceMm = distance * 1000
    ↓
Returns: { distanceMm, pointA, pointB, confidence }
    ↓
UI displays measurement + confidence
    ↓
User saves → stored in Pack
```

### 4. Photo Capture

```
User taps 📷 button
    ↓
ARKitBridge.capturePhoto()
    ↓
Swift:
  1. Get current frame.capturedImage (CVPixelBuffer)
  2. Convert to CGImage
  3. Convert to UIImage
  4. Compress as JPEG (90%)
  5. Save to /tmp/capture_{timestamp}.jpg
    ↓
Returns: { localPath, width, height }
    ↓
UI shows success
    ↓
Path stored in Capture.photoPath
```

## Storage Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                           │
│                     (React Native)                               │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Storage Interface Layer                         │
│                   (database.ts)                                  │
│  • createPack(pack: Pack)                                       │
│  • getPack(packId: string)                                      │
│  • updatePack(pack: Pack)                                       │
│  • addCapture(packId, capture)                                  │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                    SQLite Database                               │
│                   (To be implemented)                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Table: packs                                          │    │
│  │  ┌──────────┬──────────┬──────────┬──────────────┐    │    │
│  │  │ packId   │createdAt │updatedAt │ siteData     │    │    │
│  │  │ (PK)     │          │          │ (JSON)       │    │    │
│  │  └──────────┴──────────┴──────────┴──────────────┘    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Table: captures                                       │    │
│  │  ┌──────────┬──────────┬──────────┬──────────────┐    │    │
│  │  │captureId │ packId   │   type   │  timestamp   │    │    │
│  │  │  (PK)    │  (FK)    │          │              │    │    │
│  │  └──────────┴──────────┴──────────┴──────────────┘    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Table: measurements                                   │    │
│  │  ┌──────────┬──────────┬──────────┬──────────────┐    │    │
│  │  │measureId │captureId │distanceMm│ confidence   │    │    │
│  │  │  (PK)    │  (FK)    │          │              │    │    │
│  │  └──────────┴──────────┴──────────┴──────────────┘    │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Filesystem                                 │
│                                                                  │
│  Documents/packs/{packId}/                                      │
│    ├── capture_1702823456789.jpg                               │
│    ├── capture_1702823467890.jpg                               │
│    └── ...                                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Pack Export Flow

```
User taps "Export Pack"
    ↓
ExportScreen loads Pack from database
    ↓
User selects format:
    │
    ├─→ JSON Export
    │     ↓
    │   JSON.stringify(pack)
    │     ↓
    │   Save to Documents/pack_{packId}.json
    │     ↓
    │   Share sheet (email, AirDrop, etc.)
    │
    └─→ ZIP Export
          ↓
        Create temp directory
          ↓
        Write pack.json
          ↓
        Copy all image files
          ↓
        Zip directory
          ↓
        Save to Documents/pack_{packId}.zip
          ↓
        Share sheet
```

## Type System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│               @clearance-wizard/core package                     │
│                  (Shared TypeScript Types)                       │
│                                                                  │
│  types.ts:                                                       │
│  • Pack                                                         │
│  • Capture                                                      │
│  • Measurement                                                  │
│  • ARContext                                                    │
│  • CameraIntrinsics                                            │
│  • Transform                                                    │
│  • Point3D                                                      │
└──────────────┬──────────────────┬───────────────────────────────┘
               ↓                  ↓
    ┌──────────────────┐   ┌────────────────┐
    │  React Native    │   │  Future API    │
    │      App         │   │   Backend      │
    └──────────────────┘   └────────────────┘
```

## Thread Model

```
┌─────────────────────────────────────────────────────────────────┐
│                       JavaScript Thread                          │
│  • React component rendering                                    │
│  • State management                                             │
│  • UI event handling                                            │
│  • TypeScript business logic                                    │
└──────────────────────┬──────────────────────────────────────────┘
                       ↕ (async)
┌─────────────────────────────────────────────────────────────────┐
│                         Main Thread                              │
│                        (iOS UI Thread)                           │
│  • ARSession updates                                            │
│  • ARSessionDelegate callbacks                                  │
│  • Native module method calls                                   │
│  • Event emission to JavaScript                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Note:** All ARKit operations must happen on the main thread (enforced by `DispatchQueue.main.async` in Swift code).

## Memory Management

```
┌─────────────────────────────────────────────────────────────────┐
│                      React Native Heap                           │
│  • Component state                                              │
│  • Pack data structures                                         │
│  • Image paths (strings)                                        │
│  • TypeScript objects                                           │
│  Managed by: JavaScript garbage collector                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         Native Heap                              │
│  • ARSession instance                                           │
│  • AR anchors dictionary                                        │
│  • Current frame buffer                                         │
│  • Temporary image buffers                                      │
│  Managed by: Swift ARC (Automatic Reference Counting)           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      ARKit Framework                             │
│  • World tracking state                                         │
│  • Feature maps                                                 │
│  • Plane anchors                                                │
│  • Camera buffers                                               │
│  Managed by: ARKit (deallocated on stopSession)                 │
└─────────────────────────────────────────────────────────────────┘
```

## Performance Characteristics

| Operation | Time | Frequency | Thread |
|-----------|------|-----------|--------|
| `startSession()` | ~100-500ms | Once | Main |
| `hitTest()` | ~5-10ms | Per tap | Main |
| `createAnchor()` | ~1-5ms | Once | Main |
| `measureRay()` | ~10-20ms | Per measurement | Main |
| `capturePhoto()` | ~50-100ms | Per photo | Main |
| `onFrame` event | ~1ms | 60fps | Main → JS |
| Pack save | ~10-50ms | Per save | Background (future) |

## Error Recovery

```
Error Occurs
    ↓
Try to recover:
    │
    ├─→ Session error
    │     └→ Restart session
    │
    ├─→ Tracking lost
    │     └→ Show UI guidance
    │         ("Move device slowly")
    │
    ├─→ Hit test failed
    │     └→ Show error message
    │         ("No surface detected")
    │
    └─→ Critical error
          └→ Navigate back to home
              Show alert
```

## Future Architecture Plans

### Phase 2: API Sync

```
React Native App
    ↓
Local SQLite Database
    ↓
Sync Layer (Background)
    ↓
Hail Mary API
    │
    ├─→ POST /packs (create)
    ├─→ PUT /packs/{id} (update)
    ├─→ GET /packs/{id} (download)
    └─→ POST /packs/{id}/attachments (upload images)
```

### Phase 3: AprilTag Anchors

```
ARKit Session
    ↓
Camera Frame
    ↓
AprilTag Detector (native)
    ↓
Detected Tag → Known pose
    ↓
Create anchor at tag location
    ↓
Use as stable world origin
```
