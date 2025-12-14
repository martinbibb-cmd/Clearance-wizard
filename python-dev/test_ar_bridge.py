#!/usr/bin/env python3
"""
Test script for ARBridge functionality.

This script demonstrates the ARBridge streaming VIO state data to
external rendering clients via UDP/JSON.
"""

import numpy as np
from scipy.spatial.transform import Rotation
import time
import sys
import threading

from vio import ARBridge, EKFFusionEngine


def test_basic_send():
    """Test basic ARBridge send functionality."""
    print("Test 1: Basic Send Functionality")
    print("-" * 60)
    
    # Create ARBridge
    bridge = ARBridge(host='127.0.0.1', port=9999)
    
    # Create sample state
    position = np.array([1.0, 2.0, 3.0])
    velocity = np.array([0.1, 0.2, 0.3])
    orientation = Rotation.from_euler('xyz', [10, 20, 30], degrees=True)
    quaternion = np.array([1.0, 0.0, 0.0, 0.0])  # [w, x, y, z]
    gyro_bias = np.array([0.01, 0.02, 0.03])
    accel_bias = np.array([0.001, 0.002, 0.003])
    
    # Send state
    success = bridge.send_state(
        position=position,
        velocity=velocity,
        orientation=orientation,
        quaternion=quaternion,
        gyro_bias=gyro_bias,
        accel_bias=accel_bias,
        timestamp=time.time()
    )
    
    if success:
        print("✓ Successfully sent state via ARBridge")
        print(f"  Frame count: {bridge.frame_count}")
    else:
        print("✗ Failed to send state")
        return False
    
    bridge.close()
    print()
    return True


def test_ekf_integration():
    """Test ARBridge integration with EKFFusionEngine."""
    print("Test 2: EKF Integration")
    print("-" * 60)
    
    # Create EKF and ARBridge
    ekf = EKFFusionEngine()
    bridge = ARBridge(host='127.0.0.1', port=9999)
    
    # Set initial state
    initial_position = np.array([0.5, 1.0, 0.2])
    initial_rotation = Rotation.from_euler('xyz', [0, 0, 45], degrees=True)
    ekf.reset(position=initial_position, orientation=initial_rotation)
    
    # Get state and send via bridge
    state = ekf.get_state()
    success = bridge.send_ekf_state(state, timestamp=time.time())
    
    if success:
        print("✓ Successfully sent EKF state via ARBridge")
        print(f"  Position: {state['position']}")
        print(f"  Quaternion: {state['quaternion']}")
    else:
        print("✗ Failed to send EKF state")
        return False
    
    bridge.close()
    print()
    return True


def test_streaming():
    """Test continuous streaming of VIO data."""
    print("Test 3: Continuous Streaming")
    print("-" * 60)
    
    # Create components
    ekf = EKFFusionEngine()
    bridge = ARBridge(host='127.0.0.1', port=9999)
    
    # Simulate motion for 3 seconds
    duration = 3.0
    rate = 30  # Hz
    dt = 1.0 / rate
    
    print(f"Streaming at {rate} Hz for {duration} seconds...")
    print("Note: Run 'python -c \"from vio import ARBridge; ARBridge.create_sample_client()\"'")
    print("      in another terminal to receive data.")
    print()
    
    start_time = time.time()
    frame_count = 0
    
    # Set initial state
    ekf.reset(position=np.array([0.0, 0.0, 0.5]))
    
    while (time.time() - start_time) < duration:
        # Simulate some motion
        t = time.time() - start_time
        
        # Circular motion
        radius = 1.0
        angular_vel = 2 * np.pi / 10.0  # 10 second period
        angle = angular_vel * t
        
        position = np.array([
            radius * np.cos(angle),
            radius * np.sin(angle),
            0.5 + 0.1 * np.sin(2 * angle)
        ])
        
        # Update EKF state (simplified - just setting position)
        ekf.state[0:3] = position
        ekf.state[6:10] = np.array([
            np.cos(angle/2), 0, 0, np.sin(angle/2)
        ])  # Rotation around Z
        ekf.state[6:10] /= np.linalg.norm(ekf.state[6:10])
        
        # Get state and send
        state = ekf.get_state()
        bridge.send_ekf_state(
            state,
            timestamp=time.time(),
            extra_data={'motion': 'circular', 'radius': radius}
        )
        
        frame_count += 1
        
        # Maintain frame rate
        time.sleep(dt)
    
    print(f"✓ Streamed {frame_count} frames")
    bridge.close()
    print()
    return True


def test_context_manager():
    """Test ARBridge as context manager."""
    print("Test 4: Context Manager Usage")
    print("-" * 60)
    
    # Use ARBridge with context manager
    with ARBridge(host='127.0.0.1', port=9999) as bridge:
        position = np.array([1.0, 2.0, 3.0])
        velocity = np.zeros(3)
        orientation = Rotation.identity()
        quaternion = np.array([1.0, 0.0, 0.0, 0.0])
        gyro_bias = np.zeros(3)
        accel_bias = np.zeros(3)
        
        success = bridge.send_state(
            position=position,
            velocity=velocity,
            orientation=orientation,
            quaternion=quaternion,
            gyro_bias=gyro_bias,
            accel_bias=accel_bias
        )
        
        if success:
            print("✓ Context manager works correctly")
        else:
            print("✗ Failed to send via context manager")
            return False
    
    print()
    return True


def run_sample_client():
    """Run a sample client in a separate thread."""
    print("\n" + "=" * 60)
    print("Sample Client Output:")
    print("=" * 60)
    ARBridge.create_sample_client(port=9999, duration=5.0)


def main():
    """Run all ARBridge tests."""
    print("=" * 60)
    print("ARBridge Test Suite")
    print("=" * 60)
    print()
    
    # Run tests
    tests = [
        test_basic_send,
        test_ekf_integration,
        test_context_manager,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        print("\nTo test streaming with a receiver:")
        print("  Terminal 1: python -c \"from vio import ARBridge; ARBridge.create_sample_client()\"")
        print("  Terminal 2: python test_ar_bridge.py --stream")
    else:
        print("\n✗ Some tests failed")
        return 1
    
    # Check for streaming test
    if len(sys.argv) > 1 and sys.argv[1] == '--stream':
        print("\n" + "=" * 60)
        print("Running Streaming Test")
        print("=" * 60)
        test_streaming()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
