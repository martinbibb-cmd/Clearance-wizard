#!/usr/bin/env python3
"""
ARBridge Example - Streaming VIO data to AR clients

This example demonstrates how to integrate ARBridge with the VIO system
to stream pose data to external 3D rendering applications (Unity, WebGL, Three.js).
"""

import numpy as np
from scipy.spatial.transform import Rotation
import time
import argparse

try:
    import cv2
    has_cv2 = True
except ImportError:
    has_cv2 = False
    print("Note: OpenCV not available, running without camera support")

from vio import AprilTagDetector, IMUProcessor, EKFFusionEngine, ARBridge


class VIOWithAR:
    """
    VIO System with AR streaming support.
    
    This class extends the basic VIO functionality with real-time
    streaming to AR rendering clients via ARBridge.
    """
    
    def __init__(
        self,
        tag_size: float,
        camera_matrix: np.ndarray,
        dist_coeffs: np.ndarray,
        ar_host: str = '127.0.0.1',
        ar_port: int = 9999,
        enable_ar: bool = True
    ):
        """
        Initialize VIO system with AR streaming.
        
        Parameters
        ----------
        tag_size : float
            Physical size of AprilTag markers in meters.
        camera_matrix : np.ndarray
            3x3 camera intrinsic matrix.
        dist_coeffs : np.ndarray
            Camera distortion coefficients.
        ar_host : str, optional
            AR client host address. Default is '127.0.0.1'.
        ar_port : int, optional
            AR client UDP port. Default is 9999.
        enable_ar : bool, optional
            Enable AR streaming. Default is True.
        """
        # Initialize VIO components
        self.detector = AprilTagDetector(
            tag_size=tag_size,
            camera_matrix=camera_matrix,
            dist_coeffs=dist_coeffs
        )
        self.imu_processor = IMUProcessor()
        self.ekf = EKFFusionEngine()
        
        # Initialize AR bridge if enabled
        self.enable_ar = enable_ar
        if self.enable_ar:
            self.ar_bridge = ARBridge(host=ar_host, port=ar_port)
            print(f"AR streaming enabled to {ar_host}:{ar_port}")
        else:
            self.ar_bridge = None
            print("AR streaming disabled")
        
        self.last_frame_time = None
        self.frame_count = 0
    
    def process_frame(
        self,
        image: np.ndarray,
        timestamp: float,
        gyro_measurements: list,
        accel_measurements: list
    ) -> dict:
        """
        Process a frame and stream to AR client.
        
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
        
        Returns
        -------
        dict
            Processing results including pose and detection info.
        """
        self.frame_count += 1
        
        # IMU Prediction
        if self.last_frame_time is not None and len(gyro_measurements) > 0:
            state = self.ekf.get_state()
            delta_pos, delta_vel, delta_rot = self.imu_processor.preintegrate(
                gyro_measurements,
                accel_measurements,
                initial_rotation=state['orientation']
            )
            dt = timestamp - self.last_frame_time
            self.ekf.predict(delta_pos, delta_vel, delta_rot, dt)
        
        # AprilTag Detection
        detections = self.detector.detect(image)
        num_detections = len(detections)
        
        # Update with visual measurements
        if num_detections > 0:
            detection = detections[0]
            measured_position = detection['translation']
            measured_rotation = Rotation.from_matrix(detection['rotation_matrix'])
            self.ekf.update(measured_position, measured_rotation)
        
        # Get current state
        state = self.ekf.get_state()
        
        # Stream to AR client
        if self.enable_ar and self.ar_bridge is not None:
            extra_data = {
                'detections': num_detections,
                'frame': self.frame_count,
                'has_visual_update': num_detections > 0
            }
            
            if num_detections > 0:
                extra_data['detected_tag_id'] = int(detections[0]['tag_id'])
            
            self.ar_bridge.send_ekf_state(
                state,
                timestamp=timestamp,
                extra_data=extra_data
            )
        
        self.last_frame_time = timestamp
        
        return {
            'state': state,
            'detections': num_detections,
            'timestamp': timestamp,
            'frame': self.frame_count
        }
    
    def close(self):
        """Clean up resources."""
        if self.ar_bridge is not None:
            self.ar_bridge.close()


def simulate_vio_with_ar(duration: float = 10.0, ar_port: int = 9999):
    """
    Simulate VIO system with AR streaming.
    
    Parameters
    ----------
    duration : float
        Simulation duration in seconds.
    ar_port : int
        AR client UDP port.
    """
    print("=" * 60)
    print("VIO System with AR Streaming - Simulation")
    print("=" * 60)
    print()
    
    # Camera parameters
    image_width, image_height = 640, 480
    camera_matrix = AprilTagDetector.create_default_camera_matrix(
        image_width, image_height, fov_degrees=60.0
    )
    dist_coeffs = np.zeros(5)
    tag_size = 0.19
    
    # Initialize VIO with AR
    vio = VIOWithAR(
        tag_size=tag_size,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs,
        ar_host='127.0.0.1',
        ar_port=ar_port,
        enable_ar=True
    )
    
    print(f"Streaming to port {ar_port} for {duration} seconds")
    print("To receive data, run in another terminal:")
    print(f"  python -c \"from vio import ARBridge; ARBridge.create_sample_client(port={ar_port}, duration={duration+5})\"")
    print()
    print("Simulation starting in 3 seconds...")
    time.sleep(3)
    print()
    
    # Simulation parameters
    fps = 30
    imu_rate = 200
    frame_interval = 1.0 / fps
    imu_interval = 1.0 / imu_rate
    
    # Simulate circular motion
    radius = 1.0
    angular_vel = 2 * np.pi / 8.0  # 8 second period
    
    start_time = time.time()
    
    for frame_idx in range(int(duration * fps)):
        timestamp = time.time()
        t = timestamp - start_time
        
        # Generate synthetic image
        image = np.ones((image_height, image_width, 3), dtype=np.uint8) * 255
        
        # Generate IMU measurements
        gyro_measurements = []
        accel_measurements = []
        
        imu_samples = int(frame_interval / imu_interval)
        for i in range(imu_samples):
            t_imu = t - frame_interval + i * imu_interval
            
            # Simulated IMU for circular motion
            gyro = np.array([0, 0, angular_vel]) + np.random.randn(3) * 0.01
            
            # Centripetal acceleration + gravity
            angle = angular_vel * t_imu
            accel_centripetal = np.array([
                -radius * angular_vel**2 * np.cos(angle),
                -radius * angular_vel**2 * np.sin(angle),
                0
            ])
            accel = np.array([0, 0, 9.81]) + accel_centripetal + np.random.randn(3) * 0.1
            
            gyro_measurements.append((t_imu, gyro))
            accel_measurements.append((t_imu, accel))
        
        # Simulate position for EKF (since we have no real AprilTags)
        angle = angular_vel * t
        position = np.array([
            radius * np.cos(angle),
            radius * np.sin(angle),
            0.5 + 0.1 * np.sin(2 * angle)
        ])
        vio.ekf.state[0:3] = position
        
        # Simulate orientation (rotation around Z axis)
        quat_angle = angle / 2
        vio.ekf.state[6:10] = np.array([
            np.cos(quat_angle), 0, 0, np.sin(quat_angle)
        ])
        vio.ekf.state[6:10] /= np.linalg.norm(vio.ekf.state[6:10])
        
        # Process frame
        result = vio.process_frame(
            image,
            timestamp,
            gyro_measurements,
            accel_measurements
        )
        
        # Print status every second
        if frame_idx % fps == 0:
            pos = result['state']['position']
            print(f"Frame {result['frame']}: "
                  f"Position = ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
        
        # Maintain frame rate
        time.sleep(frame_interval)
    
    print()
    print("Simulation complete!")
    vio.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='VIO System with AR Streaming Example'
    )
    parser.add_argument(
        '--duration',
        type=float,
        default=10.0,
        help='Simulation duration in seconds (default: 10.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=9999,
        help='AR client UDP port (default: 9999)'
    )
    parser.add_argument(
        '--client',
        action='store_true',
        help='Run as AR client to receive data'
    )
    
    args = parser.parse_args()
    
    if args.client:
        print("Running as AR client...")
        ARBridge.create_sample_client(port=args.port, duration=args.duration + 5)
    else:
        simulate_vio_with_ar(duration=args.duration, ar_port=args.port)


if __name__ == '__main__':
    main()
