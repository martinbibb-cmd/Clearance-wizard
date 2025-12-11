# Clearance-wizard

An AR-based clearance checking tool for boilers, radiators, and other appliances using ArUco markers.

## Pro 4-Marker Version

This is the **Pro Mini-App** version featuring:
- **Simplified workflow**: Single-button start with no configuration needed
- **4-Marker support**: Uses ArUco markers with IDs 1-4 for multi-marker tracking
- **Fixed 90mm markers**: Optimized for consistent marker size
- **Worcester 4000 boiler**: Pre-configured for 724mm tall boiler (400x724x310mm)
- **Direct pose estimation**: Uses basic pinhole camera math for fast tracking

### ArUco Module Requirement

⚠️ **Important**: This Pro version requires OpenCV.js compiled with ArUco module support. The standard OpenCV.js build does not include ArUco by default.

To use this version:
1. Download or build OpenCV.js with ArUco module enabled
2. Replace the `opencv.js` file in this repository with the ArUco-enabled version
3. Alternatively, use the [OpenCV.js builder tool](https://docs.opencv.org/4.x/d4/da1/tutorial_js_setup.html) to create a custom build

If ArUco is not available, the app will display a clear error message on startup.

## Setup Instructions

### Quick Start

The application includes a standard OpenCV.js file. For the Pro 4-Marker features, you'll need to replace it with an ArUco-enabled build.

### Running the Application

Since this application uses camera access and loads local files, you need to serve it through a local web server:

```bash
# Using Python 3
python -m http.server 8000

# Or using Python 2
python -m SimpleHTTPServer 8000

# Or using Node.js
npx http-server -p 8000
```

Then open your browser and navigate to:
```
http://localhost:8000
```

## Features

- **Progressive Web App (PWA)**: Install on your device for offline access and app-like experience
- **Pro 4-Marker System**: Simplified ArUco-based multi-marker tracking
- **Worcester 4000 Focus**: Pre-configured for the popular 724mm tall boiler
- **Fixed 90mm Markers**: Consistent marker size for reliable detection
- **Simple Pinhole Math**: Fast pose estimation without complex calibration
- Real-time camera tracking and 3D wireframe overlay

## Installing as a PWA

### On Android (Chrome/Edge)
1. Open the app in Chrome or Edge browser
2. Tap the menu (⋮) and select "Install app" or "Add to Home screen"
3. The app will be installed and appear in your app drawer
4. Launch it like any other app for a fullscreen experience

### On iOS (Safari)
1. Open the app in Safari
2. Tap the Share button (□ with arrow)
3. Scroll down and tap "Add to Home Screen"
4. Tap "Add" to confirm
5. The app icon will appear on your home screen

### Benefits of Installing
- **Offline access**: Use the app without an internet connection (after first load)
- **Faster loading**: Cached assets load instantly
- **Fullscreen mode**: No browser UI cluttering your view
- **Home screen access**: Launch directly from your device
- **Save to gallery**: Capture and share images directly to your photo gallery

## Marker Requirements

This Pro version uses **ArUco markers** (DICT_4X4_50) for precise marker detection and identification.

**Creating ArUco Markers:**

1. Visit [ArUco Marker Generator](https://chev.me/arucogen/)
2. Select dictionary: **4x4 (50, 100, 250, 1000)**
3. Generate markers with **IDs 1-4**
4. Set marker size to **90mm**
5. Print on white paper with a black printer

**Marker Specifications:**
- **Fixed size**: 90mm × 90mm
- **Dictionary**: DICT_4X4_50
- **IDs needed**: 1, 2, 3, and 4
- **Print quality**: Use high-quality printer for sharp edges

**Why ArUco markers:**
ArUco markers provide unique IDs and better pose estimation compared to generic squares. The Pro version uses these IDs to support multi-marker tracking and more accurate 3D positioning.

## Troubleshooting

### "ArUco Module Not Available" Error

If you see this error:

1. The standard OpenCV.js does not include ArUco support
2. You need to build or download OpenCV.js with ArUco module enabled
3. See the [OpenCV.js documentation](https://docs.opencv.org/4.x/d4/da1/tutorial_js_setup.html) for building custom versions
4. Replace `opencv.js` in this repository with your ArUco-enabled build

### Other Common Issues

If you see "Loading OpenCV..." or other initialization errors:

1. Make sure you're running the app through a local web server (not opening the HTML file directly)
2. Check your browser console (F12) for detailed error messages
3. Ensure your browser supports WebRTC and camera access
4. Ensure `opencv.js` is present in the project root directory

## Browser Compatibility

- Requires a modern browser with WebRTC support (Chrome, Firefox, Safari, Edge)
- Camera access is required for AR functionality
- Works best on mobile devices with rear-facing cameras