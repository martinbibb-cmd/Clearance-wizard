"""
EKF Fusion Engine Module

This module provides the EKFFusionEngine class that implements an Extended
Kalman Filter for fusing IMU pre-integration and AprilTag pose measurements
in a loosely-coupled Visual-Inertial Odometry system.
"""

import numpy as np
from scipy.spatial.transform import Rotation
from typing import Tuple, Optional


class EKFFusionEngine:
    """
    Extended Kalman Filter for Visual-Inertial Odometry fusion.
    
    This class implements a loosely-coupled EKF that fuses IMU pre-integration
    predictions with AprilTag pose measurements. The state vector includes
    position, velocity, orientation, and IMU biases.
    
    State Vector (16D):
    - Position (3D): [px, py, pz]
    - Velocity (3D): [vx, vy, vz]
    - Orientation (Quaternion 4D): [qw, qx, qy, qz]
    - Gyroscope Bias (3D): [bgx, bgy, bgz]
    - Accelerometer Bias (3D): [bax, bay, baz]
    
    Parameters
    ----------
    initial_state : np.ndarray, optional
        Initial state vector (16D). Default is zeros with unit quaternion.
    initial_covariance : np.ndarray, optional
        Initial state covariance matrix (16x16). Default is identity * 0.1.
    process_noise : np.ndarray, optional
        Process noise covariance matrix (16x16). Default based on typical IMU noise.
    measurement_noise : np.ndarray, optional
        Measurement noise covariance for pose measurements (7x7 for position + quaternion).
    
    Attributes
    ----------
    state : np.ndarray
        Current state estimate (16D).
    covariance : np.ndarray
        Current state covariance (16x16).
    """
    
    def __init__(
        self,
        initial_state: Optional[np.ndarray] = None,
        initial_covariance: Optional[np.ndarray] = None,
        process_noise: Optional[np.ndarray] = None,
        measurement_noise: Optional[np.ndarray] = None
    ):
        """Initialize the EKF fusion engine."""
        # Initialize state vector
        if initial_state is not None:
            self.state = initial_state.copy()
        else:
            self.state = np.zeros(16)
            self.state[6:10] = np.array([1, 0, 0, 0])  # Unit quaternion [w, x, y, z]
        
        # Initialize covariance
        if initial_covariance is not None:
            self.covariance = initial_covariance.copy()
        else:
            self.covariance = np.eye(16) * 0.1
        
        # Process noise covariance (tuned for typical IMU characteristics)
        if process_noise is not None:
            self.Q = process_noise.copy()
        else:
            self.Q = np.eye(16)
            self.Q[0:3, 0:3] *= 0.01    # Position process noise
            self.Q[3:6, 3:6] *= 0.01    # Velocity process noise
            self.Q[6:10, 6:10] *= 0.001 # Orientation process noise
            self.Q[10:13, 10:13] *= 0.0001  # Gyro bias process noise
            self.Q[13:16, 13:16] *= 0.001   # Accel bias process noise
        
        # Measurement noise covariance
        if measurement_noise is not None:
            self.R = measurement_noise.copy()
        else:
            # 7D measurement: position (3D) + quaternion (4D)
            self.R = np.eye(7)
            self.R[0:3, 0:3] *= 0.01   # Position measurement noise (1cm std)
            self.R[3:7, 3:7] *= 0.001  # Orientation measurement noise
    
    def predict(
        self,
        delta_position: np.ndarray,
        delta_velocity: np.ndarray,
        delta_rotation: Rotation,
        dt: float
    ):
        """
        EKF Prediction step using IMU pre-integration.
        
        This method propagates the state forward using the IMU pre-integration
        results. It updates the state estimate and covariance based on the
        motion model.
        
        Parameters
        ----------
        delta_position : np.ndarray
            Position change from IMU pre-integration (3D, meters).
        delta_velocity : np.ndarray
            Velocity change from IMU pre-integration (3D, m/s).
        delta_rotation : Rotation
            Orientation change from IMU pre-integration.
        dt : float
            Time interval of pre-integration (seconds).
        """
        # Extract current state
        position = self.state[0:3]
        velocity = self.state[3:6]
        quat = self.state[6:10]
        current_rotation = Rotation.from_quat([quat[1], quat[2], quat[3], quat[0]])  # Convert [w,x,y,z] to [x,y,z,w]
        
        # Predict new state
        # Position: p_new = p_old + v_old * dt + delta_p
        new_position = position + velocity * dt + delta_position
        
        # Velocity: v_new = v_old + delta_v
        new_velocity = velocity + delta_velocity
        
        # Orientation: q_new = q_old * delta_q
        new_rotation = current_rotation * delta_rotation
        new_quat_xyzw = new_rotation.as_quat()
        new_quat = np.array([new_quat_xyzw[3], new_quat_xyzw[0], new_quat_xyzw[1], new_quat_xyzw[2]])  # Convert to [w,x,y,z]
        
        # Biases remain constant in prediction
        gyro_bias = self.state[10:13]
        accel_bias = self.state[13:16]
        
        # Update state
        self.state[0:3] = new_position
        self.state[3:6] = new_velocity
        self.state[6:10] = new_quat
        self.state[10:13] = gyro_bias
        self.state[13:16] = accel_bias
        
        # Normalize quaternion
        self.state[6:10] /= np.linalg.norm(self.state[6:10])
        
        # Update covariance: P = F * P * F^T + Q
        # For simplicity, using a constant state transition matrix
        # In practice, should compute Jacobian of motion model
        F = self._compute_state_transition_matrix(dt)
        self.covariance = F @ self.covariance @ F.T + self.Q * dt
    
    def update(
        self,
        measured_position: np.ndarray,
        measured_rotation: Rotation
    ):
        """
        EKF Update step using AprilTag pose measurement.
        
        This method updates the state estimate using the measured position and
        orientation from AprilTag detection. It computes the Kalman gain and
        updates both the state and covariance.
        
        Parameters
        ----------
        measured_position : np.ndarray
            Measured 3D position from AprilTag (meters).
        measured_rotation : Rotation
            Measured orientation from AprilTag.
        """
        # Convert measured rotation to quaternion [w, x, y, z]
        measured_quat_xyzw = measured_rotation.as_quat()
        measured_quat = np.array([
            measured_quat_xyzw[3],
            measured_quat_xyzw[0],
            measured_quat_xyzw[1],
            measured_quat_xyzw[2]
        ])
        
        # Measurement vector (7D: position + quaternion)
        z = np.concatenate([measured_position, measured_quat])
        
        # Predicted measurement (from current state)
        predicted_position = self.state[0:3]
        predicted_quat = self.state[6:10]
        h = np.concatenate([predicted_position, predicted_quat])
        
        # Innovation (measurement residual)
        # For quaternions, we need special handling to ensure shortest path
        y = z - h
        
        # Handle quaternion ambiguity (q and -q represent same rotation)
        if np.dot(measured_quat, predicted_quat) < 0:
            y[3:7] = z[3:7] + h[3:7]  # Use opposite sign
        
        # Measurement matrix (7x16): we observe position and orientation
        H = np.zeros((7, 16))
        H[0:3, 0:3] = np.eye(3)  # Position
        H[3:7, 6:10] = np.eye(4)  # Orientation (quaternion)
        
        # Innovation covariance
        S = H @ self.covariance @ H.T + self.R
        
        # Kalman gain
        K = self.covariance @ H.T @ np.linalg.inv(S)
        
        # Update state
        self.state = self.state + K @ y
        
        # Normalize quaternion after update
        self.state[6:10] /= np.linalg.norm(self.state[6:10])
        
        # Update covariance: P = (I - K * H) * P
        I = np.eye(16)
        self.covariance = (I - K @ H) @ self.covariance
    
    def _compute_state_transition_matrix(self, dt: float) -> np.ndarray:
        """
        Compute the state transition matrix F for the prediction step.
        
        This is a linearized version of the nonlinear motion model.
        
        Parameters
        ----------
        dt : float
            Time step (seconds).
        
        Returns
        -------
        np.ndarray
            State transition matrix (16x16).
        """
        F = np.eye(16)
        
        # Position depends on velocity
        F[0:3, 3:6] = np.eye(3) * dt
        
        # Velocity, orientation, and biases are independent in this simplified model
        # In a more sophisticated implementation, would include coupling terms
        
        return F
    
    def get_state(self) -> dict:
        """
        Get the current state estimate in a convenient format.
        
        Returns
        -------
        dict
            Dictionary containing:
            - 'position': 3D position (meters)
            - 'velocity': 3D velocity (m/s)
            - 'orientation': Rotation object
            - 'quaternion': Orientation as quaternion [w, x, y, z]
            - 'gyro_bias': Gyroscope bias (rad/s)
            - 'accel_bias': Accelerometer bias (m/s^2)
        """
        quat = self.state[6:10]
        # Convert [w, x, y, z] to [x, y, z, w] for scipy
        quat_xyzw = np.array([quat[1], quat[2], quat[3], quat[0]])
        
        return {
            'position': self.state[0:3].copy(),
            'velocity': self.state[3:6].copy(),
            'orientation': Rotation.from_quat(quat_xyzw),
            'quaternion': quat.copy(),
            'gyro_bias': self.state[10:13].copy(),
            'accel_bias': self.state[13:16].copy()
        }
    
    def get_covariance(self) -> np.ndarray:
        """
        Get the current state covariance matrix.
        
        Returns
        -------
        np.ndarray
            State covariance matrix (16x16).
        """
        return self.covariance.copy()
    
    def get_position_uncertainty(self) -> float:
        """
        Get the position uncertainty (standard deviation).
        
        Returns
        -------
        float
            3D position uncertainty (meters).
        """
        position_cov = self.covariance[0:3, 0:3]
        return np.sqrt(np.trace(position_cov))
    
    def reset(
        self,
        position: Optional[np.ndarray] = None,
        orientation: Optional[Rotation] = None
    ):
        """
        Reset the filter with a new initial state.
        
        Parameters
        ----------
        position : np.ndarray, optional
            Initial position (3D). Default is origin.
        orientation : Rotation, optional
            Initial orientation. Default is identity.
        """
        self.state = np.zeros(16)
        
        if position is not None:
            self.state[0:3] = position
        
        if orientation is not None:
            quat_xyzw = orientation.as_quat()
            self.state[6:10] = np.array([
                quat_xyzw[3],
                quat_xyzw[0],
                quat_xyzw[1],
                quat_xyzw[2]
            ])
        else:
            self.state[6:10] = np.array([1, 0, 0, 0])  # Unit quaternion
        
        # Reset covariance
        self.covariance = np.eye(16) * 0.1
    
    def is_initialized(self) -> bool:
        """
        Check if the filter has been properly initialized.
        
        Returns
        -------
        bool
            True if initialized, False otherwise.
        """
        # Check if position has moved from origin or covariance has been updated
        position_moved = np.linalg.norm(self.state[0:3]) > 0.001
        return position_moved
