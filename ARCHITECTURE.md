# Clearance Genie Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                         │
│  ┌───────────┐  ┌─────────────┐  ┌──────────────────────┐  │
│  │  Welcome  │  │ Main Menu   │  │   Camera View       │  │
│  │  Screen   │→ │ Configuration│→ │   + AR Overlay      │  │
│  └───────────┘  └─────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Application Controller (App)               │
│  • Manages application state                                  │
│  • Handles user interactions                                  │
│  • Coordinates between components                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
         ┌────────────────────┴────────────────────┐
         ↓                                         ↓
┌──────────────────────┐              ┌───────────────────────┐
│   VisionSystem       │              │  GraphicsEngine       │
│  (Marker Detection)  │              │  (3D Rendering)       │
└──────────────────────┘              └───────────────────────┘
         ↓                                         ↓
┌──────────────────────┐              ┌───────────────────────┐
│  Marker Detectors    │              │  THREE.js Renderer    │
│  ┌────────────────┐  │              │  • Camera             │
│  │ ArUco Detector │  │              │  • Scene              │
│  │ (OpenCV.js)    │  │              │  • Meshes & Materials │
│  └────────────────┘  │              └───────────────────────┘
│  ┌────────────────┐  │
│  │AprilTag Detect.│  │
│  │(Custom Impl.)  │  │
│  └────────────────┘  │
└──────────────────────┘
```

## Marker Detection Pipeline

```
┌──────────────┐
│ Video Frame  │
└──────┬───────┘
       ↓
┌──────────────────────┐
│ Scale & Convert to   │
│ Grayscale (0.5x)     │
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│ Histogram            │
│ Equalization         │
└──────┬───────────────┘
       ↓
┌──────────────────────────────────────────┐
│          Marker Type Selection            │
└──────┬────────────────────┬───────────────┘
       ↓                    ↓
┌──────────────────┐  ┌──────────────────────┐
│ ArUco Detection  │  │ AprilTag Detection   │
│ (OpenCV Native)  │  │ (Custom OpenCV)      │
│                  │  │                      │
│ • detectMarkers()│  │ • GaussianBlur()     │
│ • Returns IDs    │  │ • adaptiveThreshold()│
│ • Returns corners│  │ • findContours()     │
│                  │  │ • Filter squares     │
│                  │  │ • Assign sequential  │
│                  │  │   IDs                │
└──────┬───────────┘  └──────┬───────────────┘
       └────────┬─────────────┘
                ↓
       ┌────────────────────┐
       │  MarkerDetection[] │
       │  • id              │
       │  • family          │
       │  • cornersPx       │
       │  • centerPx        │
       │  • confidence      │
       └────────┬───────────┘
                ↓
       ┌────────────────────┐
       │  Pose Estimation   │
       │  (Pinhole Camera)  │
       │  • Calculate depth │
       │  • Calculate x,y,z │
       │  • Calculate rot   │
       └────────┬───────────┘
                ↓
       ┌────────────────────┐
       │  AR Overlay        │
       │  • Update 3D pos   │
       │  • Update rotation │
       │  • Render clearance│
       │    zones           │
       └────────────────────┘
```

## Component Interaction Flow

### 1. Application Startup

```
User opens app
    ↓
Load OpenCV.js (with CDN fallback)
    ↓
Load AprilTag.js
    ↓
Load detector modules
    ↓
Initialize App controller
    ↓
Show welcome screen
```

### 2. Configuration

```
User taps "Get Started"
    ↓
Show main menu
    ↓
User selects:
  • Marker Type (ArUco/AprilTag)
  • Detection Mode (Single/Multi)
  • Marker Size
  • Appliance Type
    ↓
Validate inputs
    ↓
User taps "Start Camera"
```

### 3. Camera Session

```
Request camera access
    ↓
Initialize VisionSystem with marker type
    ↓
Initialize GraphicsEngine
    ↓
Start detection loop (requestAnimationFrame)
    ↓
For each frame:
  1. Capture video frame
  2. Detect markers
  3. Calculate pose
  4. Update 3D graphics
  5. Render AR overlay
  6. Draw marker feedback
    ↓
Loop until user stops
```

### 4. Marker Detection (ArUco Path)

```
Video frame
    ↓
Convert to grayscale
    ↓
cv.detectMarkers()
    ↓
Extract marker IDs and corners
    ↓
Calculate pose from corners
    ↓
Return pose {x, y, z, rotation}
```

### 5. Marker Detection (AprilTag Path)

```
Video frame
    ↓
Convert to grayscale
    ↓
Apply Gaussian blur
    ↓
Adaptive thresholding
    ↓
Find contours
    ↓
Filter for quadrilaterals
    ↓
Check aspect ratio (roughly square)
    ↓
Extract corners and center
    ↓
Assign sequential ID
    ↓
Return MarkerDetection[]
    ↓
Calculate pose from detections
    ↓
Return pose {x, y, z, rotation}
```

## Data Structures

### MarkerDetection (Unified Interface)

```javascript
{
    id: number,              // Marker identifier
    family: string,          // "DICT_4X4_50" or "tag36h11"
    cornersPx: [             // Four corners [TL, TR, BR, BL]
        {x: number, y: number},
        {x: number, y: number},
        {x: number, y: number},
        {x: number, y: number}
    ],
    centerPx: {              // Center point
        x: number,
        y: number
    },
    confidence: number       // 0-1 (optional)
}
```

### Pose (3D Position + Rotation)

```javascript
{
    x: number,               // Horizontal position (mm)
    y: number,               // Vertical position (mm)
    z: number,               // Depth from camera (mm, negative)
    rotation: {              // Orientation angles (radians)
        x: number,           // Tilt (pitch)
        y: number,           // Pan (yaw)
        z: number            // Roll
    },
    // Multi-marker mode only:
    detectedIds: number[],   // Array of detected marker IDs
    detectedMarkers: {},     // Map of id -> marker data
    requiredCount: number,   // Expected marker count
    allMarkersFound: boolean // All required markers detected
}
```

## Class Hierarchy

```
VisionSystem
├── Properties
│   ├── ready: boolean
│   ├── scale: number (0.5)
│   ├── markerType: 'aruco' | 'apriltag'
│   ├── src: cv.Mat
│   ├── gray: cv.Mat
│   ├── dictionary: cv.aruco_Dictionary (ArUco)
│   ├── detectorParams: cv.aruco_DetectorParameters (ArUco)
│   └── apriltagDetector: AprilTagDetector (AprilTag)
│
└── Methods
    ├── init(video, markerType)
    ├── findMarker(video, markerSize, detectionMode)
    ├── _findArucoMarker(video, markerSize)
    ├── _findMultipleArucoMarkers(video, markerSize, mode)
    ├── _findAprilTagMarker(video, markerSize, mode)
    ├── _getPoseFromDetection(detection, vw, vh, markerSize)
    ├── _getPoseFromCorners(corners, vw, vh, scale, markerSize)
    ├── _getRotationFromCorners(corners) - OpenCV Mat format
    ├── _getRotationFromCornersArray(corners) - Array format
    ├── _calculateMultiMarkerPose(markers, ids, video, size, mode)
    └── _calculateMultiMarkerPoseFromDetections(detections, ...)

AprilTagDetector
├── Properties
│   ├── family: string
│   ├── tagFamilyData: object
│   ├── initialized: boolean
│   ├── grayMat: cv.Mat
│   ├── blurredMat: cv.Mat
│   ├── binaryMat: cv.Mat
│   ├── contours: cv.MatVector
│   └── hierarchy: cv.Mat
│
└── Methods
    ├── init() -> Promise<void>
    ├── detect(grayImageData, width, height) -> MarkerDetection[]
    └── dispose()

GraphicsEngine
├── Properties
│   ├── scene: THREE.Scene
│   ├── camera: THREE.PerspectiveCamera
│   ├── renderer: THREE.WebGLRenderer
│   ├── root: THREE.Group
│   ├── stencil: THREE.Group
│   └── parallaxEnabled: boolean
│
└── Methods
    ├── setStencil(data)
    ├── _createBox(data)
    ├── _createRadial(data)
    ├── _addDepthIndicator(...)
    └── render()

App (Controller)
├── Properties
│   ├── markerSize: number
│   ├── detectionMode: 'single' | '4-marker' | '5-marker'
│   ├── markerType: 'aruco' | 'apriltag'
│   ├── vision: VisionSystem
│   ├── graphics: GraphicsEngine
│   ├── locked: boolean
│   └── cvReady: boolean
│
└── Methods
    ├── onCvLoaded()
    ├── showMainMenu()
    ├── onSizeChange()
    ├── onDetectionModeChange()
    ├── onMarkerTypeChange()
    ├── onModelChange()
    ├── updateModels()
    ├── startSession()
    ├── loop()
    ├── drawMarkerFeedback(pose)
    ├── clearMarkerFeedback()
    ├── setupTouch()
    ├── lockView()
    ├── unlockView()
    ├── resetObject()
    ├── startAgain()
    ├── captureImage()
    ├── showMarkerGenerator()
    ├── hideMarkerGenerator()
    ├── generateAprilTag()
    ├── downloadMarker()
    └── printMarker()
```

## File Structure

```
/
├── index.html                    # Main application
├── service-worker.js             # PWA service worker
├── manifest.json                 # PWA manifest
│
├── opencv.js                     # OpenCV.js library (8MB)
├── apriltag.js                   # AprilTag generation library
│
├── src/
│   └── detectors/
│       ├── types.js             # Type definitions (JSDoc)
│       └── apriltagDetector.js  # AprilTag detector implementation
│
├── apriltag-families/
│   ├── 36h11.json               # Most common (587 tags)
│   ├── 25h9.json                # Smaller (35 tags)
│   ├── 16h5.json                # Fastest (30 tags)
│   ├── 36h9.json                # Alternative
│   └── 36h10.json               # Alternative
│
├── icon-192.png                 # PWA icon
├── icon-512.png                 # PWA icon
├── icon.svg                     # Icon source
│
├── README.md                    # Main documentation
├── APRILTAG_DETECTION.md        # AprilTag documentation
├── ARCHITECTURE.md              # This file
├── MARKER_GUIDE.md              # Marker usage guide
├── FUTURE_IMPROVEMENTS.md       # Roadmap
├── CHANGELOG.md                 # Version history
└── BUILD_FIX.md                 # Build troubleshooting
```

## Performance Characteristics

### Memory Usage

- OpenCV.js: ~8MB
- Video frame processing: ~2MB (scaled)
- OpenCV Mats: ~1MB (reused)
- AprilTag detector: ~500KB
- Total: ~12MB runtime memory

### Processing Speed

- ArUco detection: ~5-10ms per frame
- AprilTag detection: ~10-20ms per frame
- Pose calculation: ~1ms
- 3D rendering: ~5ms
- Total: ~20-40ms per frame (~30fps)

### Scaling Strategy

- Input video: 1280px (ideal)
- Processing: 640px (0.5x scale)
- Output: Full screen resolution

## Browser Compatibility

### Required Features

- WebRTC (camera access)
- WebGL (3D rendering)
- Async/Await (ES2017)
- Arrow functions (ES6)
- Promise API
- Canvas API
- Web Workers (future)

### Tested Browsers

- ✅ Chrome 90+ (Desktop/Mobile)
- ✅ Safari 14+ (iOS/macOS)
- ✅ Firefox 88+ (Desktop/Mobile)
- ✅ Edge 90+ (Desktop/Mobile)
- ❌ IE 11 (not supported)

## Deployment

### Static Hosting (Current)

- No build process required
- Pure client-side application
- Can be served from any static host:
  - GitHub Pages
  - Cloudflare Pages
  - Netlify
  - Local web server

### PWA Installation

1. Browser prompts user to install
2. Service worker caches all assets
3. Works offline after first load
4. App icon on home screen
5. Fullscreen experience

## Future Architecture Plans

### 1. WebAssembly AprilTag Decoder

```
C++ AprilTag Library
    ↓
Compile to WASM
    ↓
JavaScript Wrapper
    ↓
Use in AprilTagDetector
```

### 2. Web Workers for Detection

```
Main Thread          Worker Thread
    │                     │
    ├──Send frame───────>│
    │                     ├─Detect markers
    │                     ├─Calculate pose
    │<──Return pose───────┤
    │                     │
    ├──Render graphics    │
```

### 3. Custom OpenCV.js Build

```
OpenCV Source
    ├─Core modules
    ├─ArUco module
    ├─AprilTag module (add)
    └─Compile to JS/WASM
        ↓
    Smaller bundle size
    Full AprilTag support
```

## Security Considerations

- ✅ No external API calls
- ✅ No data transmission
- ✅ Camera permission required
- ✅ Local processing only
- ✅ No cookies or tracking
- ✅ CSP compatible
- ✅ HTTPS recommended

## Accessibility

- Keyboard navigation (limited - AR app)
- Screen reader labels
- High contrast UI
- Touch-friendly controls
- Error messages

## Debugging

### Browser Console Messages

```
"OpenCV loaded from local file"
"OpenCV Ready"
"ArUco detector initialized"
"AprilTag detector initialized"
"Detected N markers: IDs [...]"
"✓ Tracking" / "Looking..."
```

### Error Messages

```
"OpenCV failed to initialize"
"AprilTag detector initialization failed"
"ArUco detection error"
"Camera access denied"
```

### Performance Monitoring

Use browser DevTools:
- Performance tab (frame rate)
- Memory tab (heap usage)
- Network tab (asset loading)
- Console (detection stats)
