/**
 * @file types.js
 * @description Type definitions and interfaces for marker detection
 */

/**
 * Represents a detected marker in the camera frame
 * @typedef {Object} MarkerDetection
 * @property {number} id - Unique marker ID
 * @property {string} family - Marker family (e.g., 'DICT_4X4_50', 'tag36h11')
 * @property {Array<{x: number, y: number}>} cornersPx - Four corner positions in pixels [TL, TR, BR, BL]
 * @property {{x: number, y: number}} centerPx - Center position in pixels
 * @property {number} [confidence] - Detection confidence score (0-1)
 */

/**
 * Interface for marker detector implementations
 * @interface IMarkerDetector
 */

/**
 * Detects markers in a grayscale image
 * @function
 * @name IMarkerDetector#detect
 * @param {Uint8ClampedArray|Uint8Array} grayImageData - Grayscale image data
 * @param {number} width - Image width in pixels
 * @param {number} height - Image height in pixels
 * @returns {MarkerDetection[]} Array of detected markers
 */

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        // This is a types-only file
        // No runtime exports needed
    };
}
