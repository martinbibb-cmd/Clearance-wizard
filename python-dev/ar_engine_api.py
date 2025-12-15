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
import uuid
import time
from functools import wraps
from collections import defaultdict
from werkzeug.datastructures import FileStorage

# Import AR detection modules
try:
    from vio.apriltag_detector import AprilTagDetector
    APRILTAG_AVAILABLE = True
except ImportError:
    APRILTAG_AVAILABLE = False
    print("Warning: AprilTag detector not available")

# Import OpenAPI spec
try:
    from openapi_spec import OPENAPI_SPEC
    from flask_swagger_ui import get_swaggerui_blueprint
    SWAGGER_AVAILABLE = True
except ImportError:
    SWAGGER_AVAILABLE = False
    print("Warning: Swagger UI not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Setup Swagger UI if available
if SWAGGER_AVAILABLE:
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/v1/openapi.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "AR Engine API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Global configuration
CONFIG = {
    'default_marker_type': 'apriltag',
    'default_tag_family': 'tag36h11',
    'default_aruco_dict': 'DICT_4X4_50',
    'default_marker_size': 0.19,  # 190mm in meters
    'default_camera_fov': 60.0,   # degrees
    'max_payload_size': 10 * 1024 * 1024,  # 10 MB
    'max_image_width': 4096,
    'max_image_height': 4096,
    'rate_limit_requests': 100,  # requests per minute
    'rate_limit_window': 60,  # seconds
}

# Session storage for request-scoped configurations
SESSIONS = {}

# Calibration storage
CALIBRATIONS = {}

# Rate limiting storage
RATE_LIMITS = defaultdict(list)

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


class SessionConfig:
    """
    Request-scoped configuration for AR detection.
    
    Attributes
    ----------
    session_id : str
        Unique session identifier.
    camera_matrix : np.ndarray
        Camera intrinsic matrix.
    dist_coeffs : np.ndarray
        Camera distortion coefficients.
    calibration_id : str or None
        Associated calibration identifier.
    created_at : datetime
        Session creation timestamp.
    last_accessed : datetime
        Last access timestamp.
    """
    
    def __init__(self, session_id: str = None):
        """
        Initialize a new session configuration.
        
        Parameters
        ----------
        session_id : str, optional
            Session identifier. Auto-generated if not provided.
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.camera_matrix = None
        self.dist_coeffs = None
        self.calibration_id = None
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
    
    def update_access_time(self):
        """Update last accessed timestamp."""
        self.last_accessed = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert session to dictionary.
        
        Returns
        -------
        dict
            Session configuration as dictionary.
        """
        return {
            'session_id': self.session_id,
            'calibration_id': self.calibration_id,
            'has_camera_matrix': self.camera_matrix is not None,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat()
        }


class CalibrationData:
    """
    Camera calibration data with versioning and persistence.
    
    Attributes
    ----------
    calibration_id : str
        Unique calibration identifier.
    camera_matrix : np.ndarray
        Camera intrinsic matrix.
    dist_coeffs : np.ndarray
        Camera distortion coefficients.
    image_width : int
        Image width in pixels.
    image_height : int
        Image height in pixels.
    fov_degrees : float
        Field of view in degrees.
    device_name : str
        Associated device/camera name.
    version : int
        Calibration version number.
    created_at : datetime
        Creation timestamp.
    """
    
    def __init__(
        self,
        camera_matrix: np.ndarray,
        dist_coeffs: np.ndarray,
        image_width: int,
        image_height: int,
        fov_degrees: float,
        device_name: str = "unknown",
        calibration_id: str = None
    ):
        """
        Initialize calibration data.
        
        Parameters
        ----------
        camera_matrix : np.ndarray
            Camera intrinsic matrix.
        dist_coeffs : np.ndarray
            Camera distortion coefficients.
        image_width : int
            Image width in pixels.
        image_height : int
            Image height in pixels.
        fov_degrees : float
            Field of view in degrees.
        device_name : str, optional
            Device/camera name.
        calibration_id : str, optional
            Calibration identifier. Auto-generated if not provided.
        """
        self.calibration_id = calibration_id or str(uuid.uuid4())
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.image_width = image_width
        self.image_height = image_height
        self.fov_degrees = fov_degrees
        self.device_name = device_name
        self.version = 1
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert calibration to dictionary.
        
        Returns
        -------
        dict
            Calibration data as dictionary.
        """
        return {
            'calibration_id': self.calibration_id,
            'camera_matrix': self.camera_matrix.tolist(),
            'dist_coeffs': self.dist_coeffs.tolist(),
            'image_width': self.image_width,
            'image_height': self.image_height,
            'fov_degrees': self.fov_degrees,
            'device_name': self.device_name,
            'version': self.version,
            'created_at': self.created_at.isoformat()
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
        
        # Detect markers (using OpenCV 4.7+ API)
        detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        corners, ids, rejected = detector.detectMarkers(gray)
        
        detections = []
        if ids is not None:
            # Estimate pose for each marker (using solvePnP for OpenCV 4.7+)
            # Object points in marker coordinate system (Z=0 plane)
            # OpenCV uses: X right, Y down, Z forward
            # Corner order from detectMarkers: [Top-Left, Top-Right, Bottom-Right, Bottom-Left]
            object_points = np.array([
                [-marker_size/2, -marker_size/2, 0],  # Top-left: X negative (left), Y negative (top)
                [marker_size/2, -marker_size/2, 0],   # Top-right: X positive (right), Y negative (top)
                [marker_size/2, marker_size/2, 0],    # Bottom-right: X positive (right), Y positive (bottom)
                [-marker_size/2, marker_size/2, 0]    # Bottom-left: X negative (left), Y positive (bottom)
            ], dtype=np.float32)
            
            rvecs = []
            tvecs = []
            for corner in corners:
                success, rvec, tvec = cv2.solvePnP(
                    object_points,
                    corner[0],
                    self.camera_matrix,
                    self.dist_coeffs,
                    flags=cv2.SOLVEPNP_IPPE_SQUARE
                )
                if success:
                    rvecs.append(rvec)
                    tvecs.append(tvec)
            
            for i, marker_id in enumerate(ids.flatten()):
                if i >= len(rvecs):
                    continue
                
                # Convert rotation vector to matrix
                rmat, _ = cv2.Rodrigues(rvecs[i])
                
                # Extract position and orientation
                position = tvecs[i].flatten()
                
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
# SECURITY MIDDLEWARE & HELPERS
# ==========================================

def check_rate_limit(client_id: str) -> Tuple[bool, int]:
    """
    Check if client has exceeded rate limit.
    
    Parameters
    ----------
    client_id : str
        Client identifier (IP address or session ID).
    
    Returns
    -------
    allowed : bool
        Whether request is allowed.
    remaining : int
        Remaining requests in current window.
    """
    current_time = time.time()
    window_start = current_time - CONFIG['rate_limit_window']
    
    # Clean old entries
    RATE_LIMITS[client_id] = [
        ts for ts in RATE_LIMITS[client_id] if ts > window_start
    ]
    
    # Check limit
    request_count = len(RATE_LIMITS[client_id])
    allowed = request_count < CONFIG['rate_limit_requests']
    
    if allowed:
        RATE_LIMITS[client_id].append(current_time)
    
    remaining = max(0, CONFIG['rate_limit_requests'] - request_count - 1)
    return allowed, remaining


def get_client_ip() -> str:
    """
    Get client IP address, checking X-Forwarded-For header for proxy support.
    
    Returns
    -------
    str
        Client IP address.
    """
    # Check X-Forwarded-For header (set by proxies/load balancers)
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, use the first one (client IP)
        return forwarded_for.split(',')[0].strip()
    
    # Fallback to remote_addr
    return request.remote_addr


def rate_limit_guard(f):
    """Decorator to enforce rate limiting on endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_id = get_client_ip()
        allowed, remaining = check_rate_limit(client_id)
        
        if not allowed:
            response = jsonify({
                'error': 'Rate limit exceeded',
                'retry_after': CONFIG['rate_limit_window']
            })
            response.headers['X-RateLimit-Limit'] = str(CONFIG['rate_limit_requests'])
            response.headers['X-RateLimit-Remaining'] = '0'
            response.headers['Retry-After'] = str(CONFIG['rate_limit_window'])
            return response, 429
        
        result = f(*args, **kwargs)
        
        # Add rate limit headers to response
        if isinstance(result, tuple):
            resp_obj, status_code = result[0], result[1]
            if isinstance(resp_obj, Response):
                resp_obj.headers['X-RateLimit-Limit'] = str(CONFIG['rate_limit_requests'])
                resp_obj.headers['X-RateLimit-Remaining'] = str(remaining)
                return resp_obj, status_code
        elif isinstance(result, Response):
            result.headers['X-RateLimit-Limit'] = str(CONFIG['rate_limit_requests'])
            result.headers['X-RateLimit-Remaining'] = str(remaining)
            return result
        
        # For jsonify responses, wrap to add headers
        response = result if isinstance(result, Response) else result
        if hasattr(response, 'headers'):
            response.headers['X-RateLimit-Limit'] = str(CONFIG['rate_limit_requests'])
            response.headers['X-RateLimit-Remaining'] = str(remaining)
        
        return result
    return decorated_function


def validate_image_dimensions(image: np.ndarray, warnings: List[str]) -> bool:
    """
    Validate image dimensions against security limits.
    
    Parameters
    ----------
    image : np.ndarray
        Input image.
    warnings : list
        List to append warnings to.
    
    Returns
    -------
    bool
        Whether image dimensions are valid.
    """
    height, width = image.shape[:2]
    
    if width > CONFIG['max_image_width'] or height > CONFIG['max_image_height']:
        warnings.append(
            f"Image dimensions {width}x{height} exceed maximum "
            f"{CONFIG['max_image_width']}x{CONFIG['max_image_height']}"
        )
        return False
    
    return True


def get_or_create_session(session_id: Optional[str] = None) -> SessionConfig:
    """
    Get existing session or create new one.
    
    Parameters
    ----------
    session_id : str, optional
        Session identifier.
    
    Returns
    -------
    SessionConfig
        Session configuration object.
    """
    if session_id and session_id in SESSIONS:
        session = SESSIONS[session_id]
        session.update_access_time()
        return session
    
    # Create new session
    session = SessionConfig(session_id)
    SESSIONS[session.session_id] = session
    return session


def create_transform_matrix(rvec: np.ndarray, tvec: np.ndarray) -> np.ndarray:
    """
    Create 4x4 transformation matrix from rotation and translation vectors.
    
    Parameters
    ----------
    rvec : np.ndarray
        Rotation vector.
    tvec : np.ndarray
        Translation vector.
    
    Returns
    -------
    np.ndarray
        4x4 transformation matrix.
    """
    rmat, _ = cv2.Rodrigues(rvec)
    transform = np.eye(4)
    transform[:3, :3] = rmat
    transform[:3, 3] = tvec.flatten()
    return transform


def format_detection_response(
    detections: List[Dict[str, Any]],
    marker_type: str,
    marker_size: float,
    timings: Dict[str, float],
    camera_info: Dict[str, Any],
    warnings: List[str],
    session_id: str = None,
    calibration_id: str = None
) -> Dict[str, Any]:
    """
    Format detection response with standardized schema.
    
    Parameters
    ----------
    detections : list of dict
        Raw detection results.
    marker_type : str
        Type of marker detected.
    marker_size : float
        Physical marker size.
    timings : dict
        Timing information in milliseconds.
    camera_info : dict
        Camera configuration info.
    warnings : list
        Warning messages.
    session_id : str, optional
        Session identifier.
    calibration_id : str, optional
        Calibration identifier.
    
    Returns
    -------
    dict
        Standardized response.
    """
    # Sort detections by ID for deterministic ordering
    sorted_detections = sorted(detections, key=lambda x: x.get('id', 0))
    
    # Enhance detections with transform matrices
    for detection in sorted_detections:
        if 'rotation_matrix' in detection and 'position' in detection:
            # Create rvec from rotation matrix
            rmat = np.array(detection['rotation_matrix'])
            rvec, _ = cv2.Rodrigues(rmat)
            tvec = np.array([
                detection['position']['x'],
                detection['position']['y'],
                detection['position']['z']
            ])
            
            # Add rvec/tvec
            detection['rvec'] = rvec.flatten().tolist()
            detection['tvec'] = tvec.flatten().tolist()
            
            # Add 4x4 transform matrix
            transform = create_transform_matrix(rvec, tvec)
            detection['transform_matrix'] = transform.tolist()
    
    return {
        'status': 'success',
        'markers': sorted_detections,
        'marker_count': len(sorted_detections),
        'marker_type': marker_type,
        'marker_size': marker_size,
        'timings_ms': timings,
        'camera': camera_info,
        'warnings': warnings,
        'session_id': session_id,
        'calibration_id': calibration_id,
        'timestamp': datetime.now().isoformat()
    }


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
        'timestamp': datetime.now().isoformat(),
        'features': {
            'apriltag': APRILTAG_AVAILABLE,
            'aruco': True,
            'multipart_upload': True,
            'session_management': True,
            'calibration_persistence': True
        }
    })


@app.route('/api/v1/status', methods=['GET'])
def get_status():
    """
    Get API status including session and calibration information.
    
    Query Parameters
    ----------------
    session_id : str, optional
        Session identifier to get specific session status.
    
    Returns
    -------
    JSON response with API status, sessions, and calibrations.
    """
    session_id = request.args.get('session_id', None)
    
    response = {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(SESSIONS),
        'stored_calibrations': len(CALIBRATIONS),
        'features': {
            'apriltag': APRILTAG_AVAILABLE,
            'aruco': True,
            'multipart_upload': True,
            'session_management': True,
            'calibration_persistence': True
        }
    }
    
    # Add session details if requested
    if session_id and session_id in SESSIONS:
        session = SESSIONS[session_id]
        response['session'] = session.to_dict()
    
    return jsonify(response)


@app.route('/api/v1/calibrations', methods=['GET'])
def list_calibrations():
    """
    List all stored calibrations.
    
    Returns
    -------
    JSON response with list of calibrations.
    """
    calibrations = [calib.to_dict() for calib in CALIBRATIONS.values()]
    return jsonify({
        'calibrations': calibrations,
        'count': len(calibrations)
    })


@app.route('/api/v1/calibrations/<calibration_id>', methods=['GET'])
def get_calibration(calibration_id: str):
    """
    Get specific calibration by ID.
    
    Parameters
    ----------
    calibration_id : str
        Calibration identifier.
    
    Returns
    -------
    JSON response with calibration data.
    """
    if calibration_id not in CALIBRATIONS:
        return jsonify({'error': 'Calibration not found'}), 404
    
    calib = CALIBRATIONS[calibration_id]
    return jsonify(calib.to_dict())


@app.route('/api/v1/openapi.json', methods=['GET'])
def get_openapi_spec():
    """
    Get OpenAPI specification.
    
    Returns
    -------
    JSON response with OpenAPI specification.
    """
    if not SWAGGER_AVAILABLE:
        return jsonify({'error': 'OpenAPI documentation not available'}), 501
    
    return jsonify(OPENAPI_SPEC)


@app.route('/api/v1/config', methods=['POST'])
@rate_limit_guard
def configure_camera():
    """
    Configure camera calibration parameters (request-scoped).
    
    Request Body
    ------------
    {
        "image_width": int,
        "image_height": int,
        "fov_degrees": float (optional, default: 60.0),
        "dist_coeffs": [float] (optional, default: [0, 0, 0, 0, 0]),
        "session_id": str (optional),
        "device_name": str (optional),
        "save_calibration": bool (optional, default: false)
    }
    
    Returns
    -------
    JSON response with camera matrix, distortion coefficients, session_id, and calibration_id.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        width = data.get('image_width')
        height = data.get('image_height')
        fov = data.get('fov_degrees', CONFIG['default_camera_fov'])
        dist_coeffs_input = data.get('dist_coeffs', None)
        session_id = data.get('session_id', None)
        device_name = data.get('device_name', 'unknown')
        save_calibration = data.get('save_calibration', False)
        
        if width is None or height is None:
            return jsonify({'error': 'image_width and image_height required'}), 400
        
        # Get or create session
        session = get_or_create_session(session_id)
        
        # Setup calibration
        camera_matrix, dist_coeffs = engine.setup_camera_calibration(
            image_width=int(width),
            image_height=int(height),
            fov_degrees=float(fov),
            dist_coeffs=dist_coeffs_input
        )
        
        # Store in session
        session.camera_matrix = camera_matrix
        session.dist_coeffs = dist_coeffs
        
        # Create calibration data if requested
        calibration_id = None
        if save_calibration:
            calibration = CalibrationData(
                camera_matrix=camera_matrix,
                dist_coeffs=dist_coeffs,
                image_width=int(width),
                image_height=int(height),
                fov_degrees=float(fov),
                device_name=device_name
            )
            CALIBRATIONS[calibration.calibration_id] = calibration
            session.calibration_id = calibration.calibration_id
            calibration_id = calibration.calibration_id
        
        return jsonify({
            'status': 'configured',
            'session_id': session.session_id,
            'calibration_id': calibration_id,
            'camera_matrix': camera_matrix.tolist(),
            'dist_coeffs': dist_coeffs.tolist()
        })
    
    except Exception as e:
        logger.error(f"Configuration error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/detect', methods=['POST'])
@rate_limit_guard
def detect_markers():
    """
    Detect AR markers in an image.
    
    Supports both multipart/form-data and JSON (base64) uploads.
    
    Request Body (multipart/form-data)
    -----------------------------------
    - image: file (image file)
    - marker_type: str ("apriltag" or "aruco")
    - marker_size: float (size in meters)
    - marker_count: int (expected number of markers, optional)
    - tag_family: str (for AprilTag, optional)
    - aruco_dict: str (for ArUco, optional)
    - session_id: str (optional)
    - calibration_id: str (optional)
    
    Request Body (JSON)
    -------------------
    {
        "image": str (base64-encoded image),
        "marker_type": str ("apriltag" or "aruco"),
        "marker_size": float (size in meters),
        "marker_count": int (expected number of markers, optional),
        "tag_family": str (for AprilTag, optional),
        "aruco_dict": str (for ArUco, optional),
        "session_id": str (optional),
        "calibration_id": str (optional)
    }
    
    Returns
    -------
    JSON response with detected markers, timings, camera info, and warnings.
    """
    start_time = time.time()
    timings = {}
    warnings = []
    image = None
    
    try:
        # Check payload size
        if request.content_length and request.content_length > CONFIG['max_payload_size']:
            return jsonify({
                'error': f'Payload too large. Maximum size: {CONFIG["max_payload_size"]} bytes'
            }), 413
        
        # Parse request based on content type
        is_multipart = request.content_type and 'multipart/form-data' in request.content_type
        
        if is_multipart:
            # Handle multipart/form-data
            decode_start = time.time()
            
            if 'image' not in request.files:
                return jsonify({'error': 'image file required in multipart upload'}), 400
            
            file = request.files['image']
            image_bytes = file.read()
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if image is None:
                return jsonify({'error': 'Failed to decode uploaded image'}), 400
            
            # Get parameters from form data
            marker_type = request.form.get('marker_type', CONFIG['default_marker_type'])
            marker_size = float(request.form.get('marker_size', CONFIG['default_marker_size']))
            marker_count = request.form.get('marker_count', None)
            if marker_count is not None:
                marker_count = int(marker_count)
            tag_family = request.form.get('tag_family', CONFIG['default_tag_family'])
            aruco_dict = request.form.get('aruco_dict', CONFIG['default_aruco_dict'])
            session_id = request.form.get('session_id', None)
            calibration_id = request.form.get('calibration_id', None)
            
            timings['image_decode_ms'] = (time.time() - decode_start) * 1000
        else:
            # Handle JSON with base64
            decode_start = time.time()
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            image_b64 = data.get('image')
            if not image_b64:
                return jsonify({'error': 'image field required'}), 400
            
            try:
                image_bytes = base64.b64decode(image_b64)
                image_array = np.frombuffer(image_bytes, dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                
                if image is None:
                    return jsonify({'error': 'Failed to decode image'}), 400
            except Exception as e:
                return jsonify({'error': f'Image decode error: {str(e)}'}), 400
            
            # Get parameters from JSON
            marker_type = data.get('marker_type', CONFIG['default_marker_type'])
            marker_size = float(data.get('marker_size', CONFIG['default_marker_size']))
            marker_count = data.get('marker_count', None)
            tag_family = data.get('tag_family', CONFIG['default_tag_family'])
            aruco_dict = data.get('aruco_dict', CONFIG['default_aruco_dict'])
            session_id = data.get('session_id', None)
            calibration_id = data.get('calibration_id', None)
            
            timings['image_decode_ms'] = (time.time() - decode_start) * 1000
        
        # Validate image dimensions
        if not validate_image_dimensions(image, warnings):
            return jsonify({
                'error': 'Image dimensions exceed security limits',
                'warnings': warnings
            }), 400
        
        # Get or create session
        session = get_or_create_session(session_id)
        
        # Load calibration if specified
        if calibration_id and calibration_id in CALIBRATIONS:
            calib = CALIBRATIONS[calibration_id]
            session.camera_matrix = calib.camera_matrix
            session.dist_coeffs = calib.dist_coeffs
            session.calibration_id = calibration_id
        
        # Setup camera calibration for this session
        calibration_start = time.time()
        if session.camera_matrix is None:
            height, width = image.shape[:2]
            camera_matrix, dist_coeffs = engine.setup_camera_calibration(
                image_width=width,
                image_height=height,
                fov_degrees=CONFIG['default_camera_fov']
            )
            session.camera_matrix = camera_matrix
            session.dist_coeffs = dist_coeffs
            warnings.append("Camera calibration auto-configured from image dimensions")
        else:
            engine.camera_matrix = session.camera_matrix
            engine.dist_coeffs = session.dist_coeffs
        
        timings['calibration_setup_ms'] = (time.time() - calibration_start) * 1000
        
        # Detect markers based on type
        detection_start = time.time()
        if marker_type.lower() == 'apriltag':
            detections = engine.detect_apriltag(image, marker_size, tag_family)
        elif marker_type.lower() == 'aruco':
            detections = engine.detect_aruco(image, marker_size, aruco_dict)
        else:
            return jsonify({'error': f'Unknown marker type: {marker_type}'}), 400
        
        timings['detection_ms'] = (time.time() - detection_start) * 1000
        
        # Check marker count
        if marker_count is not None and len(detections) < marker_count:
            warnings.append(
                f"Expected {marker_count} markers, found {len(detections)}"
            )
        
        # Prepare camera info
        camera_info = {
            'width': image.shape[1],
            'height': image.shape[0],
            'calibrated': True,
            'calibration_id': session.calibration_id
        }
        
        # Total timing
        timings['total_ms'] = (time.time() - start_time) * 1000
        
        # Format response
        response = format_detection_response(
            detections=detections,
            marker_type=marker_type,
            marker_size=marker_size,
            timings=timings,
            camera_info=camera_info,
            warnings=warnings,
            session_id=session.session_id,
            calibration_id=session.calibration_id
        )
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        return jsonify({
            'error': str(e),
            'warnings': warnings
        }), 500


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
