"""
AR Engine Backend API

This module provides a REST API for AR marker detection and pose estimation.
Supports both AprilTag and ArUco marker detection with configurable parameters.

The API runs as a standalone backend service that can be integrated with
various frontend applications or other systems requiring AR detection.
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import numpy as np
import cv2
import base64
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import io
from datetime import datetime

# Import AR detection modules
try:
    from vio.apriltag_detector import AprilTagDetector
    APRILTAG_AVAILABLE = True
except ImportError:
    APRILTAG_AVAILABLE = False
    print("Warning: AprilTag detector not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Global configuration
CONFIG = {
    'default_marker_type': 'apriltag',
    'default_tag_family': 'tag36h11',
    'default_aruco_dict': 'DICT_4X4_50',
    'default_marker_size': 0.19,  # 190mm in meters
    'default_camera_fov': 60.0,   # degrees
}

# ArUco dictionary mapping
ARUCO_DICT_MAP = {
    'DICT_4X4_50': cv2.aruco.DICT_4X4_50,
    'DICT_4X4_100': cv2.aruco.DICT_4X4_100,
    'DICT_4X4_250': cv2.aruco.DICT_4X4_250,
    'DICT_4X4_1000': cv2.aruco.DICT_4X4_1000,
    'DICT_5X5_50': cv2.aruco.DICT_5X5_50,
    'DICT_5X5_100': cv2.aruco.DICT_5X5_100,
    'DICT_5X5_250': cv2.aruco.DICT_5X5_250,
    'DICT_5X5_1000': cv2.aruco.DICT_5X5_1000,
    'DICT_6X6_50': cv2.aruco.DICT_6X6_50,
    'DICT_6X6_100': cv2.aruco.DICT_6X6_100,
    'DICT_6X6_250': cv2.aruco.DICT_6X6_250,
    'DICT_6X6_1000': cv2.aruco.DICT_6X6_1000,
    'DICT_7X7_50': cv2.aruco.DICT_7X7_50,
    'DICT_7X7_100': cv2.aruco.DICT_7X7_100,
    'DICT_7X7_250': cv2.aruco.DICT_7X7_250,
    'DICT_7X7_1000': cv2.aruco.DICT_7X7_1000,
}


class AREngine:
    """
    Core AR detection engine supporting multiple marker types.
    
    Attributes
    ----------
    apriltag_detector : AprilTagDetector or None
        AprilTag detector instance.
    aruco_dict : cv2.aruco.Dictionary
        ArUco dictionary for marker detection.
    aruco_params : cv2.aruco.DetectorParameters
        ArUco detector parameters.
    camera_matrix : np.ndarray
        Camera intrinsic matrix.
    dist_coeffs : np.ndarray
        Camera distortion coefficients.
    """
    
    def __init__(self):
        """Initialize the AR Engine."""
        self.apriltag_detector = None
        self.aruco_dict = None
        self.aruco_params = None
        self.camera_matrix = None
        self.dist_coeffs = None
        
        logger.info("AR Engine initialized")
    
    def setup_camera_calibration(
        self,
        image_width: int,
        image_height: int,
        fov_degrees: float = 60.0,
        dist_coeffs: Optional[List[float]] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Setup camera calibration parameters.
        
        Parameters
        ----------
        image_width : int
            Image width in pixels.
        image_height : int
            Image height in pixels.
        fov_degrees : float
            Vertical field of view in degrees.
        dist_coeffs : list of float, optional
            Distortion coefficients [k1, k2, p1, p2, k3].
        
        Returns
        -------
        camera_matrix : np.ndarray
            3x3 camera intrinsic matrix.
        dist_coeffs : np.ndarray
            Distortion coefficients.
        """
        # Calculate focal length from FOV
        fov_rad = np.deg2rad(fov_degrees)
        focal_length = image_height / (2 * np.tan(fov_rad / 2))
        
        # Create camera matrix
        cx = image_width / 2
        cy = image_height / 2
        self.camera_matrix = np.array([
            [focal_length, 0, cx],
            [0, focal_length, cy],
            [0, 0, 1]
        ], dtype=np.float32)
        
        # Setup distortion coefficients
        if dist_coeffs is None:
            self.dist_coeffs = np.zeros(5, dtype=np.float32)
        else:
            self.dist_coeffs = np.array(dist_coeffs, dtype=np.float32)
        
        logger.info(f"Camera calibration set: {image_width}x{image_height}, FOV={fov_degrees}°")
        return self.camera_matrix, self.dist_coeffs
    
    def detect_apriltag(
        self,
        image: np.ndarray,
        tag_size: float,
        tag_family: str = 'tag36h11'
    ) -> List[Dict[str, Any]]:
        """
        Detect AprilTag markers in the image.
        
        Parameters
        ----------
        image : np.ndarray
            Input image (BGR or grayscale).
        tag_size : float
            Physical size of the tag in meters.
        tag_family : str
            AprilTag family (e.g., 'tag36h11').
        
        Returns
        -------
        list of dict
            Detected markers with pose information.
        """
        if not APRILTAG_AVAILABLE:
            raise RuntimeError("AprilTag detector not available")
        
        if self.camera_matrix is None:
            raise RuntimeError("Camera calibration not set")
        
        # Initialize detector if needed
        if self.apriltag_detector is None or self.apriltag_detector.tag_size != tag_size:
            self.apriltag_detector = AprilTagDetector(
                tag_size=tag_size,
                camera_matrix=self.camera_matrix,
                dist_coeffs=self.dist_coeffs,
                tag_family=tag_family
            )
        
        # Detect markers
        detections = self.apriltag_detector.detect(image)
        return detections
    
    def detect_aruco(
        self,
        image: np.ndarray,
        marker_size: float,
        aruco_dict_name: str = 'DICT_4X4_50'
    ) -> List[Dict[str, Any]]:
        """
        Detect ArUco markers in the image.
        
        Parameters
        ----------
        image : np.ndarray
            Input image (BGR or grayscale).
        marker_size : float
            Physical size of the marker in meters.
        aruco_dict_name : str
            ArUco dictionary name (e.g., 'DICT_4X4_50').
        
        Returns
        -------
        list of dict
            Detected markers with pose information.
        """
        if self.camera_matrix is None:
            raise RuntimeError("Camera calibration not set")
        
        # Setup ArUco detector if needed
        if self.aruco_dict is None or aruco_dict_name not in ARUCO_DICT_MAP:
            if aruco_dict_name not in ARUCO_DICT_MAP:
                aruco_dict_name = 'DICT_4X4_50'
            
            self.aruco_dict = cv2.aruco.getPredefinedDictionary(
                ARUCO_DICT_MAP[aruco_dict_name]
            )
            self.aruco_params = cv2.aruco.DetectorParameters()
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Detect markers
        corners, ids, rejected = cv2.aruco.detectMarkers(
            gray,
            self.aruco_dict,
            parameters=self.aruco_params
        )
        
        detections = []
        if ids is not None:
            # Estimate pose for each marker
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners,
                marker_size,
                self.camera_matrix,
                self.dist_coeffs
            )
            
            for i, marker_id in enumerate(ids.flatten()):
                # Convert rotation vector to matrix
                rmat, _ = cv2.Rodrigues(rvecs[i])
                
                # Extract position and orientation
                position = tvecs[i][0]
                
                detection = {
                    'id': int(marker_id),
                    'family': aruco_dict_name,
                    'position': {
                        'x': float(position[0]),
                        'y': float(position[1]),
                        'z': float(position[2])
                    },
                    'rotation_matrix': rmat.tolist(),
                    'corners': corners[i][0].tolist(),
                    'confidence': 1.0  # ArUco doesn't provide confidence
                }
                detections.append(detection)
        
        return detections


# Global AR Engine instance
engine = AREngine()


# ==========================================
# API ENDPOINTS
# ==========================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns
    -------
    JSON response with status and available features.
    """
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'features': {
            'apriltag': APRILTAG_AVAILABLE,
            'aruco': True
        }
    })


@app.route('/api/v1/config', methods=['POST'])
def configure_camera():
    """
    Configure camera calibration parameters.
    
    Request Body
    ------------
    {
        "image_width": int,
        "image_height": int,
        "fov_degrees": float (optional, default: 60.0),
        "dist_coeffs": [float] (optional, default: [0, 0, 0, 0, 0])
    }
    
    Returns
    -------
    JSON response with camera matrix and distortion coefficients.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        width = data.get('image_width')
        height = data.get('image_height')
        fov = data.get('fov_degrees', CONFIG['default_camera_fov'])
        dist_coeffs = data.get('dist_coeffs', None)
        
        if width is None or height is None:
            return jsonify({'error': 'image_width and image_height required'}), 400
        
        camera_matrix, dist_coeffs = engine.setup_camera_calibration(
            image_width=int(width),
            image_height=int(height),
            fov_degrees=float(fov),
            dist_coeffs=dist_coeffs
        )
        
        return jsonify({
            'status': 'configured',
            'camera_matrix': camera_matrix.tolist(),
            'dist_coeffs': dist_coeffs.tolist()
        })
    
    except Exception as e:
        logger.error(f"Configuration error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/detect', methods=['POST'])
def detect_markers():
    """
    Detect AR markers in an image.
    
    Request Body
    ------------
    {
        "image": str (base64-encoded image),
        "marker_type": str ("apriltag" or "aruco"),
        "marker_size": float (size in meters),
        "marker_count": int (expected number of markers, optional),
        "tag_family": str (for AprilTag, optional),
        "aruco_dict": str (for ArUco, optional)
    }
    
    Returns
    -------
    JSON response with detected markers and pose information.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Decode image
        image_b64 = data.get('image')
        if not image_b64:
            return jsonify({'error': 'image field required'}), 400
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_b64)
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if image is None:
                return jsonify({'error': 'Failed to decode image'}), 400
        except Exception as e:
            return jsonify({'error': f'Image decode error: {str(e)}'}), 400
        
        # Get detection parameters
        marker_type = data.get('marker_type', CONFIG['default_marker_type'])
        marker_size = float(data.get('marker_size', CONFIG['default_marker_size']))
        marker_count = data.get('marker_count', None)
        
        # Setup camera calibration if not already done
        if engine.camera_matrix is None:
            height, width = image.shape[:2]
            engine.setup_camera_calibration(
                image_width=width,
                image_height=height,
                fov_degrees=CONFIG['default_camera_fov']
            )
        
        # Detect markers based on type
        if marker_type.lower() == 'apriltag':
            tag_family = data.get('tag_family', CONFIG['default_tag_family'])
            detections = engine.detect_apriltag(image, marker_size, tag_family)
        
        elif marker_type.lower() == 'aruco':
            aruco_dict = data.get('aruco_dict', CONFIG['default_aruco_dict'])
            detections = engine.detect_aruco(image, marker_size, aruco_dict)
        
        else:
            return jsonify({'error': f'Unknown marker type: {marker_type}'}), 400
        
        # Filter by marker count if specified
        if marker_count is not None:
            if len(detections) < marker_count:
                logger.warning(
                    f"Expected {marker_count} markers, found {len(detections)}"
                )
        
        return jsonify({
            'status': 'success',
            'marker_type': marker_type,
            'marker_size': marker_size,
            'detected_count': len(detections),
            'expected_count': marker_count,
            'all_markers_found': (
                len(detections) >= marker_count if marker_count else True
            ),
            'detections': detections,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/supported_markers', methods=['GET'])
def get_supported_markers():
    """
    Get list of supported marker types and dictionaries.
    
    Returns
    -------
    JSON response with supported marker types and their options.
    """
    return jsonify({
        'marker_types': {
            'apriltag': {
                'available': APRILTAG_AVAILABLE,
                'families': [
                    'tag36h11',
                    'tag36h10',
                    'tag36h9',
                    'tag25h9',
                    'tag16h5',
                    'tagStandard41h12'
                ],
                'default': 'tag36h11'
            },
            'aruco': {
                'available': True,
                'dictionaries': list(ARUCO_DICT_MAP.keys()),
                'default': 'DICT_4X4_50'
            }
        }
    })


@app.route('/api/v1/generate_marker', methods=['POST'])
def generate_marker():
    """
    Generate a marker image.
    
    Request Body
    ------------
    {
        "marker_type": str ("apriltag" or "aruco"),
        "marker_id": int,
        "size_pixels": int (optional, default: 400),
        "tag_family": str (for AprilTag, optional),
        "aruco_dict": str (for ArUco, optional)
    }
    
    Returns
    -------
    PNG image of the marker.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        marker_type = data.get('marker_type', 'aruco')
        marker_id = int(data.get('marker_id', 0))
        size_pixels = int(data.get('size_pixels', 400))
        
        if marker_type.lower() == 'aruco':
            aruco_dict_name = data.get('aruco_dict', 'DICT_4X4_50')
            if aruco_dict_name not in ARUCO_DICT_MAP:
                return jsonify({'error': f'Unknown ArUco dictionary: {aruco_dict_name}'}), 400
            
            aruco_dict = cv2.aruco.getPredefinedDictionary(
                ARUCO_DICT_MAP[aruco_dict_name]
            )
            marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, size_pixels)
            
        elif marker_type.lower() == 'apriltag':
            # For AprilTag, we need external generation (not supported in OpenCV)
            return jsonify({
                'error': 'AprilTag generation not yet implemented. Use in-app generator.'
            }), 501
        
        else:
            return jsonify({'error': f'Unknown marker type: {marker_type}'}), 400
        
        # Encode image as PNG
        _, buffer = cv2.imencode('.png', marker_image)
        image_bytes = buffer.tobytes()
        
        return Response(image_bytes, mimetype='image/png')
    
    except Exception as e:
        logger.error(f"Marker generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==========================================
# MAIN
# ==========================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='AR Engine Backend API')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port number (default: 5000)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    
    args = parser.parse_args()
    
    logger.info(f"Starting AR Engine API on {args.host}:{args.port}")
    logger.info(f"AprilTag available: {APRILTAG_AVAILABLE}")
    logger.info(f"ArUco available: True")
    
    app.run(host=args.host, port=args.port, debug=args.debug)
