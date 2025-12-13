"""
IMU Processor Module

This module provides the IMUProcessor class for IMU pre-integration between
image frames in a Visual-Inertial Odometry system.
"""

import numpy as np
from scipy.spatial.transform import Rotation
from typing import List, Tuple, Optional


class IMUProcessor:
    """
    Implements IMU Pre-integration for Visual-Inertial Odometry.
    
    This class takes high-frequency accelerometer and gyroscope readings and
    calculates the relative change in position, velocity, and orientation
    between two image frames. Includes basic bias subtraction.
    
    Parameters
    ----------
    gyro_bias : np.ndarray, optional
        Initial gyroscope bias (3D vector). Default is zeros.
    accel_bias : np.ndarray, optional
        Initial accelerometer bias (3D vector). Default is zeros.
    gravity : np.ndarray, optional
        Gravity vector in world frame. Default is [0, 0, -9.81] m/s^2.
    
    Attributes
    ----------
    gyro_bias : np.ndarray
        Current gyroscope bias estimate (rad/s).
    accel_bias : np.ndarray
        Current accelerometer bias estimate (m/s^2).
    gravity : np.ndarray
        Gravity vector in world frame (m/s^2).
    """
    
    def __init__(
        self,
        gyro_bias: Optional[np.ndarray] = None,
        accel_bias: Optional[np.ndarray] = None,
        gravity: Optional[np.ndarray] = None
    ):
        """Initialize the IMU processor with bias estimates."""
        self.gyro_bias = gyro_bias if gyro_bias is not None else np.zeros(3)
        self.accel_bias = accel_bias if accel_bias is not None else np.zeros(3)
        self.gravity = gravity if gravity is not None else np.array([0.0, 0.0, -9.81])
        
        # Integration state
        self.reset_integration()
    
    def reset_integration(self):
        """Reset the pre-integration state."""
        self.delta_position = np.zeros(3)
        self.delta_velocity = np.zeros(3)
        self.delta_rotation = Rotation.identity()
        self.dt_total = 0.0
    
    def preintegrate(
        self,
        gyro_measurements: List[Tuple[float, np.ndarray]],
        accel_measurements: List[Tuple[float, np.ndarray]],
        initial_rotation: Optional[Rotation] = None
    ) -> Tuple[np.ndarray, np.ndarray, Rotation]:
        """
        Perform IMU pre-integration between two image frames.
        
        This method integrates a sequence of IMU measurements to compute the
        relative change in position, velocity, and orientation. The integration
        is performed in the body frame and then transformed to the world frame.
        
        Parameters
        ----------
        gyro_measurements : List[Tuple[float, np.ndarray]]
            List of (timestamp, gyroscope_reading) tuples.
            Gyroscope readings in rad/s (3D vector).
        accel_measurements : List[Tuple[float, np.ndarray]]
            List of (timestamp, accelerometer_reading) tuples.
            Accelerometer readings in m/s^2 (3D vector).
        initial_rotation : Rotation, optional
            Initial orientation for the integration period.
            If None, uses identity (world frame aligned with body frame).
        
        Returns
        -------
        Tuple[np.ndarray, np.ndarray, Rotation]
            Tuple containing:
            - delta_position: 3D position change (meters)
            - delta_velocity: 3D velocity change (m/s)
            - delta_rotation: Rotation object representing orientation change
        
        Notes
        -----
        This is a simplified pre-integration that assumes:
        1. Linear interpolation between IMU samples
        2. Constant bias during the integration period
        3. Small rotation angles for linearization
        
        For production systems, consider using more sophisticated methods like
        the Forster et al. (2017) pre-integration framework.
        """
        self.reset_integration()
        
        if initial_rotation is None:
            initial_rotation = Rotation.identity()
        
        current_rotation = initial_rotation
        
        # Sort measurements by timestamp
        gyro_measurements = sorted(gyro_measurements, key=lambda x: x[0])
        accel_measurements = sorted(accel_measurements, key=lambda x: x[0])
        
        # Interpolate and integrate
        gyro_idx = 0
        accel_idx = 0
        
        while gyro_idx < len(gyro_measurements) - 1 and accel_idx < len(accel_measurements) - 1:
            # Get current measurements
            t_gyro, gyro = gyro_measurements[gyro_idx]
            t_accel, accel = accel_measurements[accel_idx]
            
            # Determine next timestamp
            t_gyro_next = gyro_measurements[gyro_idx + 1][0]
            t_accel_next = accel_measurements[accel_idx + 1][0]
            t_next = min(t_gyro_next, t_accel_next)
            
            # Time step
            dt = t_next - min(t_gyro, t_accel)
            
            if dt <= 0:
                # Skip invalid time steps
                if t_gyro_next <= t_accel_next:
                    gyro_idx += 1
                else:
                    accel_idx += 1
                continue
            
            # Apply bias correction
            gyro_corrected = gyro - self.gyro_bias
            accel_corrected = accel - self.accel_bias
            
            # Integrate rotation (using small angle approximation)
            # For better accuracy, use exponential map: exp(omega * dt)
            delta_angle = gyro_corrected * dt
            delta_rot = Rotation.from_rotvec(delta_angle)
            current_rotation = current_rotation * delta_rot
            
            # Transform acceleration to world frame and subtract gravity
            accel_world = current_rotation.apply(accel_corrected) - self.gravity
            
            # Integrate velocity
            self.delta_velocity += accel_world * dt
            
            # Integrate position (using midpoint method for better accuracy)
            self.delta_position += self.delta_velocity * dt + 0.5 * accel_world * dt * dt
            
            self.dt_total += dt
            
            # Move to next measurements
            if t_gyro_next <= t_accel_next:
                gyro_idx += 1
            else:
                accel_idx += 1
        
        # Store final rotation change
        self.delta_rotation = initial_rotation.inv() * current_rotation
        
        return self.delta_position, self.delta_velocity, self.delta_rotation
    
    def update_bias(self, gyro_bias: np.ndarray, accel_bias: np.ndarray):
        """
        Update IMU bias estimates.
        
        Parameters
        ----------
        gyro_bias : np.ndarray
            New gyroscope bias (3D vector, rad/s).
        accel_bias : np.ndarray
            New accelerometer bias (3D vector, m/s^2).
        """
        self.gyro_bias = gyro_bias.copy()
        self.accel_bias = accel_bias.copy()
    
    def get_bias(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get current IMU bias estimates.
        
        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Tuple of (gyro_bias, accel_bias).
        """
        return self.gyro_bias.copy(), self.accel_bias.copy()
    
    @staticmethod
    def simulate_imu_data(
        duration: float,
        frequency: float = 200.0,
        motion_type: str = 'stationary'
    ) -> Tuple[List[Tuple[float, np.ndarray]], List[Tuple[float, np.ndarray]]]:
        """
        Generate simulated IMU data for testing.
        
        Parameters
        ----------
        duration : float
            Duration of simulation in seconds.
        frequency : float, optional
            IMU sampling frequency in Hz. Default is 200 Hz.
        motion_type : str, optional
            Type of motion to simulate. Options:
            - 'stationary': No motion, only noise
            - 'linear': Constant velocity motion
            - 'circular': Circular motion
        
        Returns
        -------
        Tuple[List[Tuple[float, np.ndarray]], List[Tuple[float, np.ndarray]]]
            Tuple of (gyro_measurements, accel_measurements).
        """
        dt = 1.0 / frequency
        timestamps = np.arange(0, duration, dt)
        
        gyro_measurements = []
        accel_measurements = []
        
        # Noise parameters
        gyro_noise_std = 0.01  # rad/s
        accel_noise_std = 0.1  # m/s^2
        
        for t in timestamps:
            if motion_type == 'stationary':
                # Only noise and gravity
                gyro = np.random.randn(3) * gyro_noise_std
                accel = np.array([0, 0, 9.81]) + np.random.randn(3) * accel_noise_std
            
            elif motion_type == 'linear':
                # Constant velocity in x direction
                gyro = np.random.randn(3) * gyro_noise_std
                accel = np.array([0.5, 0, 9.81]) + np.random.randn(3) * accel_noise_std
            
            elif motion_type == 'circular':
                # Circular motion in XY plane
                omega = 0.5  # rad/s
                radius = 1.0  # meters
                
                # Angular velocity (constant around Z axis)
                gyro = np.array([0, 0, omega]) + np.random.randn(3) * gyro_noise_std
                
                # Centripetal acceleration
                centripetal = omega**2 * radius
                angle = omega * t
                accel = np.array([
                    -centripetal * np.cos(angle),
                    -centripetal * np.sin(angle),
                    9.81
                ]) + np.random.randn(3) * accel_noise_std
            
            else:
                raise ValueError(f"Unknown motion type: {motion_type}")
            
            gyro_measurements.append((t, gyro))
            accel_measurements.append((t, accel))
        
        return gyro_measurements, accel_measurements
    
    def get_integration_info(self) -> dict:
        """
        Get information about the last integration.
        
        Returns
        -------
        dict
            Dictionary containing:
            - 'delta_position': Position change (meters)
            - 'delta_velocity': Velocity change (m/s)
            - 'delta_rotation': Rotation change (as quaternion)
            - 'total_time': Total integration time (seconds)
        """
        return {
            'delta_position': self.delta_position.copy(),
            'delta_velocity': self.delta_velocity.copy(),
            'delta_rotation': self.delta_rotation.as_quat(),
            'total_time': self.dt_total
        }
