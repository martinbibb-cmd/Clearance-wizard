# ARKit Bridge API Reference

Complete TypeScript/Swift API documentation for the Clearance Wizard native module.

## Overview

The ARKit Bridge provides a React Native interface to iOS ARKit functionality. All methods are async and return Promises. Events are delivered via the React Native event emitter.

## Module Import

```typescript
import { ARKitBridge } from './src/native/ARKitBridge';
```

## Session Management

### `startSession(): Promise<{success: boolean}>`

Starts the AR session with world tracking configuration.

**Configuration:**
- World tracking (6DOF)
- Horizontal and vertical plane detection
- Light estimation enabled

**Example:**
```typescript
try {
  await ARKitBridge.startSession();
  console.log('AR session started');
} catch (error) {
  console.error('Failed to start AR:', error);
}
```

**Errors:**
- `NOT_SUPPORTED` - ARKit not available on device
- `CONFIG_ERROR` - Configuration initialization failed

---

### `stopSession(): Promise<{success: boolean}>`

Stops the AR session and removes all anchors.

**Example:**
```typescript
await ARKitBridge.stopSession();
```

## Surface Detection

### `hitTest(x: number, y: number): Promise<HitTestResult>`

Performs ray casting from screen coordinates to detect surfaces.

**Parameters:**
- `x` - Normalized X coordinate (0.0 to 1.0)
- `y` - Normalized Y coordinate (0.0 to 1.0)

**Returns:**
```typescript
interface HitTestResult {
  worldTransform: Transform;  // 4x4 matrix (16 floats)
  planeDetected: boolean;     // true if detected plane
  confidence: number;         // 0.7 (feature) or 1.0 (plane)
}
```

**Example:**
```typescript
// Convert touch coordinates to normalized
const x = touchX / screenWidth;
const y = touchY / screenHeight;

const result = await ARKitBridge.hitTest(x, y);
if (result.planeDetected) {
  console.log('Detected plane at:', result.worldTransform);
}
```

**Errors:**
- `NO_FRAME` - No current AR frame available
- `NO_HIT` - No surface detected at point

## Anchor Management

### `createAnchor(transform: Transform): Promise<AnchorResult>`

Creates a world anchor at the specified transform.

**Parameters:**
- `transform` - 4x4 transformation matrix (array of 16 numbers)

**Returns:**
```typescript
interface AnchorResult {
  anchorId: string;      // UUID of created anchor
  transform: Transform;  // Confirmed transform
}
```

**Example:**
```typescript
// Create anchor from hit test result
const hitResult = await ARKitBridge.hitTest(x, y);
const anchor = await ARKitBridge.createAnchor(hitResult.worldTransform);
console.log('Anchor created:', anchor.anchorId);
```

## Measurements

### `measureRay(x1: number, y1: number, x2: number, y2: number): Promise<MeasurementResult>`

Measures distance between two screen points by ray casting.

**Parameters:**
- `x1`, `y1` - First point (normalized 0.0-1.0)
- `x2`, `y2` - Second point (normalized 0.0-1.0)

**Returns:**
```typescript
interface MeasurementResult {
  distanceMm: number;    // Distance in millimeters
  pointA: Point3D;       // First point in world space
  pointB: Point3D;       // Second point in world space
  confidence: number;    // 0.7-1.0
}

interface Point3D {
  x: number;  // meters
  y: number;  // meters
  z: number;  // meters
}
```

**Example:**
```typescript
const result = await ARKitBridge.measureRay(0.3, 0.5, 0.7, 0.5);
console.log(`Distance: ${result.distanceMm}mm`);
console.log(`Confidence: ${(result.confidence * 100).toFixed(0)}%`);

// Convert to cm
const distanceCm = result.distanceMm / 10;
```

**Confidence Levels:**
- `1.0` - Both points on detected planes (highest confidence)
- `0.7` - One or both points on feature points (lower confidence)

**Errors:**
- `NO_FRAME` - No current AR frame available
- `NO_HIT` - Could not detect surfaces at both points

## Photo Capture

### `capturePhoto(): Promise<PhotoResult>`

Captures the current AR frame as a JPEG image.

**Returns:**
```typescript
interface PhotoResult {
  localPath: string;  // Absolute path to saved JPEG
  width: number;      // Image width in pixels
  height: number;     // Image height in pixels
}
```

**Example:**
```typescript
const photo = await ARKitBridge.capturePhoto();
console.log('Photo saved to:', photo.localPath);
// Path: /var/.../tmp/capture_1702823456789.jpg
```

**Notes:**
- Images saved to temporary directory
- JPEG quality: 90%
- Move to permanent location if needed

**Errors:**
- `NO_FRAME` - No current AR frame available
- `CAPTURE_ERROR` - Failed to create image
- `SAVE_ERROR` - Failed to save image

## Tracking State

### `getTrackingState(): Promise<TrackingStateResult>`

Gets current AR tracking state and reason.

**Returns:**
```typescript
interface TrackingStateResult {
  state: TrackingState;
  reason: TrackingStateReason;
}

enum TrackingState {
  NotAvailable = 'notAvailable',
  Limited = 'limited',
  Normal = 'normal',
}

enum TrackingStateReason {
  None = 'none',
  Initializing = 'initializing',
  ExcessiveMotion = 'excessiveMotion',
  InsufficientFeatures = 'insufficientFeatures',
  Relocalizing = 'relocalizing',
}
```

**Example:**
```typescript
const state = await ARKitBridge.getTrackingState();
if (state.state === 'normal') {
  console.log('✓ Tracking is stable');
} else {
  console.warn('⚠ Limited tracking:', state.reason);
}
```

## Event Subscriptions

### `onFrame(callback: (event: FrameEvent) => void): () => void`

Subscribe to AR frame updates (fires every frame ~60fps).

**Event Data:**
```typescript
interface FrameEvent {
  intrinsics: CameraIntrinsics;
  cameraTransform: Transform;
  trackingState: TrackingState;
  timestamp: number;  // Unix timestamp (ms)
}

interface CameraIntrinsics {
  fx: number;      // Focal length X
  fy: number;      // Focal length Y
  cx: number;      // Principal point X
  cy: number;      // Principal point Y
  width: number;   // Image width
  height: number;  // Image height
}
```

**Example:**
```typescript
const unsubscribe = ARKitBridge.onFrame(event => {
  console.log('Tracking:', event.trackingState);
  console.log('Camera position:', event.cameraTransform);
});

// Later: stop listening
unsubscribe();
```

**Notes:**
- High frequency events (careful with expensive operations)
- Unsubscribe when component unmounts
- Tracking state updates in real-time

---

### `onAnchorUpdate(callback: (event: AnchorUpdateEvent) => void): () => void`

Subscribe to anchor creation and updates.

**Event Data:**
```typescript
interface AnchorUpdateEvent {
  anchorId: string;
  transform: Transform;
  type: 'added' | 'updated';
}
```

**Example:**
```typescript
const unsubscribe = ARKitBridge.onAnchorUpdate(event => {
  if (event.type === 'added') {
    console.log('New anchor:', event.anchorId);
  } else {
    console.log('Anchor updated:', event.anchorId);
  }
});
```

---

### `onError(callback: (event: ErrorEvent) => void): () => void`

Subscribe to AR session errors.

**Event Data:**
```typescript
interface ErrorEvent {
  code: string;
  message: string;
}
```

**Example:**
```typescript
const unsubscribe = ARKitBridge.onError(event => {
  console.error('AR Error:', event.code, event.message);
  Alert.alert('AR Error', event.message);
});
```

**Common Errors:**
- `SESSION_ERROR` - General AR session failure

## Type Definitions

### Transform Matrix

4x4 transformation matrix in **column-major order** (ARKit standard):

```typescript
type Transform = number[];  // 16 elements

// Layout:
// [m00, m01, m02, m03,    // Column 0 (right vector)
//  m10, m11, m12, m13,    // Column 1 (up vector)
//  m20, m21, m22, m23,    // Column 2 (forward vector)
//  m30, m31, m32, m33]    // Column 3 (position)

// Extract position:
const x = transform[12];  // m30
const y = transform[13];  // m31
const z = transform[14];  // m32
```

### Coordinate System

ARKit uses a **right-handed coordinate system**:
- **+X** - Right
- **+Y** - Up
- **+Z** - Toward user (camera forward is -Z)

All measurements are in **meters** unless otherwise specified.

## Best Practices

### 1. Session Management
```typescript
useEffect(() => {
  ARKitBridge.startSession();
  return () => {
    ARKitBridge.stopSession();
  };
}, []);
```

### 2. Event Cleanup
```typescript
useEffect(() => {
  const unsubscribeFrame = ARKitBridge.onFrame(handleFrame);
  const unsubscribeError = ARKitBridge.onError(handleError);
  
  return () => {
    unsubscribeFrame();
    unsubscribeError();
  };
}, []);
```

### 3. Error Handling
```typescript
try {
  const result = await ARKitBridge.measureRay(x1, y1, x2, y2);
  if (result.confidence > 0.8) {
    // High confidence measurement
    saveMeasurement(result);
  } else {
    // Low confidence warning
    showWarning('Measurement may be inaccurate');
  }
} catch (error) {
  Alert.alert('Error', 'Could not complete measurement');
}
```

### 4. Coordinate Conversion
```typescript
// Touch to normalized coordinates
const normalizedX = touchX / screenWidth;
const normalizedY = touchY / screenHeight;

// Meters to millimeters
const distanceMm = distanceMeters * 1000;

// Millimeters to centimeters
const distanceCm = distanceMm / 10;
```

## Performance Considerations

- **Frame events** fire at ~60fps - avoid heavy computation
- **Hit testing** is fast (~5-10ms)
- **Photo capture** may take ~50-100ms
- Use `onFrame` sparingly or throttle updates
- Unsubscribe from events when not needed

## Platform Requirements

- **iOS 11.0+** for ARKit support
- **iPhone 6S+** or iPad Pro (2017+)
- **Physical device** required (no simulator support)

## Troubleshooting

### "Module not found"
Ensure native module is properly linked in Xcode project.

### "ARKit not supported"
- Device must support ARKit (iPhone 6S or later)
- Must run on physical device (not simulator)

### Poor tracking
- Move device slowly to initialize
- Point at textured surfaces
- Ensure good lighting
- Avoid blank walls or reflective surfaces

### Low confidence measurements
- Use detected planes when possible
- Keep measurements under 5 meters
- Ensure stable tracking state
- Avoid measuring at steep angles
