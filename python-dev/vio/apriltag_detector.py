"""
AprilTag Detector Module

This module provides the AprilTagDetector class for detecting AprilTags in images
and estimating their 3D pose using Perspective-n-Point (PnP) algorithm.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any

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
    
    Includes stability improvements for near-field tracking:
    - Minimum distance enforcement
    - Pose continuity checking with solvePnPGeneric
    - Temporal smoothing to reduce jitter
    - Adaptive rejection thresholds
    
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
    min_distance : float, optional
        Minimum distance in meters for stable pose estimation.
        Default is 2 * tag_size (recommended rule of thumb).
    max_reprojection_error : float, optional
        Maximum allowed reprojection error in pixels. Default is 5.0.
        Near-field markers naturally have higher error.
    smoothing_alpha : float, optional
        Smoothing factor for temporal filtering (0-1). Default is 0.3.
        0 = no smoothing, 1 = use only new measurement.
    lost_timeout_frames : int, optional
        Number of frames to wait before declaring marker lost. Default is 5.
    
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
    previous_poses : dict
        Dictionary storing previous poses for each tag_id for continuity.
    tracking_state : dict
        Dictionary storing tracking state (frames_lost) for each tag_id.
    """
    
    def __init__(
        self,
        tag_size: float,
        camera_matrix: np.ndarray,
        dist_coeffs: np.ndarray,
        tag_family: str = 'tagStandard41h12',
        min_distance: Optional[float] = None,
        max_reprojection_error: float = 5.0,
        smoothing_alpha: float = 0.3,
        lost_timeout_frames: int = 5
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
        
        # Stability parameters
        self.min_distance = min_distance if min_distance is not None else 2.0 * tag_size
        self.max_reprojection_error = max_reprojection_error
        self.smoothing_alpha = smoothing_alpha
        self.lost_timeout_frames = lost_timeout_frames
        
        # Tracking state
        self.previous_poses = {}  # tag_id -> (tvec, rvec)
        self.tracking_state = {}  # tag_id -> frames_lost
        
        # Initialize AprilTag detector
        options = apriltag.DetectorOptions(families=tag_family)
        self.detector = apriltag.Detector(options)
        
        # Define 3D coordinates of tag corners in tag's coordinate system
        # Tag is centered at origin, lying in XY plane (Z=0)
        # OpenCV coordinate system: X right, Y down, Z forward
        # Corner order from apriltag library: [Top-Left, Top-Right, Bottom-Right, Bottom-Left]
        half_size = tag_size / 2.0
        self.object_points = np.array([
            [-half_size, -half_size, 0],  # Top-left (X negative=left, Y negative=top)
            [ half_size, -half_size, 0],  # Top-right (X positive=right, Y negative=top)
            [ half_size,  half_size, 0],  # Bottom-right (X positive=right, Y positive=bottom)
            [-half_size,  half_size, 0],  # Bottom-left (X negative=left, Y positive=bottom)
        ], dtype=np.float32)
    
    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect all AprilTags in the image and estimate their 3D pose.
        
        Implements stability improvements:
        - Uses solvePnPGeneric to get multiple pose solutions
        - Selects solution with minimal change from previous frame
        - Applies temporal smoothing to reduce jitter
        - Validates minimum distance and reprojection error
        - Maintains tracking state with timeout
        
        Parameters
        ----------
        image : np.ndarray
            Input image (can be color or grayscale).
        
        Returns
        -------
        List[Dict[str, Any]]
            List of detected tags, where each tag is a dictionary containing:
            - 'tag_id': int - Unique identifier of the detected tag
            - 'center': np.ndarray - 2D center position in image (x, y)
            - 'corners': np.ndarray - 4x2 array of corner positions
            - 'translation': np.ndarray - 3D translation vector (tx, ty, tz)
            - 'rotation_matrix': np.ndarray - 3x3 rotation matrix
            - 'rotation_vector': np.ndarray - 3D rotation vector (Rodrigues)
            - 'tracking_status': str - 'detected', 'tracking', or 'lost'
            - 'reprojection_error': float - Reprojection error in pixels
        
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
        
        # Track which tags were detected this frame
        detected_tag_ids = set()
        
        detections = []
        for result in results:
            tag_id = result.tag_id
            detected_tag_ids.add(tag_id)
            
            # Get 2D corner positions in image
            image_points = result.corners.astype(np.float32)
            
            # Use solvePnPGeneric to get all possible solutions
            # This helps handle corner order ambiguity
            success, rvecs, tvecs, reprojection_errors = cv2.solvePnPGeneric(
                self.object_points,
                image_points,
                self.camera_matrix,
                self.dist_coeffs,
                flags=cv2.SOLVEPNP_IPPE_SQUARE  # Best for planar objects
            )
            
            if not success or len(rvecs) == 0:
                continue
            
            # Select best solution based on continuity with previous frame
            best_rvec, best_tvec, best_idx = self._select_best_pose(
                tag_id, rvecs, tvecs
            )
            
            # Validate distance
            distance = np.linalg.norm(best_tvec)
            if distance < self.min_distance:
                # Too close - skip this detection
                continue
            
            # Calculate reprojection error for the selected solution
            if len(reprojection_errors) > best_idx:
                reproj_error = reprojection_errors[best_idx][0]
            else:
                # Calculate manually if not provided
                reproj_error = self._calculate_reprojection_error(
                    best_rvec, best_tvec, image_points
                )
            
            # Validate reprojection error with distance-aware threshold
            # Near-field markers can have higher error, so scale threshold
            distance_factor = max(1.0, self.min_distance / distance)
            adjusted_threshold = self.max_reprojection_error * distance_factor
            
            if reproj_error > adjusted_threshold:
                # Reprojection error too high - skip
                continue
            
            # Apply temporal smoothing if we have a previous pose
            if tag_id in self.previous_poses:
                prev_tvec, prev_rvec = self.previous_poses[tag_id]
                best_tvec = self._smooth_pose(prev_tvec, best_tvec)
                best_rvec = self._smooth_rotation(prev_rvec, best_rvec)
                tracking_status = 'tracking'
            else:
                tracking_status = 'detected'
            
            # Store current pose for next frame
            self.previous_poses[tag_id] = (best_tvec.copy(), best_rvec.copy())
            self.tracking_state[tag_id] = 0  # Reset lost counter
            
            # Convert rotation vector to rotation matrix
            rotation_matrix, _ = cv2.Rodrigues(best_rvec)
            
            detection = {
                'tag_id': tag_id,
                'center': result.center,
                'corners': result.corners,
                'translation': best_tvec.flatten(),
                'rotation_matrix': rotation_matrix,
                'rotation_vector': best_rvec.flatten(),
                'hamming': result.hamming,  # Error metric (lower is better)
                'decision_margin': result.decision_margin,  # Confidence metric
                'tracking_status': tracking_status,
                'reprojection_error': reproj_error,
            }
            detections.append(detection)
        
        # Update tracking state for tags not detected this frame
        self._update_lost_tags(detected_tag_ids)
        
        return detections
    
    def _select_best_pose(
        self,
        tag_id: int,
        rvecs: List[np.ndarray],
        tvecs: List[np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray, int]:
        """
        Select the best pose from multiple solutions.
        
        If we have a previous pose, select the solution closest to it.
        Otherwise, select the solution with positive Z (in front of camera).
        
        Parameters
        ----------
        tag_id : int
            Tag ID for tracking.
        rvecs : List[np.ndarray]
            List of rotation vectors from solvePnPGeneric.
        tvecs : List[np.ndarray]
            List of translation vectors from solvePnPGeneric.
        
        Returns
        -------
        Tuple[np.ndarray, np.ndarray, int]
            Best rotation vector, translation vector, and index.
        """
        if tag_id in self.previous_poses:
            # Select solution with minimal change from previous frame
            prev_tvec, prev_rvec = self.previous_poses[tag_id]
            
            min_delta = float('inf')
            best_idx = 0
            
            for i, (rvec, tvec) in enumerate(zip(rvecs, tvecs)):
                # Calculate position delta
                pos_delta = np.linalg.norm(tvec - prev_tvec)
                
                # Calculate rotation delta (angle between rotations)
                rot_delta = self._rotation_distance(prev_rvec, rvec)
                
                # Combined metric (weighted)
                total_delta = pos_delta + 0.5 * rot_delta
                
                if total_delta < min_delta:
                    min_delta = total_delta
                    best_idx = i
        else:
            # No previous pose - select solution with positive Z and reject mirrors
            best_idx = 0
            best_z = tvecs[0][2, 0]
            
            for i, tvec in enumerate(tvecs):
                z = tvec[2, 0]
                # Prefer positive Z (in front of camera) and larger Z values
                if z > best_z:
                    best_z = z
                    best_idx = i
        
        return rvecs[best_idx], tvecs[best_idx], best_idx
    
    def _rotation_distance(self, rvec1: np.ndarray, rvec2: np.ndarray) -> float:
        """
        Calculate angular distance between two rotation vectors.
        
        Parameters
        ----------
        rvec1 : np.ndarray
            First rotation vector.
        rvec2 : np.ndarray
            Second rotation vector.
        
        Returns
        -------
        float
            Angular distance in radians.
        """
        # Convert to rotation matrices
        R1, _ = cv2.Rodrigues(rvec1)
        R2, _ = cv2.Rodrigues(rvec2)
        
        # Calculate relative rotation
        R_delta = R1.T @ R2
        
        # Extract angle from rotation matrix
        trace = np.trace(R_delta)
        angle = np.arccos(np.clip((trace - 1) / 2, -1, 1))
        
        return angle
    
    def _smooth_pose(self, prev_tvec: np.ndarray, new_tvec: np.ndarray) -> np.ndarray:
        """
        Apply exponential smoothing to translation vector.
        
        Parameters
        ----------
        prev_tvec : np.ndarray
            Previous translation vector.
        new_tvec : np.ndarray
            New translation vector.
        
        Returns
        -------
        np.ndarray
            Smoothed translation vector.
        """
        alpha = self.smoothing_alpha
        return alpha * new_tvec + (1 - alpha) * prev_tvec
    
    def _smooth_rotation(self, prev_rvec: np.ndarray, new_rvec: np.ndarray) -> np.ndarray:
        """
        Apply SLERP-like smoothing to rotation vector.
        
        Parameters
        ----------
        prev_rvec : np.ndarray
            Previous rotation vector.
        new_rvec : np.ndarray
            New rotation vector.
        
        Returns
        -------
        np.ndarray
            Smoothed rotation vector.
        """
        # Simple linear interpolation in rotation vector space
        # For better results, could use SLERP in quaternion space
        alpha = self.smoothing_alpha
        return alpha * new_rvec + (1 - alpha) * prev_rvec
    
    def _calculate_reprojection_error(
        self,
        rvec: np.ndarray,
        tvec: np.ndarray,
        image_points: np.ndarray
    ) -> float:
        """
        Calculate reprojection error for a pose.
        
        Parameters
        ----------
        rvec : np.ndarray
            Rotation vector.
        tvec : np.ndarray
            Translation vector.
        image_points : np.ndarray
            Observed 2D corner positions.
        
        Returns
        -------
        float
            RMS reprojection error in pixels.
        """
        # Project 3D points to 2D
        projected, _ = cv2.projectPoints(
            self.object_points,
            rvec,
            tvec,
            self.camera_matrix,
            self.dist_coeffs
        )
        projected = projected.reshape(-1, 2)
        
        # Calculate RMS error
        errors = np.linalg.norm(projected - image_points, axis=1)
        return np.sqrt(np.mean(errors ** 2))
    
    def _update_lost_tags(self, detected_tag_ids: set):
        """
        Update tracking state for tags not detected this frame.
        
        Parameters
        ----------
        detected_tag_ids : set
            Set of tag IDs detected in current frame.
        """
        # Increment lost counter for tags not detected
        for tag_id in list(self.tracking_state.keys()):
            if tag_id not in detected_tag_ids:
                self.tracking_state[tag_id] += 1
                
                # Remove from tracking if lost for too long
                if self.tracking_state[tag_id] > self.lost_timeout_frames:
                    del self.tracking_state[tag_id]
                    if tag_id in self.previous_poses:
                        del self.previous_poses[tag_id]
    
    def reset_tracking(self, tag_id: Optional[int] = None):
        """
        Reset tracking state for a specific tag or all tags.
        
        Parameters
        ----------
        tag_id : int, optional
            Tag ID to reset. If None, reset all tags.
        """
        if tag_id is None:
            self.previous_poses.clear()
            self.tracking_state.clear()
        else:
            if tag_id in self.previous_poses:
                del self.previous_poses[tag_id]
            if tag_id in self.tracking_state:
                del self.tracking_state[tag_id]
    
    def get_pose_from_tag_id(
        self,
        detections: List[Dict[str, Any]],
        tag_id: int
    ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Extract pose (translation and rotation) for a specific tag ID.
        
        Parameters
        ----------
        detections : List[Dict[str, Any]]
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
        detections: List[Dict[str, Any]],
        draw_axes: bool = True,
        axis_length: float = None
    ) -> np.ndarray:
        """
        Draw detected tags and their coordinate axes on the image.
        
        Parameters
        ----------
        image : np.ndarray
            Input image to draw on (will be copied).
        detections : List[Dict[str, Any]]
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
