#!/usr/bin/env python3
"""
Visual-Inertial Odometry Main Application

This script demonstrates the VIO system by simulating synced image and IMU data,
performing AprilTag detection, IMU pre-integration, and EKF fusion to estimate
the globally-referenced 3D pose.
"""

import numpy as np
from scipy.spatial.transform import Rotation
import time
from typing import Optional

try:
    import cv2
except ImportError:
    print("Warning: OpenCV not installed. Image visualization will be disabled.")
    cv2 = None

from vio import AprilTagDetector, IMUProcessor, EKFFusionEngine


class VIOSystem:
    """
    Complete Visual-Inertial Odometry System.
    
    This class integrates the AprilTag detector, IMU processor, and EKF fusion
    engine to provide robust 3D pose estimation.
    
    Parameters
    ----------
    tag_size : float
        Physical size of AprilTag markers in meters.
    camera_matrix : np.ndarray
        3x3 camera intrinsic matrix.
    dist_coeffs : np.ndarray
        Camera distortion coefficients.
    tag_family : str, optional
        AprilTag family to detect. Default is 'tagStandard41h12'.
    """
    
    def __init__(
        self,
        tag_size: float,
        camera_matrix: np.ndarray,
        dist_coeffs: np.ndarray,
        tag_family: str = 'tagStandard41h12'
    ):
        """Initialize the VIO system."""
        # Initialize components
        self.detector = AprilTagDetector(
            tag_size=tag_size,
            camera_matrix=camera_matrix,
            dist_coeffs=dist_coeffs,
            tag_family=tag_family
        )
        
        self.imu_processor = IMUProcessor()
        self.ekf = EKFFusionEngine()
        
        # Timing
        self.last_frame_time = None
        self.frame_count = 0
        
        print("VIO System initialized")
        print(f"  Tag size: {tag_size}m")
        print(f"  Tag family: {tag_family}")
    
    def process_frame(
        self,
        image: np.ndarray,
        timestamp: float,
        gyro_measurements: list,
        accel_measurements: list,
        visualize: bool = True
    ) -> Optional[dict]:
        """
        Process a single frame with synchronized IMU data.
        
        Parameters
        ----------
        image : np.ndarray
            Input image frame.
        timestamp : float
            Frame timestamp in seconds.
        gyro_measurements : list
            List of (timestamp, gyro_reading) tuples since last frame.
        accel_measurements : list
            List of (timestamp, accel_reading) tuples since last frame.
        visualize : bool, optional
            Whether to visualize detections. Default is True.
        
        Returns
        -------
        Optional[dict]
            Dictionary containing pose estimate, or None if tracking failed.
        """
        self.frame_count += 1
        
        # Step 1: IMU Prediction
        if self.last_frame_time is not None and len(gyro_measurements) > 0:
            # Get current orientation estimate
            state = self.ekf.get_state()
            current_rotation = state['orientation']
            
            # Pre-integrate IMU measurements
            delta_pos, delta_vel, delta_rot = self.imu_processor.preintegrate(
                gyro_measurements,
                accel_measurements,
                initial_rotation=current_rotation
            )
            
            dt = timestamp - self.last_frame_time
            
            # EKF Prediction step
            self.ekf.predict(delta_pos, delta_vel, delta_rot, dt)
            
            print(f"Frame {self.frame_count}: IMU prediction - "
                  f"Δpos: {np.linalg.norm(delta_pos):.3f}m, "
                  f"Δvel: {np.linalg.norm(delta_vel):.3f}m/s")
        
        # Step 2: AprilTag Detection
        detections = self.detector.detect(image)
        
        if len(detections) > 0:
            print(f"  Detected {len(detections)} AprilTag(s)")
            
            # Use the first detected tag for measurement update
            # In a real system, might use multiple tags or select best quality
            detection = detections[0]
            
            measured_position = detection['translation']
            measured_rotation = Rotation.from_matrix(detection['rotation_matrix'])
            
            # EKF Update step
            self.ekf.update(measured_position, measured_rotation)
            
            print(f"  Tag {detection['tag_id']}: Updated pose estimate")
            
            # Visualize if requested
            if visualize and cv2 is not None:
                vis_image = self.detector.visualize_detections(image, detections)
                cv2.imshow('VIO System - AprilTag Detection', vis_image)
                cv2.waitKey(1)
        else:
            print(f"  No AprilTags detected - using IMU prediction only")
        
        # Get current state estimate
        state = self.ekf.get_state()
        position = state['position']
        uncertainty = self.ekf.get_position_uncertainty()
        
        print(f"  Estimated pose: X={position[0]:.3f}m, "
              f"Y={position[1]:.3f}m, Z={position[2]:.3f}m "
              f"(±{uncertainty:.3f}m)")
        print()
        
        self.last_frame_time = timestamp
        
        return {
            'position': position,
            'velocity': state['velocity'],
            'orientation': state['orientation'],
            'quaternion': state['quaternion'],
            'uncertainty': uncertainty,
            'detections': len(detections),
            'timestamp': timestamp
        }
    
    def get_current_pose(self) -> dict:
        """Get the current pose estimate."""
        return self.ekf.get_state()
    
    def reset(self):
        """Reset the VIO system."""
        self.ekf.reset()
        self.imu_processor.reset_integration()
        self.last_frame_time = None
        self.frame_count = 0
        print("VIO System reset")


def simulate_vio_system():
    """
    Simulate the VIO system with synthetic data.
    
    This function demonstrates the main application loop by generating
    synthetic AprilTag images and IMU data, then processing them through
    the VIO pipeline.
    """
    print("=" * 60)
    print("Visual-Inertial Odometry Simulation")
    print("=" * 60)
    print()
    
    # Camera parameters (simulated)
    image_width, image_height = 640, 480
    camera_matrix = AprilTagDetector.create_default_camera_matrix(
        image_width, image_height, fov_degrees=60.0
    )
    dist_coeffs = np.zeros(5)  # No distortion
    
    # AprilTag parameters
    tag_size = 0.19  # 190mm
    
    # Initialize VIO system
    try:
        vio = VIOSystem(
            tag_size=tag_size,
            camera_matrix=camera_matrix,
            dist_coeffs=dist_coeffs,
            tag_family='tagStandard41h12'
        )
    except ImportError as e:
        print(f"Error: {e}")
        print("\nTo run this simulation, install required packages:")
        print("  pip install apriltag opencv-python numpy scipy")
        return
    
    # Simulation parameters
    fps = 30  # Camera frame rate
    imu_rate = 200  # IMU sampling rate (Hz)
    duration = 5.0  # Simulation duration (seconds)
    
    print(f"Simulation parameters:")
    print(f"  Camera: {fps} fps, {image_width}x{image_height}")
    print(f"  IMU: {imu_rate} Hz")
    print(f"  Duration: {duration}s")
    print()
    
    # Generate synthetic AprilTag image
    # In a real system, this would come from a camera
    print("Note: This simulation uses synthetic data.")
    print("For real AprilTag detection, capture images with actual tags.")
    print()
    
    # Simulate frames
    frame_interval = 1.0 / fps
    imu_interval = 1.0 / imu_rate
    
    for frame_idx in range(int(duration * fps)):
        timestamp = frame_idx * frame_interval
        
        # Generate synthetic image (blank for demonstration)
        # In a real system, capture from camera
        image = np.ones((image_height, image_width, 3), dtype=np.uint8) * 255
        
        # Generate IMU data for this frame period
        gyro_measurements = []
        accel_measurements = []
        
        # Simulate IMU samples between frames
        imu_samples = int(frame_interval / imu_interval)
        for i in range(imu_samples):
            t = timestamp - frame_interval + i * imu_interval
            
            # Simulated IMU data (stationary with noise)
            gyro = np.random.randn(3) * 0.01  # Small noise
            accel = np.array([0, 0, 9.81]) + np.random.randn(3) * 0.1
            
            gyro_measurements.append((t, gyro))
            accel_measurements.append((t, accel))
        
        # Process frame
        result = vio.process_frame(
            image,
            timestamp,
            gyro_measurements,
            accel_measurements,
            visualize=False  # Disable visualization for synthetic data
        )
        
        # Small delay to make output readable
        time.sleep(0.1)
    
    print("=" * 60)
    print("Simulation complete!")
    print()
    print("Final pose estimate:")
    final_state = vio.get_current_pose()
    print(f"  Position: {final_state['position']}")
    print(f"  Velocity: {final_state['velocity']}")
    print(f"  Orientation (quat): {final_state['quaternion']}")
    print()
    print("To use with real data:")
    print("  1. Calibrate your camera")
    print("  2. Print AprilTag markers (e.g., tag36h11 family)")
    print("  3. Capture images and IMU data")
    print("  4. Replace synthetic data with real sensor data")
    print("=" * 60)


def main():
    """Main entry point."""
    print(__doc__)
    
    # Check if running with real data or simulation
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Usage:")
        print("  python main.py              Run simulation with synthetic data")
        print("  python main.py --help       Show this help message")
        print()
        print("For real-world usage, modify the main() function to:")
        print("  - Capture images from camera")
        print("  - Read IMU data from sensor")
        print("  - Use calibrated camera parameters")
        return
    
    # Run simulation
    simulate_vio_system()


if __name__ == '__main__':
    main()
