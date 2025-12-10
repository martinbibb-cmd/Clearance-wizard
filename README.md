# Clearance-wizard

An AR-based clearance checking tool for boilers, radiators, and other appliances using ArUco markers.

## Setup Instructions

### Quick Start (Online Mode)

The application now automatically loads OpenCV.js from a CDN, so you can run it immediately without any additional setup:

### Optional: Download OpenCV.js for Offline Use

For offline operation or better performance, you can optionally download OpenCV.js locally:

1. Download the OpenCV.js file from: https://docs.opencv.org/4.5.2/opencv.js
2. Save the file as `opencv.js` in the same directory as `index.html`
3. The app will automatically detect and use the local copy instead of the CDN

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

- AR-based clearance visualization using ArUco markers
- Support for multiple appliance types (boilers, radiators, cylinders, flues)
- Custom marker and appliance sizing
- Real-time camera tracking and overlay

## ArUco Markers

This application uses ArUco markers for AR tracking. You need to have pre-printed markers to use the app.

**How to get markers:**

1. **Download pre-generated markers**: You can download a PDF with ArUco markers from various online sources
2. **Generate markers yourself**: Use Python with OpenCV to generate markers from the DICT_4X4_50 dictionary (IDs 0-49)
3. **Online generators**: Search for "ArUco marker generator DICT_4X4_50" online

**Recommended marker sizes:**
- 43mm (credit card size) - Most portable
- 53mm - Good balance
- 160mm or larger - Better detection at distance

Print the markers on white paper with a black printer for best results.

## Troubleshooting

If you see "Loading OpenCV..." or initialization errors:

1. **Check your internet connection** - The app will load OpenCV.js from CDN if no local copy is found
2. Make sure you're running the app through a local web server (not opening the HTML file directly)
3. Check your browser console (F12) for detailed error messages
4. Ensure your browser supports WebRTC and camera access
5. If using offline, ensure `opencv.js` is downloaded and placed in the project root directory

## Browser Compatibility

- Requires a modern browser with WebRTC support (Chrome, Firefox, Safari, Edge)
- Camera access is required for AR functionality
- Works best on mobile devices with rear-facing cameras