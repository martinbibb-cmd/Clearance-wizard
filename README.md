# Clearance-wizard

An AR-based clearance checking tool for boilers, radiators, and other appliances using ArUco markers.

## Setup Instructions

### Step 1: Download OpenCV.js

The application requires the OpenCV.js library to function. You need to download it and place it in the project directory.

1. Download the OpenCV.js file from: https://docs.opencv.org/4.5.2/opencv.js
2. Save the file as `opencv.js` in the same directory as `index.html`

### Step 2: Run the Application

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
- ArUco marker generator for printing
- Real-time camera tracking and overlay

## Troubleshooting

If you see "Loading OpenCV..." or initialization errors:

1. Ensure `opencv.js` is downloaded and placed in the project root directory
2. Make sure you're running the app through a local web server (not opening the HTML file directly)
3. Check your browser console (F12) for detailed error messages
4. Ensure your browser supports WebRTC and camera access

## Browser Compatibility

- Requires a modern browser with WebRTC support (Chrome, Firefox, Safari, Edge)
- Camera access is required for AR functionality
- Works best on mobile devices with rear-facing cameras