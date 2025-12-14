#!/usr/bin/env python3
"""
PoseStreamer Example - Simple Pose Streaming to 3D Renderers

This example demonstrates how to integrate PoseStreamer with the VIO system
to stream camera pose (position and orientation) to external 3D rendering
applications using a simple UDP/JSON protocol.

The PoseStreamer is a lightweight alternative to ARBridge, focusing solely
on pose data with minimal overhead.
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

from vio import AprilTagDetector, IMUProcessor, EKFFusionEngine, PoseStreamer


def integrate_pose_streamer_with_vio():
    """
    Demonstrate PoseStreamer integration with VIO main loop.
    
    This example shows the minimal code needed to add real-time pose
    streaming to an existing VIO system.
    """
    print("=" * 60)
    print("PoseStreamer Integration Example")
    print("=" * 60)
    print()
    
    # Camera parameters (simulated)
    image_width, image_height = 640, 480
    camera_matrix = AprilTagDetector.create_default_camera_matrix(
        image_width, image_height, fov_degrees=60.0
    )
    dist_coeffs = np.zeros(5)
    tag_size = 0.19  # 190mm
    
    # Initialize VIO components
    detector = AprilTagDetector(
        tag_size=tag_size,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs
    )
    imu_processor = IMUProcessor()
    ekf = EKFFusionEngine()
    
    # Initialize PoseStreamer
    # This is the key addition - just instantiate the streamer!
    pose_streamer = PoseStreamer(port=6000, host='127.0.0.1')
    
    print("VIO System initialized with PoseStreamer")
    print("Pose data will be streamed to port 6000")
    print()
    print("To receive the stream, run in another terminal:")
    print("  python -c \"from vio import PoseStreamer; PoseStreamer.create_sample_receiver(port=6000, duration=30)\"")
    print()
    print("Starting simulation in 3 seconds...")
    time.sleep(3)
    print()
    
    # Simulation parameters
    fps = 30
    duration = 10.0
    frame_interval = 1.0 / fps
    
    # Simulate circular motion
    radius = 1.5
    angular_vel = 2 * np.pi / 10.0  # 10 second period
    
    start_time = time.time()
    last_frame_time = None
    frame_count = 0
    
    for frame_idx in range(int(duration * fps)):
        current_time = time.time()
        t = current_time - start_time
        
        # Generate synthetic image (blank for demo)
        image = np.ones((image_height, image_width, 3), dtype=np.uint8) * 255
        
        # Simulate IMU measurements
        gyro_measurements = []
        accel_measurements = []
        
        # IMU prediction step (if we have previous frame)
        if last_frame_time is not None:
            dt = current_time - last_frame_time
            
            # Simplified: just predict with small random noise
            state = ekf.get_state()
            delta_pos = np.random.randn(3) * 0.001
            delta_vel = np.random.randn(3) * 0.001
            delta_rot = Rotation.from_euler('xyz', np.random.randn(3) * 0.01, degrees=True)
            
            ekf.predict(delta_pos, delta_vel, delta_rot, dt)
        
        # Simulate pose for demonstration
        # In a real system, this comes from AprilTag detection
        angle = angular_vel * t
        position = np.array([
            radius * np.cos(angle),
            radius * np.sin(angle),
            0.5 + 0.2 * np.sin(2 * angle)
        ])
        
        # Simulate orientation (rotating around Z axis)
        orientation_angle = angle + np.pi / 2  # Tangent to circle
        orientation = Rotation.from_euler('z', orientation_angle)
        
        # Update EKF state (simulating visual measurement)
        ekf.update(position, orientation)
        
        # Get current state
        state = ekf.get_state()
        current_position = state['position']
        current_quaternion = state['quaternion']
        
        # ===== THIS IS THE KEY INTEGRATION POINT =====
        # Stream the pose to external 3D rendering clients
        pose_streamer.stream_pose(current_position, current_quaternion)
        # =============================================
        
        frame_count += 1
        
        # Print status every 30 frames (1 second)
        if frame_count % 30 == 0:
            print(f"Frame {frame_count}: "
                  f"Position = [{current_position[0]:.2f}, {current_position[1]:.2f}, {current_position[2]:.2f}], "
                  f"Quaternion = [{current_quaternion[0]:.3f}, {current_quaternion[1]:.3f}, "
                  f"{current_quaternion[2]:.3f}, {current_quaternion[3]:.3f}]")
        
        last_frame_time = current_time
        
        # Maintain frame rate
        time.sleep(frame_interval)
    
    print()
    print("Simulation complete!")
    pose_streamer.close()


def minimal_example():
    """
    Minimal example showing just the PoseStreamer API.
    
    This demonstrates the simplest possible usage without a full VIO system.
    """
    print("=" * 60)
    print("Minimal PoseStreamer Example")
    print("=" * 60)
    print()
    
    # Create streamer (context manager automatically closes socket)
    with PoseStreamer(port=6000) as streamer:
        print("Streaming 10 pose updates...")
        print()
        
        for i in range(10):
            # Example pose data
            position = np.array([i * 0.1, i * 0.2, 0.5])
            quaternion = np.array([1.0, 0.0, 0.0, 0.0])  # Identity rotation
            
            # Stream the pose
            streamer.stream_pose(position, quaternion)
            
            print(f"Sent frame {i+1}: pos={position}, rot={quaternion}")
            time.sleep(0.5)
    
    print()
    print("Done! Socket closed automatically.")


def run_receiver(port: int = 6000, duration: float = 30.0):
    """
    Run a sample receiver to display streamed pose data.
    
    Parameters
    ----------
    port : int
        Port to listen on.
    duration : float
        Duration in seconds.
    """
    print("=" * 60)
    print("PoseStreamer Receiver")
    print("=" * 60)
    print()
    
    PoseStreamer.create_sample_receiver(port=port, duration=duration)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='PoseStreamer Examples - Stream VIO pose to 3D renderers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full VIO integration example
  python example_pose_streamer.py
  
  # Run minimal example
  python example_pose_streamer.py --minimal
  
  # Run receiver (in separate terminal)
  python example_pose_streamer.py --receiver
  
  # Specify custom port
  python example_pose_streamer.py --port 7000
        """
    )
    parser.add_argument(
        '--minimal',
        action='store_true',
        help='Run minimal example without full VIO system'
    )
    parser.add_argument(
        '--receiver',
        action='store_true',
        help='Run as receiver to display streamed data'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=6000,
        help='UDP port (default: 6000)'
    )
    parser.add_argument(
        '--duration',
        type=float,
        default=30.0,
        help='Duration in seconds (default: 30.0)'
    )
    
    args = parser.parse_args()
    
    if args.receiver:
        run_receiver(port=args.port, duration=args.duration)
    elif args.minimal:
        minimal_example()
    else:
        integrate_pose_streamer_with_vio()


if __name__ == '__main__':
    main()
