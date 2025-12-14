/**
 * @file apriltagDetector.js
 * @description AprilTag marker detector implementation
 * Uses OpenCV.js for image processing and square detection
 * Note: Full AprilTag decoding requires custom OpenCV build with AprilTag module
 * This implementation detects square markers and uses simple pattern matching
 */

/**
 * @typedef {import('./types.js').MarkerDetection} MarkerDetection
 */

/**
 * AprilTag detector implementation
 * @implements {IMarkerDetector}
 */
class AprilTagDetector {
    /**
     * Creates an AprilTag detector
     * @param {Object} options - Configuration options
     * @param {string} [options.family='36h11'] - Tag family to use (36h11, 25h9, 16h5, 36h9, 36h10)
     * @param {cv.Mat} [options.grayMat] - Pre-allocated grayscale Mat for reuse
     * @param {cv.Mat} [options.blurredMat] - Pre-allocated blur Mat for reuse
     * @param {cv.Mat} [options.binaryMat] - Pre-allocated binary Mat for reuse
     */
    constructor(options = {}) {
        this.family = options.family || '36h11';
        this.tagFamilyData = null;
        this.initialized = false;
        
        // Pre-allocate Mats for performance (if provided)
        this.grayMat = options.grayMat || null;
        this.blurredMat = options.blurredMat || null;
        this.binaryMat = options.binaryMat || null;
        this.contours = null;
        this.hierarchy = null;
    }

    /**
     * Initialize the detector by loading tag family data and setting up OpenCV structures
     * @returns {Promise<void>}
     */
    async init() {
        if (this.initialized) return;

        if (typeof cv === 'undefined' || !cv.Mat) {
            throw new Error('OpenCV.js not loaded');
        }

        try {
            // Load tag family configuration
            const response = await fetch(`./apriltag-families/${this.family}.json`);
            if (!response.ok) {
                throw new Error(`Failed to load AprilTag family: ${this.family}`);
            }
            this.tagFamilyData = await response.json();
            
            // Initialize OpenCV structures for contour detection
            if (!this.blurredMat) this.blurredMat = new cv.Mat();
            if (!this.binaryMat) this.binaryMat = new cv.Mat();
            if (!this.contours) this.contours = new cv.MatVector();
            if (!this.hierarchy) this.hierarchy = new cv.Mat();
            
            console.log(`AprilTag detector initialized: family=${this.family}, codes=${this.tagFamilyData.codes.length}`);
            this.initialized = true;
        } catch (error) {
            console.error('Failed to initialize AprilTag detector:', error);
            throw error;
        }
    }

    /**
     * Detects AprilTag markers using OpenCV square detection
     * Note: This is a simplified implementation that detects square markers
     * Full AprilTag decoding would require custom OpenCV build with apriltag module
     * 
     * @param {Uint8ClampedArray|Uint8Array|cv.Mat} grayImageData - Grayscale image data or Mat
     * @param {number} width - Image width in pixels
     * @param {number} height - Image height in pixels
     * @returns {MarkerDetection[]} Array of detected markers
     */
    detect(grayImageData, width, height) {
        if (!this.initialized) {
            console.warn('AprilTag detector not initialized. Call init() first.');
            return [];
        }

        const detections = [];

        try {
            // Convert input to cv.Mat if needed
            let grayMat;
            if (grayImageData instanceof cv.Mat) {
                grayMat = grayImageData;
            } else {
                if (!this.grayMat || this.grayMat.cols !== width || this.grayMat.rows !== height) {
                    if (this.grayMat) this.grayMat.delete();
                    this.grayMat = new cv.Mat(height, width, cv.CV_8UC1);
                }
                this.grayMat.data.set(grayImageData);
                grayMat = this.grayMat;
            }

            // Apply Gaussian blur to reduce noise
            const ksize = new cv.Size(5, 5);
            cv.GaussianBlur(grayMat, this.blurredMat, ksize, 0);

            // Apply adaptive thresholding (better for varying lighting)
            cv.adaptiveThreshold(
                this.blurredMat,
                this.binaryMat,
                255,
                cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv.THRESH_BINARY,
                11,
                2
            );

            // Find contours
            cv.findContours(
                this.binaryMat,
                this.contours,
                this.hierarchy,
                cv.RETR_LIST,
                cv.CHAIN_APPROX_SIMPLE
            );

            const minArea = 800;
            const maxArea = (width * height) * 0.7;
            let detectionId = 0;

            // Process each contour
            for (let i = 0; i < this.contours.size(); i++) {
                const contour = this.contours.get(i);
                const area = cv.contourArea(contour);

                if (area >= minArea && area <= maxArea) {
                    const peri = cv.arcLength(contour, true);
                    const approx = new cv.Mat();
                    cv.approxPolyDP(contour, approx, 0.02 * peri, true);

                    // Check if it's a quadrilateral
                    if (approx.rows === 4 && cv.isContourConvex(approx)) {
                        const rect = cv.boundingRect(approx);
                        const aspectRatio = Math.max(rect.width, rect.height) / Math.min(rect.width, rect.height);

                        // Check if roughly square (AprilTags are square)
                        if (aspectRatio <= 1.5) {
                            // Extract corners
                            const corners = [];
                            for (let j = 0; j < 8; j += 2) {
                                corners.push({
                                    x: approx.data32S[j],
                                    y: approx.data32S[j + 1]
                                });
                            }

                            // Calculate center
                            const centerPx = {
                                x: corners.reduce((sum, c) => sum + c.x, 0) / 4,
                                y: corners.reduce((sum, c) => sum + c.y, 0) / 4
                            };

                            // Create detection
                            // Note: Without full AprilTag decoder, we can't determine actual tag ID
                            // Using sequential IDs for now (detection order)
                            detections.push({
                                id: detectionId++,
                                family: `tag${this.family}`,
                                cornersPx: corners,
                                centerPx: centerPx,
                                confidence: 0.8 // Lower confidence since we're not doing full decoding
                            });
                        }
                    }

                    approx.delete();
                }
            }
        } catch (error) {
            console.error('AprilTag detection error:', error);
        }

        return detections;
    }

    /**
     * Cleanup resources
     */
    dispose() {
        if (this.grayMat) this.grayMat.delete();
        if (this.blurredMat) this.blurredMat.delete();
        if (this.binaryMat) this.binaryMat.delete();
        if (this.contours) this.contours.delete();
        if (this.hierarchy) this.hierarchy.delete();
        
        this.grayMat = null;
        this.blurredMat = null;
        this.binaryMat = null;
        this.contours = null;
        this.hierarchy = null;
        this.initialized = false;
    }
}

// Export for browser usage
if (typeof window !== 'undefined') {
    window.AprilTagDetector = AprilTagDetector;
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AprilTagDetector;
}
