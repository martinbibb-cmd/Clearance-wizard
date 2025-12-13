# Project: Clearance Wizard (Visual-Inertial Odometry Upgrade)

## Goal
The primary goal is to upgrade the current camera-based pose estimation system to a highly robust and accurate Visual-Inertial Odometry (VIO) system for 3D measurement. The VIO must use AprilTags as reliable anchors.

## Tech Stack
-   **Core Language:** Python
-   **Vision Library:** OpenCV (for image processing, camera calibration, PnP)
-   **Marker System:** AprilTag (using a robust Python wrapper, e.g., 'apriltag')
-   **IMU/Fusion:** Focus on implementing a **loosely-coupled** VIO system using an **Extended Kalman Filter (EKF)** to fuse IMU data (accelerometer/gyro) and AprilTag pose estimates. This is simpler than a tightly-coupled system.
-   **Deployment Target:** Must be structured for eventual deployment to mobile (e.g., via a Python-to-mobile wrapper or a defined API for data ingestion).

## Guidelines
1.  All code must be well-documented with docstrings (e.g., using NumPy style).
2.  Prioritize using open-source, easily installable libraries.
3.  The system must be modular: separate classes for `IMUProcessor`, `AprilTagDetector`, and `EKFFusionEngine`.

## Architecture

### Core Components

#### AprilTagDetector
- Handles reading images and detecting AprilTags
- Uses tagStandard41h12 family
- Performs PnP (Perspective-n-Point) to return 3D position and orientation
- Returns translation vector and rotation matrix relative to camera
- Assumes camera is already calibrated

#### IMUProcessor
- Implements IMU Pre-integration step
- Takes high-frequency accelerometer and gyroscope readings
- Calculates relative change in position, velocity, and orientation (quaternion)
- Operates between closest image frames
- Includes basic bias subtraction

#### EKFFusionEngine
- Implements Extended Kalman Filter (EKF) approach
- Fuses predicted state from IMUProcessor with measurements from AprilTagDetector
- State vector includes:
  - Position (3D)
  - Velocity (3D)
  - Orientation (Quaternion - 4D)
  - IMU Biases (Gyro & Accel - 6D)
- Provides EKF prediction and update logic

### Main Application Loop
- Simulates reading synced image and IMU data
- Calls IMUProcessor for prediction
- Calls EKFFusionEngine to perform AprilTag measurement update
- Prints resulting globally-referenced 3D pose (X, Y, Z)

## Code Style
- Use NumPy-style docstrings for all classes and methods
- Follow PEP 8 conventions
- Use type hints for function signatures
- Keep functions focused and modular
- Include comprehensive error handling
- Add inline comments for complex algorithms

## Dependencies
- numpy: Numerical operations
- opencv-python (cv2): Computer vision operations
- apriltag: AprilTag detection library
- scipy: Quaternion operations and linear algebra

## Testing Considerations
- System should handle missing detections gracefully
- IMU data should be validated before integration
- EKF should handle divergence cases
- Provide diagnostic output for debugging

## Future Deployment
- Code should be structured to support mobile deployment
- Consider API interface for data ingestion
- Keep dependencies minimal for cross-platform compatibility
- Document calibration requirements clearly
