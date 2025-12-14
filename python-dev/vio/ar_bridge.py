"""
AR Bridge Module

This module provides the ARBridge class for streaming VIO state data to
external 3D rendering clients via UDP socket in JSON format.
"""

import socket
import json
import numpy as np
from typing import Optional, Tuple
from scipy.spatial.transform import Rotation


class ARBridge:
    """
    Streams VIO state to external AR rendering clients.
    
    This class sets up a UDP socket to stream the 16D state vector
    (Position, Velocity, Quaternion, Biases) from the EKFFusionEngine
    to external 3D rendering applications like Unity, WebGL, or Three.js.
    
    The data is formatted as JSON for easy consumption by rendering clients.
    
    Parameters
    ----------
    host : str, optional
        Default IP address for target_host if not specified. Default is '127.0.0.1' (localhost).
    port : int, optional
        Default UDP port for target_port if not specified. Default is 9999.
    target_host : str, optional
        Target IP address for sending data. If None, uses host parameter.
    target_port : int, optional
        Target UDP port for sending data. If None, uses port parameter.
    
    Attributes
    ----------
    socket : socket.socket
        UDP socket for sending data.
    target_address : Tuple[str, int]
        Target address (host, port) for sending data.
    frame_count : int
        Number of frames sent.
    """
    
    def __init__(
        self,
        host: str = '127.0.0.1',
        port: int = 9999,
        target_host: Optional[str] = None,
        target_port: Optional[int] = None
    ):
        """Initialize the AR Bridge."""
        # Create UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Set target address for sending data
        if target_host is None:
            target_host = host
        if target_port is None:
            target_port = port
        
        self.target_address = (target_host, target_port)
        self.frame_count = 0
        
        print(f"ARBridge initialized: sending to {target_host}:{target_port}")
    
    def send_state(
        self,
        position: np.ndarray,
        velocity: np.ndarray,
        orientation: Rotation,
        quaternion: np.ndarray,
        gyro_bias: np.ndarray,
        accel_bias: np.ndarray,
        timestamp: Optional[float] = None,
        extra_data: Optional[dict] = None
    ) -> bool:
        """
        Send VIO state to the rendering client.
        
        Parameters
        ----------
        position : np.ndarray
            3D position in meters [x, y, z].
        velocity : np.ndarray
            3D velocity in m/s [vx, vy, vz].
        orientation : Rotation
            Orientation as scipy Rotation object.
        quaternion : np.ndarray
            Quaternion [w, x, y, z].
        gyro_bias : np.ndarray
            Gyroscope bias [bgx, bgy, bgz].
        accel_bias : np.ndarray
            Accelerometer bias [bax, bay, baz].
        timestamp : float, optional
            Timestamp in seconds.
        extra_data : dict, optional
            Additional data to include in the message.
        
        Returns
        -------
        bool
            True if sent successfully, False otherwise.
        """
        try:
            # Build JSON message
            message = self._build_message(
                position=position,
                velocity=velocity,
                orientation=orientation,
                quaternion=quaternion,
                gyro_bias=gyro_bias,
                accel_bias=accel_bias,
                timestamp=timestamp,
                extra_data=extra_data
            )
            
            # Convert to JSON string
            json_str = json.dumps(message)
            json_bytes = json_str.encode('utf-8')
            
            # Send via UDP
            self.socket.sendto(json_bytes, self.target_address)
            
            self.frame_count += 1
            return True
            
        except Exception as e:
            print(f"ARBridge: Error sending data: {e}")
            return False
    
    def send_ekf_state(
        self,
        ekf_state: dict,
        timestamp: Optional[float] = None,
        extra_data: Optional[dict] = None
    ) -> bool:
        """
        Send state from EKFFusionEngine.get_state() output.
        
        This is a convenience method that accepts the dictionary format
        returned by EKFFusionEngine.get_state().
        
        Parameters
        ----------
        ekf_state : dict
            State dictionary from EKFFusionEngine.get_state().
            Should contain: position, velocity, orientation, quaternion,
            gyro_bias, accel_bias.
        timestamp : float, optional
            Timestamp in seconds.
        extra_data : dict, optional
            Additional data to include in the message.
        
        Returns
        -------
        bool
            True if sent successfully, False otherwise.
        """
        return self.send_state(
            position=ekf_state['position'],
            velocity=ekf_state['velocity'],
            orientation=ekf_state['orientation'],
            quaternion=ekf_state['quaternion'],
            gyro_bias=ekf_state['gyro_bias'],
            accel_bias=ekf_state['accel_bias'],
            timestamp=timestamp,
            extra_data=extra_data
        )
    
    def _build_message(
        self,
        position: np.ndarray,
        velocity: np.ndarray,
        orientation: Rotation,
        quaternion: np.ndarray,
        gyro_bias: np.ndarray,
        accel_bias: np.ndarray,
        timestamp: Optional[float] = None,
        extra_data: Optional[dict] = None
    ) -> dict:
        """
        Build JSON message from VIO state.
        
        Parameters
        ----------
        position : np.ndarray
            3D position.
        velocity : np.ndarray
            3D velocity.
        orientation : Rotation
            Orientation as Rotation object.
        quaternion : np.ndarray
            Quaternion [w, x, y, z].
        gyro_bias : np.ndarray
            Gyroscope bias.
        accel_bias : np.ndarray
            Accelerometer bias.
        timestamp : float, optional
            Timestamp.
        extra_data : dict, optional
            Additional data.
        
        Returns
        -------
        dict
            JSON-serializable dictionary.
        """
        # Extract Euler angles for convenience
        euler = orientation.as_euler('xyz', degrees=True)
        
        # Build message
        message = {
            'frame': self.frame_count,
            'timestamp': timestamp,
            'pose': {
                'position': {
                    'x': float(position[0]),
                    'y': float(position[1]),
                    'z': float(position[2])
                },
                'orientation': {
                    'quaternion': {
                        'w': float(quaternion[0]),
                        'x': float(quaternion[1]),
                        'y': float(quaternion[2]),
                        'z': float(quaternion[3])
                    },
                    'euler': {
                        'roll': float(euler[0]),
                        'pitch': float(euler[1]),
                        'yaw': float(euler[2])
                    }
                }
            },
            'velocity': {
                'x': float(velocity[0]),
                'y': float(velocity[1]),
                'z': float(velocity[2])
            },
            'biases': {
                'gyroscope': {
                    'x': float(gyro_bias[0]),
                    'y': float(gyro_bias[1]),
                    'z': float(gyro_bias[2])
                },
                'accelerometer': {
                    'x': float(accel_bias[0]),
                    'y': float(accel_bias[1]),
                    'z': float(accel_bias[2])
                }
            }
        }
        
        # Add extra data if provided
        if extra_data is not None:
            message['extra'] = extra_data
        
        return message
    
    def close(self):
        """Close the UDP socket."""
        self.socket.close()
        print(f"ARBridge closed after sending {self.frame_count} frames")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
    
    @staticmethod
    def create_sample_client(port: int = 9999, duration: float = 10.0, host: str = '127.0.0.1'):
        """
        Create a sample UDP client to receive and display AR data.
        
        This is a utility method for testing the ARBridge functionality.
        
        Parameters
        ----------
        port : int, optional
            Port to listen on. Default is 9999.
        duration : float, optional
            How long to run the client in seconds. Default is 10.0.
        host : str, optional
            Host address to bind to. Default is '127.0.0.1' for localhost only.
            Use '0.0.0.0' to listen on all interfaces (less secure).
        """
        import time
        
        print(f"Starting sample AR client on {host}:{port}")
        print(f"Listening for {duration} seconds...")
        print("-" * 60)
        
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.settimeout(1.0)  # 1 second timeout
        
        start_time = time.time()
        frame_count = 0
        
        try:
            while (time.time() - start_time) < duration:
                try:
                    # Receive data
                    data, addr = sock.recvfrom(4096)
                    message = json.loads(data.decode('utf-8'))
                    
                    frame_count += 1
                    
                    # Display received data
                    pos = message['pose']['position']
                    quat = message['pose']['orientation']['quaternion']
                    euler = message['pose']['orientation']['euler']
                    
                    print(f"Frame {message['frame']}:")
                    print(f"  Position: ({pos['x']:.3f}, {pos['y']:.3f}, {pos['z']:.3f})")
                    print(f"  Quaternion: ({quat['w']:.3f}, {quat['x']:.3f}, "
                          f"{quat['y']:.3f}, {quat['z']:.3f})")
                    print(f"  Euler (deg): ({euler['roll']:.1f}, {euler['pitch']:.1f}, "
                          f"{euler['yaw']:.1f})")
                    print()
                    
                except socket.timeout:
                    continue
                    
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            sock.close()
            print(f"\nReceived {frame_count} frames")
            print("Sample client closed")
