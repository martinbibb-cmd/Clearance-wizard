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

## Marker Detection

This application uses computer vision to detect square markers for AR tracking. You need to have a printed square marker (ideally black on white background) to use the app.

**How to create markers:**

1. **Print a simple square**: Any black square on white paper will work
2. **Use QR codes**: QR codes work well as they're already square
3. **Create a custom pattern**: Draw or print any high-contrast square shape

**Recommended marker sizes:**
- 45mm - Default setting (small marker)
- 53mm (credit card size) - Good for close-up work
- 148mm (A5 square) - **Recommended for better tracking**
- 160mm-190mm (A4 sizes) - **Best for distant measurements**

**Why larger markers work better:**
Larger markers (A5 or A4) provide significantly more stable tracking, especially when stepping back from the installation point. The increased pixel coverage gives the computer vision system more data to work with, reducing "jumping" or instability in the AR overlay at distance.

Print the markers on white paper with a black printer for best results. The app detects the square shape using contour detection.

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