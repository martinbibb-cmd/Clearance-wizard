# Clearance Genie 🔥

An AR-based clearance checking tool for boilers, radiators, and other appliances using computer vision markers.

## Recent Updates

- **Improved UI**: Simplified interface with visual icons and collapsible sections
- **Better Detection Feedback**: Visual progress indicators for multi-marker detection
- **Enhanced User Experience**: Less text-heavy, more intuitive navigation

## Future Improvements

See [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) for a comprehensive roadmap including:
- **AprilTag Support**: Upgrade from ArUco to AprilTag for better accuracy and reliability
- **Markerless Detection**: Path toward object recognition without printed markers
- **Enhanced Feedback**: Real-time marker quality indicators
- **Data Export**: Save and share measurement data

## Setup Instructions

### Quick Start

The application now includes OpenCV.js in the repository, so you can run it immediately without any additional downloads.

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
- AR-based clearance visualization using ArUco markers
- Support for multiple appliance types (boilers, radiators, cylinders, flues)
- Custom marker and appliance sizing
- Real-time camera tracking and overlay
- **Direct gallery saving**: Capture images and save directly to your device's photo gallery

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

## Marker Detection

This application uses computer vision (ArUco markers) for precise AR tracking. **See [MARKER_GUIDE.md](MARKER_GUIDE.md) for comprehensive instructions.**

### Quick Start

1. **Download markers** from [ArUco Generator](https://chev.me/arucogen/)
2. **Select dictionary**: DICT_4X4_50
3. **Print size**: 190mm recommended (measure BLACK SQUARE only)
4. **Print on white paper** with black ink

### Recommended Marker Sizes
- 45mm - Close-up work (0.2m - 1m)
- 90mm - Standard installations (0.5m - 2m)
- 148mm (A5) - Better stability (0.5m - 3m) ⭐
- 190mm (A4) - Best for distance (0.7m - 5m) ⭐⭐⭐

**💡 Key Tip:** Larger markers = better tracking stability at distance!  
**📏 Important:** Always measure the BLACK SQUARE AREA ONLY (exclude white border)

For detailed guidance on marker creation, printing, positioning, and troubleshooting, see [MARKER_GUIDE.md](MARKER_GUIDE.md).

## Capturing Images

The app includes an image capture feature with smart saving:

- **On mobile devices with Web Share API support**: Tap the 📷 button to capture the AR view. You can then choose to save the image to your gallery, share it, or cancel.
- **On other devices**: The image will be downloaded automatically to your default downloads folder.

The captured image includes both the camera feed and the AR overlay, showing the complete clearance visualization.

## Troubleshooting

If you see "Loading OpenCV..." or initialization errors:

1. Make sure you're running the app through a local web server (not opening the HTML file directly)
2. Check your browser console (F12) for detailed error messages
3. Ensure your browser supports WebRTC and camera access
4. Ensure `opencv.js` is present in the project root directory (it should be included in the repository)

## Browser Compatibility

- Requires a modern browser with WebRTC support (Chrome, Firefox, Safari, Edge)
- Camera access is required for AR functionality
- Works best on mobile devices with rear-facing cameras

## Roadmap & Future Enhancements

This project has significant potential for improvement. See [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) for detailed implementation guides, including:

### 🥇 Highest Priority: AprilTag Support
The most direct upgrade path is switching from ArUco to **AprilTag** markers:
- **Better accuracy**: More robust pose estimation, especially at steep angles
- **Fewer false positives**: More reliable detection in challenging conditions
- **Industry standard**: Widely used in robotics and autonomous systems

**Implementation options:**
1. JavaScript library (client-side, maintains PWA offline capability)
2. Python server (maximum accuracy, requires backend)
3. Hybrid approach (progressive enhancement)

### 🚀 Next Steps: Enhanced Features
- **Real-time quality feedback**: Distance, angle, lighting indicators
- **In-app marker generation**: Print directly from the app
- **Measurement export**: Save data as JSON/CSV/PDF
- **Better visual feedback**: Progressive indicators for marker detection

### ✨ Future Vision: Markerless Detection
Long-term goal of eliminating markers entirely:
- **Object Detection (YOLO)**: Recognize appliances directly from camera
- **Depth Sensors**: Use iPhone LiDAR or Intel RealSense for 3D measurements
- **Structure from Motion**: Build 3D models from camera movement

### 📚 For Developers
See [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) for:
- Code examples and implementation guides
- Performance optimization strategies
- Technical comparison of different approaches
- Learning resources and tutorials

### 💡 Contribute
Interested in implementing any of these improvements? Open an issue or PR on GitHub!