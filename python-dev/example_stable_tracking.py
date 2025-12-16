#!/usr/bin/env python3
"""
Example: Stable AprilTag Tracking

This script demonstrates the pose estimation stability features implemented
to address near-field tracking issues and pose collapse.
"""

import numpy as np
import cv2
from vio import AprilTagDetector


def test_stability_features():
    """
    Test and demonstrate all stability features.
    """
    print("=" * 70)
    print("AprilTag Pose Estimation Stability Features Demo")
    print("=" * 70)
    print()
    
    # Setup camera parameters
    image_width, image_height = 1280, 720
    camera_matrix = AprilTagDetector.create_default_camera_matrix(
        image_width, image_height, fov_degrees=60.0
    )
    dist_coeffs = np.zeros(5)
    
    print("Camera Configuration")
    print("-" * 70)
    print(f"Resolution: {image_width}×{image_height}")
    print(f"FOV: 60°")
    print(f"Focal length: {camera_matrix[0, 0]:.1f}px")
    print()
    
    # Test different configurations
    configs = [
        {
            'name': 'Default (Unstable)',
            'tag_size': 0.04,  # 40mm
            'min_distance': None,  # Will default to 2×tag_size = 80mm
            'max_reprojection_error': 5.0,
            'smoothing_alpha': 0.3,
            'lost_timeout_frames': 5,
        },
        {
            'name': 'Close-Range Optimized',
            'tag_size': 0.04,  # 40mm
            'min_distance': 0.12,  # 3×tag_size = 120mm (more conservative)
            'max_reprojection_error': 8.0,  # Allow higher error for close range
            'smoothing_alpha': 0.2,  # Heavier smoothing
            'lost_timeout_frames': 10,  # More forgiving
        },
        {
            'name': 'Large Marker Stable',
            'tag_size': 0.19,  # 190mm (A4)
            'min_distance': 0.38,  # 2×tag_size = 380mm
            'max_reprojection_error': 5.0,
            'smoothing_alpha': 0.3,
            'lost_timeout_frames': 5,
        },
        {
            'name': 'Responsive (Less Smoothing)',
            'tag_size': 0.19,
            'min_distance': 0.38,
            'max_reprojection_error': 5.0,
            'smoothing_alpha': 0.6,  # Light smoothing
            'lost_timeout_frames': 3,  # Quick timeout
        },
    ]
    
    for config in configs:
        print(f"Configuration: {config['name']}")
        print("-" * 70)
        
        detector = AprilTagDetector(
            tag_size=config['tag_size'],
            camera_matrix=camera_matrix,
            dist_coeffs=dist_coeffs,
            min_distance=config['min_distance'],
            max_reprojection_error=config['max_reprojection_error'],
            smoothing_alpha=config['smoothing_alpha'],
            lost_timeout_frames=config['lost_timeout_frames'],
        )
        
        print(f"  Tag size: {config['tag_size']*1000:.0f}mm")
        print(f"  Min distance: {detector.min_distance*1000:.0f}mm")
        print(f"  Max reproj error: {config['max_reprojection_error']:.1f}px")
        print(f"  Smoothing alpha: {config['smoothing_alpha']:.2f}")
        print(f"  Lost timeout: {config['lost_timeout_frames']} frames")
        print()
        
        # Simulate detection sequence
        print("  Simulated Detection Sequence:")
        test_detection_sequence(detector)
        print()


def test_detection_sequence(detector):
    """
    Simulate a sequence of detections with various scenarios.
    """
    # Create blank image
    image = np.ones((720, 1280, 3), dtype=np.uint8) * 255
    
    # Scenario 1: No detection
    detections = detector.detect(image)
    print(f"    Frame 1: {len(detections)} detections (expected: 0)")
    
    # Scenario 2: Simulate tracking state
    # In real usage, this would come from actual AprilTag detections
    # For demonstration, we'll show the tracking state management
    
    # Add a simulated tag to tracking state
    test_tag_id = 42
    test_pose = (np.array([[0.0], [0.0], [1.0]]), np.array([[0.0], [0.0], [0.0]]))
    
    # Show tracking state
    if test_tag_id in detector.previous_poses:
        print(f"    Tag {test_tag_id} is being tracked")
    else:
        print(f"    Tag {test_tag_id} not in tracking state")
    
    # Test reset
    detector.reset_tracking(test_tag_id)
    print(f"    Reset tracking for tag {test_tag_id}")
    
    if test_tag_id in detector.previous_poses:
        print(f"    Tag {test_tag_id} still tracked (unexpected)")
    else:
        print(f"    Tag {test_tag_id} tracking cleared ✓")


def demonstrate_distance_checking():
    """
    Demonstrate minimum distance validation.
    """
    print("=" * 70)
    print("Minimum Distance Validation Demo")
    print("=" * 70)
    print()
    
    # Setup
    camera_matrix = AprilTagDetector.create_default_camera_matrix(640, 480)
    dist_coeffs = np.zeros(5)
    
    # Test different marker sizes
    test_cases = [
        (0.04, 'Small (40mm)'),
        (0.08, 'Medium (80mm)'),
        (0.19, 'Large (190mm)'),
    ]
    
    for tag_size, name in test_cases:
        detector = AprilTagDetector(
            tag_size=tag_size,
            camera_matrix=camera_matrix,
            dist_coeffs=dist_coeffs,
        )
        
        min_dist_mm = detector.min_distance * 1000
        print(f"{name} Marker:")
        print(f"  Tag size: {tag_size*1000:.0f}mm")
        print(f"  Minimum distance: {min_dist_mm:.0f}mm (2× tag size)")
        print(f"  Recommended range: {min_dist_mm:.0f}mm - {min_dist_mm*10:.0f}mm")
        print()


def demonstrate_smoothing():
    """
    Demonstrate temporal smoothing effect.
    """
    print("=" * 70)
    print("Temporal Smoothing Demo")
    print("=" * 70)
    print()
    
    # Simulate noisy measurements
    true_position = np.array([0.0, 0.0, 1.0])
    noise_std = 0.01  # 1cm noise
    
    alpha_values = [0.0, 0.3, 0.5, 1.0]
    
    print("Simulating 10 noisy measurements with different smoothing factors:")
    print()
    
    for alpha in alpha_values:
        smoothed_pos = true_position.copy()
        errors = []
        
        for i in range(10):
            # Add noise
            noisy_pos = true_position + np.random.randn(3) * noise_std
            
            # Apply smoothing (simplified version of detector's method)
            smoothed_pos = alpha * noisy_pos + (1 - alpha) * smoothed_pos
            
            error = np.linalg.norm(smoothed_pos - true_position)
            errors.append(error)
        
        mean_error = np.mean(errors)
        std_error = np.std(errors)
        
        print(f"Alpha = {alpha:.1f}:")
        print(f"  Mean error: {mean_error*1000:.2f}mm")
        print(f"  Std error: {std_error*1000:.2f}mm")
        
        if alpha == 0.0:
            print("  (No update - uses only previous pose)")
        elif alpha == 1.0:
            print("  (No smoothing - uses only new measurement)")
        else:
            print(f"  ({int((1-alpha)*100)}% previous + {int(alpha*100)}% new)")
        print()


def demonstrate_reprojection_error():
    """
    Demonstrate distance-aware reprojection error thresholds.
    """
    print("=" * 70)
    print("Distance-Aware Reprojection Error Demo")
    print("=" * 70)
    print()
    
    # Setup
    camera_matrix = AprilTagDetector.create_default_camera_matrix(640, 480)
    dist_coeffs = np.zeros(5)
    
    detector = AprilTagDetector(
        tag_size=0.19,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs,
        min_distance=0.38,
        max_reprojection_error=5.0,
    )
    
    print(f"Base reprojection error threshold: {detector.max_reprojection_error}px")
    print(f"Minimum distance: {detector.min_distance*1000:.0f}mm")
    print()
    
    # Test different distances
    test_distances = [0.4, 0.8, 1.5, 3.0, 5.0]
    
    print("Adjusted thresholds at different distances:")
    print()
    
    for distance in test_distances:
        distance_factor = max(1.0, detector.min_distance / distance)
        adjusted_threshold = detector.max_reprojection_error * distance_factor
        
        print(f"Distance: {distance:.1f}m")
        print(f"  Distance factor: {distance_factor:.2f}×")
        print(f"  Adjusted threshold: {adjusted_threshold:.2f}px")
        
        if distance < detector.min_distance:
            print(f"  ⚠️  Too close! Would be rejected.")
        else:
            print(f"  ✓ Within valid range")
        print()


def main():
    """
    Run all demonstrations.
    """
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "AprilTag Pose Stability Demonstrations" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    # Run demonstrations
    test_stability_features()
    demonstrate_distance_checking()
    demonstrate_smoothing()
    demonstrate_reprojection_error()
    
    # Summary
    print("=" * 70)
    print("Summary: Key Stability Features")
    print("=" * 70)
    print()
    print("✓ Minimum Distance Enforcement")
    print("  Prevents near-field instability by rejecting too-close detections")
    print()
    print("✓ Pose Continuity (solvePnPGeneric)")
    print("  Resolves corner order ambiguity by selecting closest to previous pose")
    print()
    print("✓ Temporal Smoothing")
    print("  Reduces jitter through exponential filtering of position and rotation")
    print()
    print("✓ Distance-Aware Error Thresholds")
    print("  Adapts reprojection error limits based on marker distance")
    print()
    print("✓ Tracking State Machine")
    print("  Detection → Tracking → Lost (with timeout)")
    print()
    print("For complete usage guide, see POSE_STABILITY_GUIDE.md")
    print("=" * 70)
    print()


if __name__ == '__main__':
    main()
