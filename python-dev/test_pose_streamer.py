#!/usr/bin/env python3
"""
Test script for PoseStreamer functionality.

This script validates the PoseStreamer class for streaming camera pose
data to external 3D rendering clients via UDP/JSON.
"""

import numpy as np
from scipy.spatial.transform import Rotation
import time
import socket
import json
import threading

from vio import PoseStreamer, EKFFusionEngine


def test_initialization():
    """Test PoseStreamer initialization."""
    print("Test 1: Initialization")
    print("-" * 60)
    
    # Test default initialization
    streamer = PoseStreamer()
    assert streamer.target_address == ('127.0.0.1', 6000), "Default address incorrect"
    assert streamer.frame_count == 0, "Initial frame count should be 0"
    print("✓ Default initialization successful")
    streamer.close()
    
    # Test custom port
    streamer = PoseStreamer(port=7000, host='127.0.0.1')
    assert streamer.target_address == ('127.0.0.1', 7000), "Custom address incorrect"
    print("✓ Custom port initialization successful")
    streamer.close()
    
    print()
    return True


def test_stream_pose():
    """Test basic pose streaming."""
    print("Test 2: Basic Pose Streaming")
    print("-" * 60)
    
    streamer = PoseStreamer(port=6001)
    
    # Test with numpy arrays
    position = np.array([1.0, 2.0, 3.0])
    quaternion = np.array([1.0, 0.0, 0.0, 0.0])  # [w, x, y, z]
    
    success = streamer.stream_pose(position, quaternion)
    assert success, "Failed to stream pose"
    assert streamer.frame_count == 1, "Frame count should be 1"
    print("✓ Successfully streamed pose with numpy arrays")
    
    # Test with lists
    position_list = [1.5, 2.5, 3.5]
    quaternion_list = [0.707, 0.707, 0.0, 0.0]
    
    success = streamer.stream_pose(position_list, quaternion_list)
    assert success, "Failed to stream pose with lists"
    assert streamer.frame_count == 2, "Frame count should be 2"
    print("✓ Successfully streamed pose with lists")
    
    # Test with tuples
    position_tuple = (2.0, 3.0, 4.0)
    quaternion_tuple = (1.0, 0.0, 0.0, 0.0)
    
    success = streamer.stream_pose(position_tuple, quaternion_tuple)
    assert success, "Failed to stream pose with tuples"
    assert streamer.frame_count == 3, "Frame count should be 3"
    print("✓ Successfully streamed pose with tuples")
    
    streamer.close()
    print()
    return True


def test_input_validation():
    """Test input validation."""
    print("Test 3: Input Validation")
    print("-" * 60)
    
    streamer = PoseStreamer(port=6002)
    
    # Test invalid position dimension
    try:
        invalid_pos = [1.0, 2.0]  # Only 2 elements
        quaternion = [1.0, 0.0, 0.0, 0.0]
        success = streamer.stream_pose(invalid_pos, quaternion)
        assert not success, "Should fail with invalid position dimension"
        print("✓ Correctly rejected invalid position dimension")
    except ValueError:
        print("✓ Correctly raised ValueError for invalid position")
    
    # Test invalid quaternion dimension
    try:
        position = [1.0, 2.0, 3.0]
        invalid_quat = [1.0, 0.0, 0.0]  # Only 3 elements
        success = streamer.stream_pose(position, invalid_quat)
        assert not success, "Should fail with invalid quaternion dimension"
        print("✓ Correctly rejected invalid quaternion dimension")
    except ValueError:
        print("✓ Correctly raised ValueError for invalid quaternion")
    
    streamer.close()
    print()
    return True


def test_json_format():
    """Test JSON message format."""
    print("Test 4: JSON Message Format")
    print("-" * 60)
    
    # Create receiver socket to capture message
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    receiver.bind(('127.0.0.1', 6003))
    receiver.settimeout(2.0)
    
    # Create streamer and send message
    streamer = PoseStreamer(port=6003, host='127.0.0.1')
    position = [1.5, 2.5, 3.5]
    quaternion = [0.707, 0.707, 0.0, 0.0]
    
    streamer.stream_pose(position, quaternion)
    
    # Receive and parse message
    try:
        data, _ = receiver.recvfrom(4096)
        message = json.loads(data.decode('utf-8'))
        
        # Validate format
        assert 'pos' in message, "Message should contain 'pos' key"
        assert 'rot' in message, "Message should contain 'rot' key"
        
        assert len(message['pos']) == 3, "Position should have 3 elements"
        assert len(message['rot']) == 4, "Quaternion should have 4 elements"
        
        # Validate values
        assert message['pos'][0] == 1.5, f"pos[0] should be 1.5, got {message['pos'][0]}"
        assert message['pos'][1] == 2.5, f"pos[1] should be 2.5, got {message['pos'][1]}"
        assert message['pos'][2] == 3.5, f"pos[2] should be 3.5, got {message['pos'][2]}"
        
        assert abs(message['rot'][0] - 0.707) < 0.001, f"rot[0] should be ~0.707, got {message['rot'][0]}"
        assert abs(message['rot'][1] - 0.707) < 0.001, f"rot[1] should be ~0.707, got {message['rot'][1]}"
        
        print("✓ JSON message format is correct")
        print(f"  Received message: {json.dumps(message, indent=2)}")
        
    except socket.timeout:
        print("✗ Failed to receive message within timeout")
        streamer.close()
        receiver.close()
        return False
    
    streamer.close()
    receiver.close()
    print()
    return True


def test_context_manager():
    """Test context manager functionality."""
    print("Test 5: Context Manager")
    print("-" * 60)
    
    # Use context manager
    with PoseStreamer(port=6004) as streamer:
        position = [1.0, 2.0, 3.0]
        quaternion = [1.0, 0.0, 0.0, 0.0]
        success = streamer.stream_pose(position, quaternion)
        assert success, "Failed to stream in context manager"
    
    print("✓ Context manager works correctly (auto-cleanup)")
    print()
    return True


def test_ekf_integration():
    """Test integration with EKFFusionEngine."""
    print("Test 6: EKF Integration")
    print("-" * 60)
    
    # Create EKF and PoseStreamer
    ekf = EKFFusionEngine()
    streamer = PoseStreamer(port=6005)
    
    # Set a specific state in EKF
    initial_position = np.array([0.5, 1.0, 0.2])
    initial_rotation = Rotation.from_euler('xyz', [0, 0, 45], degrees=True)
    ekf.reset(position=initial_position, orientation=initial_rotation)
    
    # Get state from EKF
    state = ekf.get_state()
    position = state['position']
    quaternion = state['quaternion']
    
    # Stream using EKF state
    success = streamer.stream_pose(position, quaternion)
    assert success, "Failed to stream EKF state"
    
    print("✓ Successfully integrated with EKFFusionEngine")
    print(f"  Position: {position}")
    print(f"  Quaternion: {quaternion}")
    
    streamer.close()
    print()
    return True


def test_continuous_streaming():
    """Test continuous streaming at high rate."""
    print("Test 7: Continuous Streaming")
    print("-" * 60)
    
    streamer = PoseStreamer(port=6006)
    
    # Stream 100 frames rapidly
    num_frames = 100
    start_time = time.time()
    
    for i in range(num_frames):
        # Generate varying pose
        t = i / 10.0
        position = np.array([
            np.cos(t),
            np.sin(t),
            0.5 + 0.1 * np.sin(2 * t)
        ])
        
        angle = t / 2
        quaternion = np.array([
            np.cos(angle), 0, 0, np.sin(angle)
        ])
        quaternion /= np.linalg.norm(quaternion)
        
        streamer.stream_pose(position, quaternion)
    
    elapsed = time.time() - start_time
    rate = num_frames / elapsed
    
    print(f"✓ Streamed {num_frames} frames in {elapsed:.3f} seconds")
    print(f"  Streaming rate: {rate:.1f} Hz")
    print(f"  Final frame count: {streamer.frame_count}")
    
    assert streamer.frame_count == num_frames, f"Frame count mismatch: {streamer.frame_count} != {num_frames}"
    
    streamer.close()
    print()
    return True


def test_receiver_client():
    """Test the sample receiver client."""
    print("Test 8: Sample Receiver Client")
    print("-" * 60)
    
    print("Starting receiver in background thread...")
    
    received_frames = []
    
    def receiver_thread():
        """Run receiver in thread."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', 6007))
        sock.settimeout(1.0)
        
        for _ in range(5):
            try:
                data, _ = sock.recvfrom(4096)
                message = json.loads(data.decode('utf-8'))
                received_frames.append(message)
            except socket.timeout:
                continue
        
        sock.close()
    
    # Start receiver thread
    thread = threading.Thread(target=receiver_thread)
    thread.start()
    
    time.sleep(0.5)  # Let receiver start
    
    # Send some frames
    streamer = PoseStreamer(port=6007)
    for i in range(5):
        position = [float(i), float(i+1), float(i+2)]
        quaternion = [1.0, 0.0, 0.0, 0.0]
        streamer.stream_pose(position, quaternion)
        time.sleep(0.1)
    
    streamer.close()
    
    # Wait for receiver to finish
    thread.join(timeout=3.0)
    
    print(f"✓ Receiver received {len(received_frames)} frames")
    if len(received_frames) > 0:
        print(f"  Sample frame: {received_frames[0]}")
    
    assert len(received_frames) > 0, "Receiver should have received at least one frame"
    
    print()
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("PoseStreamer Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_initialization,
        test_stream_pose,
        test_input_validation,
        test_json_format,
        test_context_manager,
        test_ekf_integration,
        test_continuous_streaming,
        test_receiver_client
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} raised exception: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 60)
    print("Test Results")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print()
    
    if failed == 0:
        print("✓ All tests passed!")
        return True
    else:
        print("✗ Some tests failed")
        return False


if __name__ == '__main__':
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
