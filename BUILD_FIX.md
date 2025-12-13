# Build Fix: Python Dependency Issue Resolved

## Problem

The Cloudflare Pages build was failing with this error:
```
RuntimeError: CMake must be installed to build the following extensions: apriltags
ERROR: Failed building wheel for apriltag
```

## Root Cause

1. Cloudflare Pages automatically detects `requirements.txt` in the root directory
2. It attempts to install Python dependencies during the build process
3. The `apriltag>=0.0.16` package requires CMake to compile native extensions
4. CMake is not available in the Cloudflare Pages build environment

## Solution

The fix recognizes that **this is a static Progressive Web App (PWA) that runs entirely in the browser using JavaScript**. The Python code was for optional development/research purposes and is not needed for the web application to function.

### Changes Made

1. **Moved Python code to `python-dev/` subdirectory**
   - `requirements.txt` → `python-dev/requirements.txt`
   - `vio/` → `python-dev/vio/`
   - `main.py` → `python-dev/main.py`
   - All Python-related files moved to the new directory

2. **Created `.cfignore`** to exclude Python code from Cloudflare Pages deployment

3. **Updated documentation**
   - Main `README.md` clarifies Python code is optional
   - Created `python-dev/README.md` with installation instructions for developers

### Result

- ✅ No `requirements.txt` in root directory = no automatic Python dependency installation
- ✅ Web application files remain in root for proper deployment
- ✅ Python development code still available for developers who want to use it
- ✅ Build process will now succeed as it only needs to serve static files

## Web Application Requirements

The Clearance Wizard web application only needs:
- Static file serving (HTML, CSS, JavaScript)
- No build process required
- No Python or other server-side dependencies
- Runs entirely in the browser using:
  - JavaScript for logic
  - OpenCV.js for computer vision
  - PWA technology for offline capabilities

## For Developers

If you want to use the Python VIO (Visual-Inertial Odometry) code for development:

1. Install system dependencies (CMake, Python 3.7+)
2. Navigate to `python-dev/` directory
3. Run `pip install -r requirements.txt`

See `python-dev/README.md` for detailed instructions.

## Verification

To verify this fix works:
1. Deploy to Cloudflare Pages
2. Build should succeed as it no longer attempts to install Python dependencies
3. Web application should function normally (it never needed Python anyway)

## Technical Notes

This approach follows best practices for:
- **Separation of concerns**: Development tools separate from production deployment
- **Minimal dependencies**: Only deploy what's needed to run the application
- **Clear documentation**: Developers know what's required and what's optional
- **Build optimization**: Faster builds with fewer unnecessary steps
