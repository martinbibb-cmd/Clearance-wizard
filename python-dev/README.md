# Python Development Code

This directory contains Python development code for Visual-Inertial Odometry (VIO) research and backend development. **This code is NOT required for the main Clearance Wizard web application**, which runs entirely in the browser using JavaScript.

## Contents

- **vio/** - Python implementation of Visual-Inertial Odometry system
  - `apriltag_detector.py` - AprilTag detection and pose estimation
  - `imu_processor.py` - IMU data pre-integration
  - `ekf_fusion_engine.py` - Extended Kalman Filter for sensor fusion
- **main.py** - Example VIO system demonstration
- **test_apriltag_detector.py** - Unit tests for AprilTag detector
- **example_apriltag_usage.py** - Usage examples
- **requirements.txt** - Python dependencies for this code

## Purpose

The Python VIO code serves as:
1. Research and development for future mobile app features
2. Backend processing capabilities (if needed)
3. Reference implementation for understanding VIO algorithms
4. Testing and validation tools

## Installation (Optional)

**Note:** You only need to install these dependencies if you want to run or develop the Python VIO code. The main web application works without any Python installation.

### Prerequisites

- Python 3.7 or higher
- CMake (required for building the `apriltag` package)

### System Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install cmake python3-dev
```

#### macOS
```bash
brew install cmake
```

#### Windows
Download and install CMake from: https://cmake.org/download/

### Python Dependencies

After installing system dependencies:

```bash
cd python-dev
pip install -r requirements.txt
```

### Troubleshooting

If you have trouble installing the `apriltag` library, see the detailed installation instructions in `README_VIO.md`.

## Running the Code

### Quick Test
```bash
cd python-dev
python main.py
```

### Running Tests
```bash
cd python-dev
python test_apriltag_detector.py
```

## Documentation

See `README_VIO.md` for comprehensive documentation on the VIO system, including:
- Architecture overview
- API reference
- Usage examples
- Configuration guide
- Performance considerations

## Web Application

The main Clearance Wizard web application is in the parent directory and uses:
- **JavaScript** for all logic
- **OpenCV.js** for computer vision (ArUco marker detection)
- **PWA technology** for offline capabilities
- No Python dependencies required

To run the web application, see the main README.md in the parent directory.
