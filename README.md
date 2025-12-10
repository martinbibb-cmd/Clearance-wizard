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

1. Make sure you're running the app through a local web server (not opening the HTML file directly)
2. Check your browser console (F12) for detailed error messages
3. Ensure your browser supports WebRTC and camera access
4. Ensure `opencv.js` is present in the project root directory (it should be included in the repository)

## Browser Compatibility

- Requires a modern browser with WebRTC support (Chrome, Firefox, Safari, Edge)
- Camera access is required for AR functionality
- Works best on mobile devices with rear-facing cameras