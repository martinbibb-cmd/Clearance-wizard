"""
VIO (Visual-Inertial Odometry) Module

This package provides a loosely-coupled Visual-Inertial Odometry system
that fuses AprilTag visual measurements with IMU data using an Extended
Kalman Filter.

Components:
    - AprilTagDetector: Detects AprilTags and estimates their 3D pose
    - IMUProcessor: Pre-integrates IMU measurements between image frames
    - EKFFusionEngine: Fuses IMU and visual data using an Extended Kalman Filter
"""

from .apriltag_detector import AprilTagDetector
from .imu_processor import IMUProcessor
from .ekf_fusion_engine import EKFFusionEngine

__version__ = '0.1.0'
__all__ = ['AprilTagDetector', 'IMUProcessor', 'EKFFusionEngine']
