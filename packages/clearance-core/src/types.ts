/**
 * Core type definitions for Clearance Wizard
 * Shared between React Native app and future API
 */

/**
 * ARKit camera intrinsics
 */
export interface CameraIntrinsics {
  fx: number; // Focal length x
  fy: number; // Focal length y
  cx: number; // Principal point x
  cy: number; // Principal point y
  width: number;
  height: number;
}

/**
 * 4x4 transformation matrix (column-major order as per ARKit)
 */
export type Transform = number[]; // 16 elements

/**
 * ARKit tracking state
 */
export enum TrackingState {
  NotAvailable = 'notAvailable',
  Limited = 'limited',
  Normal = 'normal',
}

/**
 * Tracking state change reason
 */
export enum TrackingStateReason {
  None = 'none',
  Initializing = 'initializing',
  ExcessiveMotion = 'excessiveMotion',
  InsufficientFeatures = 'insufficientFeatures',
  Relocalizing = 'relocalizing',
}

/**
 * 3D point in world space
 */
export interface Point3D {
  x: number;
  y: number;
  z: number;
}

/**
 * AR context data captured with each measurement/photo
 */
export interface ARContext {
  anchorTransform: Transform;
  cameraIntrinsics: CameraIntrinsics;
  trackingState: TrackingState;
  timestamp: number; // Unix timestamp in ms
}

/**
 * Measurement between two points
 */
export interface Measurement {
  distanceMm: number;
  from: Point3D;
  to: Point3D;
  confidence: number; // 0-1
  label?: string; // e.g., "clearance-to-window"
}

/**
 * Capture type
 */
export enum CaptureType {
  Photo = 'photo',
  Measurement = 'measurement',
  Annotation = 'annotation',
}

/**
 * Individual capture within a pack
 */
export interface Capture {
  captureId: string; // UUID
  type: CaptureType;
  timestamp: number; // Unix timestamp in ms
  photoPath?: string; // Local filesystem path
  measurements: Measurement[];
  notes?: string; // Free text
  structuredData?: Record<string, unknown>; // Optional structured fields
  ar: ARContext;
}

/**
 * Site metadata (optional minimal for v1)
 */
export interface SiteMetadata {
  address?: string;
  leadRef?: string;
  customerRef?: string;
  notes?: string;
}

/**
 * Boiler context
 */
export interface BoilerContext {
  model?: string;
  location?: string;
  notes?: string;
}

/**
 * Complete pack (local-first data structure)
 */
export interface Pack {
  packId: string; // UUID
  createdAt: number; // Unix timestamp in ms
  updatedAt: number; // Unix timestamp in ms
  site?: SiteMetadata;
  boiler?: BoilerContext;
  captures: Capture[];
}

/**
 * Export format metadata
 */
export interface PackExport {
  pack: Pack;
  exportedAt: number;
  version: string; // Schema version
  format: 'json' | 'zip';
}
