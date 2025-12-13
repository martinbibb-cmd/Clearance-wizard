"""
AprilTag Detector Module

This module provides the AprilTagDetector class for detecting AprilTags in images
and estimating their 3D pose using Perspective-n-Point (PnP) algorithm.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import apriltag
except ImportError:
    apriltag = None


class AprilTagDetector:
    """
    Handles reading images, detecting AprilTags, and estimating their 3D pose.
    
    This class detects AprilTags of the tagStandard41h12 family and performs
    PnP (Perspective-n-Point) to return the 3D position and orientation
    (translation vector and rotation matrix) relative to the camera.
    
    Parameters
    ----------
    tag_size : float
        Physical size of the AprilTag in meters (measured as the width of the
        black square area, excluding the white border).
    camera_matrix : np.ndarray
        3x3 camera intrinsic matrix containing focal lengths and principal point.
    dist_coeffs : np.ndarray
        Camera distortion coefficients (k1, k2, p1, p2, k3).
    tag_family : str, optional
        AprilTag family to detect. Default is 'tagStandard41h12'.
        Other options: 'tag36h11', 'tag25h9', 'tag16h5', etc.
    
    Attributes
    ----------
    tag_size : float
        Physical size of the AprilTag in meters.
    camera_matrix : np.ndarray
        Camera intrinsic matrix.
    dist_coeffs : np.ndarray
        Camera distortion coefficients.
    detector : apriltag.Detector
        AprilTag detector instance.
    """
    
    def __init__(
        self,
        tag_size: float,
        camera_matrix: np.ndarray,
        dist_coeffs: np.ndarray,
        tag_family: str = 'tagStandard41h12'
    ):
        """Initialize the AprilTag detector with camera calibration parameters."""
        if apriltag is None:
            raise ImportError(
                "apriltag library not found. Install it with: pip install apriltag"
            )
        if cv2 is None:
            raise ImportError(
                "OpenCV not found. Install it with: pip install opencv-python"
            )
        
        self.tag_size = tag_size
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        
        # Initialize AprilTag detector
        options = apriltag.DetectorOptions(families=tag_family)
        self.detector = apriltag.Detector(options)
        
        # Define 3D coordinates of tag corners in tag's coordinate system
        # Tag is centered at origin, lying in XY plane
        half_size = tag_size / 2.0
        self.object_points = np.array([
            [-half_size, -half_size, 0],  # Bottom-left
            [ half_size, -half_size, 0],  # Bottom-right
            [ half_size,  half_size, 0],  # Top-right
            [-half_size,  half_size, 0],  # Top-left
        ], dtype=np.float32)
    
    def detect(self, image: np.ndarray) -> List[Dict[str, any]]:
        """
        Detect all AprilTags in the image and estimate their 3D pose.
        
        Parameters
        ----------
        image : np.ndarray
            Input image (can be color or grayscale).
        
        Returns
        -------
        List[Dict[str, any]]
            List of detected tags, where each tag is a dictionary containing:
            - 'tag_id': int - Unique identifier of the detected tag
            - 'center': np.ndarray - 2D center position in image (x, y)
            - 'corners': np.ndarray - 4x2 array of corner positions
            - 'translation': np.ndarray - 3D translation vector (tx, ty, tz)
            - 'rotation_matrix': np.ndarray - 3x3 rotation matrix
            - 'rotation_vector': np.ndarray - 3D rotation vector (Rodrigues)
        
        Examples
        --------
        >>> detector = AprilTagDetector(tag_size=0.19, camera_matrix=K, dist_coeffs=D)
        >>> detections = detector.detect(image)
        >>> for detection in detections:
        ...     print(f"Tag {detection['tag_id']}: Position {detection['translation']}")
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Detect AprilTags
        results = self.detector.detect(gray)
        
        detections = []
        for result in results:
            # Get 2D corner positions in image
            image_points = result.corners.astype(np.float32)
            
            # Solve PnP to get pose
            success, rvec, tvec = cv2.solvePnP(
                self.object_points,
                image_points,
                self.camera_matrix,
                self.dist_coeffs,
                flags=cv2.SOLVEPNP_IPPE_SQUARE  # Best for planar objects
            )
            
            if success:
                # Convert rotation vector to rotation matrix
                rotation_matrix, _ = cv2.Rodrigues(rvec)
                
                detection = {
                    'tag_id': result.tag_id,
                    'center': result.center,
                    'corners': result.corners,
                    'translation': tvec.flatten(),
                    'rotation_matrix': rotation_matrix,
                    'rotation_vector': rvec.flatten(),
                    'hamming': result.hamming,  # Error metric (lower is better)
                    'decision_margin': result.decision_margin,  # Confidence metric
                }
                detections.append(detection)
        
        return detections
    
    def get_pose_from_tag_id(
        self,
        detections: List[Dict[str, any]],
        tag_id: int
    ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Extract pose (translation and rotation) for a specific tag ID.
        
        Parameters
        ----------
        detections : List[Dict[str, any]]
            List of detections from detect() method.
        tag_id : int
            Tag ID to search for.
        
        Returns
        -------
        Optional[Tuple[np.ndarray, np.ndarray]]
            Tuple of (translation_vector, rotation_matrix) if tag found,
            None otherwise.
        """
        for detection in detections:
            if detection['tag_id'] == tag_id:
                return detection['translation'], detection['rotation_matrix']
        return None
    
    def visualize_detections(
        self,
        image: np.ndarray,
        detections: List[Dict[str, any]],
        draw_axes: bool = True,
        axis_length: float = None
    ) -> np.ndarray:
        """
        Draw detected tags and their coordinate axes on the image.
        
        Parameters
        ----------
        image : np.ndarray
            Input image to draw on (will be copied).
        detections : List[Dict[str, any]]
            List of detections from detect() method.
        draw_axes : bool, optional
            Whether to draw 3D coordinate axes. Default is True.
        axis_length : float, optional
            Length of coordinate axes in meters. Default is tag_size.
        
        Returns
        -------
        np.ndarray
            Image with visualizations drawn.
        """
        vis_image = image.copy()
        
        if axis_length is None:
            axis_length = self.tag_size
        
        for detection in detections:
            # Draw tag corners
            corners = detection['corners'].astype(int)
            cv2.polylines(vis_image, [corners], True, (0, 255, 0), 2)
            
            # Draw tag ID
            center = detection['center'].astype(int)
            cv2.putText(
                vis_image,
                f"ID: {detection['tag_id']}",
                (center[0] - 20, center[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
            
            # Draw 3D coordinate axes
            if draw_axes:
                # Define 3D points for axes
                axis_points = np.float32([
                    [0, 0, 0],              # Origin
                    [axis_length, 0, 0],    # X-axis (red)
                    [0, axis_length, 0],    # Y-axis (green)
                    [0, 0, -axis_length]    # Z-axis (blue) - note negative for right-hand rule
                ])
                
                # Project 3D points to image plane
                image_points, _ = cv2.projectPoints(
                    axis_points,
                    detection['rotation_vector'],
                    detection['translation'],
                    self.camera_matrix,
                    self.dist_coeffs
                )
                image_points = image_points.reshape(-1, 2).astype(int)
                
                # Draw axes
                origin = tuple(image_points[0])
                cv2.line(vis_image, origin, tuple(image_points[1]), (0, 0, 255), 2)  # X: Red
                cv2.line(vis_image, origin, tuple(image_points[2]), (0, 255, 0), 2)  # Y: Green
                cv2.line(vis_image, origin, tuple(image_points[3]), (255, 0, 0), 2)  # Z: Blue
        
        return vis_image
    
    @staticmethod
    def create_default_camera_matrix(
        image_width: int,
        image_height: int,
        fov_degrees: float = 60.0
    ) -> np.ndarray:
        """
        Create a default camera matrix based on image dimensions and field of view.
        
        This is useful for testing when exact camera calibration is not available.
        For production use, perform proper camera calibration.
        
        Parameters
        ----------
        image_width : int
            Image width in pixels.
        image_height : int
            Image height in pixels.
        fov_degrees : float, optional
            Vertical field of view in degrees. Default is 60.
        
        Returns
        -------
        np.ndarray
            3x3 camera intrinsic matrix.
        """
        # Calculate focal length from FOV
        fov_rad = np.deg2rad(fov_degrees)
        focal_length = image_height / (2.0 * np.tan(fov_rad / 2.0))
        
        # Principal point at image center
        cx = image_width / 2.0
        cy = image_height / 2.0
        
        camera_matrix = np.array([
            [focal_length, 0, cx],
            [0, focal_length, cy],
            [0, 0, 1]
        ], dtype=np.float32)
        
        return camera_matrix
