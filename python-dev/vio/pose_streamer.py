"""
Pose Streamer Module

This module provides the PoseStreamer class for streaming camera pose data
(position and quaternion) to external 3D rendering applications via UDP socket.

This is a lightweight alternative to ARBridge, focusing solely on pose streaming
with a simple JSON format.
"""

import socket
import json
import numpy as np
from typing import Optional, Tuple, Union


class PoseStreamer:
    """
    Streams camera pose to external 3D rendering clients.
    
    This class sets up a UDP socket to broadcast the camera's 3D position
    and orientation (as quaternion) to external rendering applications.
    The data is formatted as simple JSON for easy consumption.
    
    This is designed to integrate with EKFFusionEngine to provide real-time
    pose updates for AR/3D visualization.
    
    Parameters
    ----------
    port : int, optional
        UDP port for broadcasting data. Default is 6000.
    host : str, optional
        Target IP address for sending data. Default is '127.0.0.1' (localhost).
    
    Attributes
    ----------
    socket : socket.socket
        UDP socket for sending data.
    target_address : Tuple[str, int]
        Target address (host, port) for sending data.
    frame_count : int
        Number of frames sent.
    
    Examples
    --------
    >>> streamer = PoseStreamer(port=6000)
    >>> position = np.array([1.0, 2.0, 3.0])
    >>> quaternion = np.array([1.0, 0.0, 0.0, 0.0])  # [w, x, y, z]
    >>> streamer.stream_pose(position, quaternion)
    >>> streamer.close()
    
    Using context manager:
    >>> with PoseStreamer(port=6000) as streamer:
    ...     streamer.stream_pose(position, quaternion)
    """
    
    def __init__(
        self,
        port: int = 6000,
        host: str = '127.0.0.1'
    ):
        """
        Initialize the Pose Streamer.
        
        Parameters
        ----------
        port : int, optional
            UDP port for broadcasting. Default is 6000.
        host : str, optional
            Target host address. Default is '127.0.0.1'.
        """
        # Create UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Set target address
        self.target_address = (host, port)
        self.frame_count = 0
        
        print(f"PoseStreamer initialized: broadcasting to {host}:{port}")
    
    def stream_pose(
        self,
        position: Union[np.ndarray, list, tuple],
        quaternion: Union[np.ndarray, list, tuple]
    ) -> bool:
        """
        Stream camera pose to the rendering client.
        
        This method broadcasts the camera's current 3D position and orientation
        as a JSON message over UDP.
        
        Parameters
        ----------
        position : np.ndarray or list or tuple
            3D position in meters [x, y, z].
        quaternion : np.ndarray or list or tuple
            Orientation quaternion [w, x, y, z].
        
        Returns
        -------
        bool
            True if sent successfully, False otherwise.
        
        Examples
        --------
        >>> streamer = PoseStreamer()
        >>> position = [1.0, 2.0, 3.0]
        >>> quaternion = [1.0, 0.0, 0.0, 0.0]
        >>> success = streamer.stream_pose(position, quaternion)
        """
        try:
            # Convert to lists if numpy arrays
            if isinstance(position, np.ndarray):
                pos_list = position.tolist()
            else:
                pos_list = list(position)
            
            if isinstance(quaternion, np.ndarray):
                quat_list = quaternion.tolist()
            else:
                quat_list = list(quaternion)
            
            # Validate input dimensions
            if len(pos_list) != 3:
                raise ValueError(f"Position must be 3D, got {len(pos_list)} elements")
            if len(quat_list) != 4:
                raise ValueError(f"Quaternion must be 4D [w,x,y,z], got {len(quat_list)} elements")
            
            # Build simple JSON message
            message = {
                "pos": [float(pos_list[0]), float(pos_list[1]), float(pos_list[2])],
                "rot": [float(quat_list[0]), float(quat_list[1]), 
                       float(quat_list[2]), float(quat_list[3])]
            }
            
            # Convert to JSON string
            json_str = json.dumps(message)
            json_bytes = json_str.encode('utf-8')
            
            # Broadcast via UDP
            self.socket.sendto(json_bytes, self.target_address)
            
            self.frame_count += 1
            return True
            
        except Exception as e:
            print(f"PoseStreamer: Error sending data: {e}")
            return False
    
    def close(self):
        """Close the UDP socket and clean up resources."""
        self.socket.close()
        print(f"PoseStreamer closed after sending {self.frame_count} frames")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
    
    @staticmethod
    def create_sample_receiver(
        port: int = 6000,
        duration: float = 10.0,
        host: str = '127.0.0.1'
    ):
        """
        Create a sample UDP receiver to display streamed pose data.
        
        This is a utility method for testing the PoseStreamer functionality.
        Run this in a separate terminal to receive and display pose updates.
        
        Parameters
        ----------
        port : int, optional
            Port to listen on. Default is 6000.
        duration : float, optional
            How long to run the receiver in seconds. Default is 10.0.
        host : str, optional
            Host address to bind to. Default is '127.0.0.1' for localhost only.
        
        Examples
        --------
        Run in terminal:
        >>> from vio import PoseStreamer
        >>> PoseStreamer.create_sample_receiver(port=6000, duration=30)
        """
        import time
        
        print(f"Starting Pose Receiver on {host}:{port}")
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
                    
                    # Extract pose data
                    pos = message['pos']
                    rot = message['rot']
                    
                    # Display received data
                    print(f"Frame {frame_count}:")
                    print(f"  Position: [{pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}]")
                    print(f"  Quaternion: [{rot[0]:.3f}, {rot[1]:.3f}, {rot[2]:.3f}, {rot[3]:.3f}]")
                    print()
                    
                except socket.timeout:
                    continue
                    
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            sock.close()
            print(f"\nReceived {frame_count} frames")
            print("Receiver closed")
