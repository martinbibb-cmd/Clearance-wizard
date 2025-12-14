# Custom Fiducial Markers Guide

## Overview

This guide explores advanced techniques for creating visually appealing fiducial markers that maintain machine vision accuracy while being less obtrusive in user-facing applications.

Standard AprilTags are highly robust but can appear industrial and unattractive. This document outlines methods to "beautify" markers without sacrificing pose estimation accuracy.

## Table of Contents

1. [The Problem with Standard Markers](#the-problem-with-standard-markers)
2. [Custom Marker Technologies](#custom-marker-technologies)
3. [Implementation Approaches](#implementation-approaches)
4. [Recommendations](#recommendations)
5. [GitHub Resources](#github-resources)
6. [Integration Guide](#integration-guide)

---

## The Problem with Standard Markers

### Why Plain AprilTags Look Industrial

- **High Contrast Black & White:** Necessary for robust detection but visually stark
- **Geometric Patterns:** Essential for encoding ID but lack aesthetic appeal
- **Environmental Mismatch:** Stand out in consumer or commercial spaces
- **Brand Inconsistency:** Don't align with company branding or décor

### Requirements for Custom Markers

Any custom marker system must maintain:
- **Pose Estimation Accuracy:** Sub-centimeter position accuracy
- **Robustness:** Detection under varying lighting and angles
- **Speed:** Real-time detection (>30 fps)
- **ID Encoding:** Unique identification of multiple markers

---

## Custom Marker Technologies

### 1. Custom Templates (VuMark/JuMarker)

#### Description
These systems allow embedding markers within custom graphics, logos, or patterns. The marker's functional elements are integrated into a larger design.

#### How It Works
- **Background Layer:** Custom image, logo, or branded pattern
- **Functional Regions:** Specific high-contrast areas encode the marker ID
- **Detection Algorithm:** Custom detector identifies functional regions within template

#### Benefits
✅ Markers blend with branding or environment  
✅ Professional appearance  
✅ Maintains pose estimation accuracy  
✅ Suitable for consumer-facing applications

#### Caveats
⚠️ Requires custom detection algorithm (not standard AprilTag)  
⚠️ Template design requires expertise  
⚠️ May be less robust than pure AprilTags in challenging conditions  
⚠️ Limited open-source implementations

#### Example Use Cases
- Retail product packaging with branded markers
- Museum exhibits with artistic marker integration
- AR business cards with company logos

---

### 2. DeepTag (Deep Learning-Based Markers)

#### Description
DeepTag uses deep neural networks to detect and decode custom-designed markers. It provides flexibility in marker appearance while maintaining detection robustness.

#### How It Works
- **Training Phase:** Train a CNN to recognize custom marker designs
- **Marker Design:** Create markers with aesthetic patterns
- **Detection Phase:** Neural network detects and decodes markers
- **Pose Estimation:** Standard PnP algorithm after detection

#### Benefits
✅ High flexibility in marker design  
✅ Can handle complex, artistic patterns  
✅ Potentially more robust to occlusion  
✅ Active research area with improvements

#### Caveats
⚠️ Requires training dataset and GPU resources  
⚠️ Slower detection than classical methods (10-30ms vs 1-5ms)  
⚠️ Needs retraining for new marker designs  
⚠️ Limited Python implementations available

#### Example Use Cases
- Custom artistic markers for galleries
- Markers that match specific design themes
- Markers with company-specific patterns

---

### 3. Colour-Based Markers

#### Description
Use high-contrast color patterns instead of black and white to encode marker data. Colors can be more visually appealing and theme-appropriate.

#### How It Works
- **Color Encoding:** Use distinct color pairs (e.g., blue/yellow, red/green)
- **Detection:** Color segmentation in HSV space
- **ID Decoding:** Pattern of colored cells encodes unique ID
- **Pose Estimation:** Standard PnP on detected corners

#### Benefits
✅ Visually appealing and themeable  
✅ Can increase robustness in certain lighting  
✅ Easier to integrate with branding  
✅ Relatively simple to implement

#### Caveats
⚠️ Requires color camera (no grayscale)  
⚠️ Sensitive to lighting color temperature  
⚠️ Color calibration needed per environment  
⚠️ May be less robust than B&W in shadows

#### Example Use Cases
- Educational applications with colorful themes
- Children's apps with playful markers
- Brand-matched markers (company colors)

---

### 4. Invisible Markers (iMarkers / UV / IR)

#### Description
Markers printed with inks invisible to the human eye but detectable by cameras with specific filters (UV or IR).

#### How It Works
- **Invisible Ink:** UV-fluorescent or IR-reflective inks
- **Special Camera:** Camera with UV/IR filter
- **Standard Detection:** Once captured, uses standard marker detection
- **Pose Estimation:** Standard PnP algorithm

#### Benefits
✅ Completely eliminates visual clutter  
✅ Perfect for high-end consumer applications  
✅ Maintains full marker robustness  
✅ No aesthetic compromise

#### Caveats
⚠️ Requires specialized hardware (IR/UV camera)  
⚠️ Special ink and printing process  
⚠️ More expensive than standard markers  
⚠️ Limited to devices with appropriate sensors

#### Example Use Cases
- High-end AR furniture visualization
- Museum installations (preserve aesthetics)
- Luxury product AR experiences

---

### 5. Hybrid Markers (ChArUco)

#### Description
ChArUco boards combine checkerboard patterns with ArUco markers, providing both robust corner detection and ID encoding.

#### How It Works
- **Checkerboard:** High-precision corner detection
- **Embedded ArUco:** Unique IDs within checkerboard squares
- **Dual Detection:** Checkerboard for accuracy, ArUco for ID
- **OpenCV Support:** Built into OpenCV library

#### Benefits
✅ Excellent pose estimation accuracy  
✅ Native OpenCV support  
✅ Robust to partial occlusion  
✅ Well-documented and tested

#### Caveats
⚠️ Still visually "technical" (black and white)  
⚠️ Larger size required than pure markers  
⚠️ Not as customizable aesthetically  
⚠️ Better for calibration than AR visualization

#### Example Use Cases
- Camera calibration targets
- Robotic navigation markers
- High-precision industrial AR

---

## Implementation Approaches

### Recommended Path: Progressive Enhancement

Start with standard AprilTags and progressively enhance aesthetics:

#### Phase 1: Standard AprilTags (Immediate)
```python
from vio import AprilTagDetector

detector = AprilTagDetector(
    tag_size=0.19,
    camera_matrix=K,
    dist_coeffs=D,
    tag_family='tag36h11'  # Good balance of robustness and aesthetics
)
```

**Advantages:**
- Immediate deployment
- Proven reliability
- Full VIO integration

#### Phase 2: Design Enhancement (Short-term)
- Add colored borders or frames around markers
- Integrate markers into larger visual designs
- Use smaller markers with aesthetic surroundings

```
┌─────────────────────────┐
│                         │
│   [Your Brand Logo]     │
│                         │
│    ┌────────────┐       │
│    │ AprilTag  │       │
│    │   #123     │       │
│    └────────────┘       │
│                         │
│  [Product Information]  │
│                         │
└─────────────────────────┘
```

#### Phase 3: Custom Implementation (Medium-term)
Implement color-based or custom template markers:

```python
class ColorMarkerDetector:
    """
    Detector for color-based fiducial markers.
    
    Similar to AprilTag but uses color patterns for encoding.
    """
    
    def __init__(self, marker_size, camera_matrix, dist_coeffs):
        self.marker_size = marker_size
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
    
    def detect(self, image):
        """Detect color markers in image."""
        # 1. Color segmentation (HSV space)
        # 2. Contour detection
        # 3. Pattern matching
        # 4. PnP pose estimation
        pass
```

#### Phase 4: Deep Learning (Long-term)
Implement DeepTag or similar for maximum flexibility:

```python
class DeepTagDetector:
    """
    Neural network-based custom marker detector.
    
    Uses trained CNN for detecting aesthetic custom markers.
    """
    
    def __init__(self, model_path, marker_size, camera_matrix, dist_coeffs):
        self.model = load_model(model_path)
        self.marker_size = marker_size
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
    
    def detect(self, image):
        """Detect custom markers using neural network."""
        # 1. Neural network inference
        # 2. Corner refinement
        # 3. PnP pose estimation
        pass
```

---

## Recommendations

### For Clearance Wizard VIO Project

#### Immediate Use (Week 1)
**Stick with AprilTags** but improve presentation:
- Use smaller markers in larger branded cards
- Print on high-quality materials
- Add frames or borders for aesthetic appeal
- Choose tag36h11 family (better error correction)

```python
# Current implementation - already optimal
detector = AprilTagDetector(
    tag_size=0.19,
    camera_matrix=camera_matrix,
    dist_coeffs=dist_coeffs,
    tag_family='tag36h11'  # Recommended for balance
)
```

#### Near-term Enhancement (Month 1-2)
**Research and prototype color markers:**

1. **Design Phase:**
   - Create branded color marker templates
   - Test color combinations for robustness
   - Validate under various lighting conditions

2. **Implementation Phase:**
   - Fork AprilTagDetector to ColorMarkerDetector
   - Implement HSV-based color segmentation
   - Maintain PnP pose estimation pipeline

3. **Testing Phase:**
   - Compare accuracy with standard AprilTags
   - Measure detection speed
   - Test in target environments

#### Long-term Research (Month 3+)
**Investigate DeepTag or custom neural solutions:**

1. **Research existing implementations:**
   - Search GitHub for "DeepTag", "DeepMarker", "CNN fiducial"
   - Evaluate PyTorch/TensorFlow marker detection models
   - Assess computational requirements

2. **Prototype development:**
   - Create small training dataset
   - Train simple CNN for proof-of-concept
   - Benchmark against AprilTag performance

3. **Production evaluation:**
   - Assess real-world robustness
   - Measure mobile device performance
   - Evaluate user acceptance

---

## GitHub Resources

### Existing Open-Source Projects

#### 1. Standard Fiducial Systems (Production-Ready)

**AprilTag**
- Repository: https://github.com/AprilRobotics/apriltag
- Language: C/C++ with Python bindings
- Status: Mature, actively maintained
- Best for: Production use, proven reliability

**ArUco (OpenCV)**
- Repository: Built into OpenCV
- Documentation: https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html
- Language: C++ with Python bindings
- Best for: OpenCV-integrated projects

**ChArUco**
- Repository: Built into OpenCV
- Documentation: https://docs.opencv.org/4.x/df/d4a/tutorial_charuco_detection.html
- Best for: High-precision calibration

#### 2. Custom Marker Research Projects

**DeepTag (Research)**
- Search: "DeepTag marker detection GitHub"
- Note: Multiple research implementations, not production-ready
- Languages: PyTorch, TensorFlow
- Best for: Research and experimentation

**ARTag / ARToolKit**
- Repository: https://github.com/artoolkitx/artoolkit5
- Language: C++
- Status: Legacy but functional
- Best for: Historical reference

**Alvar (VTT)**
- Repository: https://github.com/vtt-a/alvar
- Language: C++
- Status: Unmaintained but documented
- Best for: Understanding marker systems

#### 3. Color Marker Projects

**PlayARific (Unity)**
- Search: "color marker detection Unity"
- Language: C#
- Best for: Unity integration ideas

**Color ArUco Markers**
- Search: "color aruco marker python"
- Language: Python + OpenCV
- Best for: Quick prototypes

### Copilot Search Prompts

To find modern implementations:

```
"Search GitHub for a modern Python implementation of a Customizable 
Fiducial Marker system (like DeepTag, VuMark, or JuMarker) that allows 
a logo or custom image as the marker background while maintaining pose 
estimation accuracy, suitable for a VIO project."
```

```
"Find Python libraries for detecting color-based fiducial markers 
with pose estimation capabilities, compatible with OpenCV and suitable 
for real-time AR applications."
```

```
"Search for deep learning-based marker detection systems in Python 
that support custom marker designs and provide 6DOF pose estimation."
```

---

## Integration Guide

### Maintaining API Compatibility

Any custom marker implementation should maintain the same API as AprilTagDetector:

```python
class CustomMarkerDetector:
    """
    Drop-in replacement for AprilTagDetector with custom markers.
    """
    
    def __init__(self, marker_size, camera_matrix, dist_coeffs, **kwargs):
        """Initialize detector with same signature as AprilTagDetector."""
        self.marker_size = marker_size
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
    
    def detect(self, image):
        """
        Detect markers in image.
        
        Returns
        -------
        list
            List of detection dictionaries with same format as AprilTagDetector:
            - tag_id: int
            - center: (x, y)
            - corners: 4x2 array
            - translation: [x, y, z]
            - rotation_matrix: 3x3 array
            - rotation_vector: [rx, ry, rz]
        """
        pass
```

### Switching Between Marker Types

Make it easy to switch between marker systems:

```python
# Configuration-based detector selection
MARKER_TYPE = 'apriltag'  # or 'color', 'deeptag', 'custom'

if MARKER_TYPE == 'apriltag':
    detector = AprilTagDetector(tag_size, K, D)
elif MARKER_TYPE == 'color':
    detector = ColorMarkerDetector(marker_size, K, D)
elif MARKER_TYPE == 'deeptag':
    detector = DeepTagDetector(model_path, marker_size, K, D)
else:
    raise ValueError(f"Unknown marker type: {MARKER_TYPE}")

# Rest of VIO code remains unchanged
detections = detector.detect(image)
```

---

## Performance Comparison

### Expected Performance Metrics

| Marker Type | Detection Speed | Accuracy | Robustness | Aesthetics | Complexity |
|-------------|----------------|----------|------------|------------|------------|
| **AprilTag** | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Color Markers** | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **DeepTag** | ⚡⚡⚡ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Invisible (IR)** | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **ChArUco** | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |

### Benchmark Targets

For real-time VIO at 30 FPS:
- **Detection time:** < 33ms per frame
- **Position accuracy:** < 1cm at 1m distance
- **Orientation accuracy:** < 2° at 1m distance
- **Detection rate:** > 95% with marker visible

---

## Conclusion

### Summary of Approaches

1. **Short-term:** Continue with AprilTags, enhance presentation
2. **Medium-term:** Prototype color-based markers
3. **Long-term:** Research deep learning approaches
4. **Premium:** Consider IR/UV markers for high-end applications

### Next Steps for Implementation

1. ✅ **Completed:** Basic VIO with AprilTag support
2. ✅ **Completed:** ARBridge for 3D rendering integration
3. 🔄 **Current:** Design branded marker cards with AprilTags
4. 📋 **Next:** Research and prototype color marker system
5. 📋 **Future:** Investigate deep learning marker detection

### Key Takeaway

**Start simple, iterate based on user feedback.**

AprilTags provide excellent technical performance. Enhanced aesthetics can be achieved through:
- Better presentation (frames, cards, branding)
- Selective use (only where needed)
- Future custom implementations as project matures

The VIO system's modular architecture makes it easy to swap marker detection systems without changing the core fusion algorithm.

---

## References

### Academic Papers

1. **AprilTag:** Wang, J., & Olson, E. (2016). "AprilTag 2: Efficient and robust fiducial detection." IROS.

2. **DeepTag:** Various papers on deep learning for marker detection (search arXiv/IEEE)

3. **VuMark:** Commercial system by PTC (Vuforia)

4. **ChArUco:** Garrido-Jurado, S., et al. (2016). "Generation of fiducial marker dictionaries using mixed integer linear programming."

### Online Resources

- **AprilTag Official:** https://april.eecs.umich.edu/software/apriltag
- **OpenCV Markers:** https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html
- **AR/VR Markers Survey:** Search IEEE Xplore for "fiducial marker survey"

### Tools

- **Marker Generators:**
  - AprilTag: https://github.com/AprilRobotics/apriltag-imgs
  - ArUco: OpenCV built-in generators
  - Online: Various web-based generators

- **Design Tools:**
  - Inkscape/Illustrator for custom templates
  - Photoshop for marker integration
  - Blender for 3D marker visualization

---

*Last Updated: 2025-12-14*  
*Part of the Clearance Wizard VIO Project*
