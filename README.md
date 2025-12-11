# Clearance-wizard

An AR-based clearance checking tool for boilers, radiators, and other appliances using ArUco markers.

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

This application uses ArUco marker detection for AR tracking. ArUco markers are square black and white patterns that provide precise pose estimation.

### Marker Modes

The app supports two marker detection modes:

#### 1. **Single Marker Mode (Quick Setup)**
- Use **any ArUco marker** (DICT_4X4_50 format)
- Best for quick measurements and single-person setup
- Position one marker near the appliance location
- Fastest setup time

#### 2. **4-Marker Mode (More Accurate)**
- Use **4 ArUco markers with IDs 1, 2, 3, and 4**
- Provides enhanced accuracy through averaging multiple marker positions
- Position markers around the appliance area
- More stable tracking, especially at distance
- Recommended for final documentation

### How to Get ArUco Markers

1. **Download pre-generated markers**: Visit [arucogen](https://chev.me/arucogen/)
   - Select dictionary: `DICT_4X4_50`
   - For single marker mode: Download any ID
   - For 4-marker mode: Download markers with IDs 1, 2, 3, and 4
   
2. **Print markers**: Print on white paper with a laser printer for best results

### Recommended Marker Sizes

- 45mm - Default setting (small marker)
- 53mm (credit card size) - Good for close-up work
- 148mm (A5 square) - **Recommended for better tracking**
- 160mm-190mm (A4 sizes) - **Best for distant measurements**

**Why larger markers work better:**
Larger markers (A5 or A4) provide significantly more stable tracking, especially when stepping back from the installation point. The increased pixel coverage gives the computer vision system more data to work with, reducing "jumping" or instability in the AR overlay at distance.

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