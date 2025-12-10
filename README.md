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
http://localhost:8000              # AR Clearance Tool
http://localhost:8000/voice-notes.html  # Voice-to-Notes PWA
```

## Features

### AR Clearance Tool (`index.html`)
- AR-based clearance visualization using ArUco markers
- Support for multiple appliance types (boilers, radiators, cylinders, flues)
- Custom marker and appliance sizing
- ArUco marker generator for printing
- Real-time camera tracking and overlay

### Voice-to-Notes PWA (`voice-notes.html`)
- Voice recognition using Web Speech API
- Real-time speech-to-text transcription
- Automatic categorization into Engineer and Customer summaries
- Offline support via Service Worker
- Can be installed as a Progressive Web App (PWA)
- Works on mobile and desktop browsers with microphone access

## Using Voice-to-Notes

1. Open `voice-notes.html` in your browser
2. Click the "🎙️ Start Recording" button
3. Allow microphone access when prompted
4. Speak your notes - they will appear in real-time in the "Raw Transcript" box
5. Click "🛑 Stop Recording & Summarize" when finished
6. View the automatically categorized notes in:
   - **Engineer's Summary (Blue)**: Technical details and specifications
   - **Customer Summary (Green)**: Customer-friendly explanations

### Customizing Categorization

Edit the `categorizeAndSummarize()` function in `app.js` to add your own keywords and categorization logic. For example:

```javascript
if (lowerText.includes("your keyword")) {
    engineerNotes.push("Your custom note here");
}
```

## Troubleshooting

If you see "Loading OpenCV..." or initialization errors:

1. Ensure `opencv.js` is downloaded and placed in the project root directory
2. Make sure you're running the app through a local web server (not opening the HTML file directly)
3. Check your browser console (F12) for detailed error messages
4. Ensure your browser supports WebRTC and camera access

## Browser Compatibility

### AR Clearance Tool
- Requires a modern browser with WebRTC support (Chrome, Firefox, Safari, Edge)
- Camera access is required for AR functionality
- Works best on mobile devices with rear-facing cameras

### Voice-to-Notes PWA
- Requires Web Speech API support (Chrome, Edge, Safari 14.1+)
- Microphone access required for voice recording
- Best experience on Chrome/Edge (continuous recognition)
- Can be installed as a PWA on supported devices