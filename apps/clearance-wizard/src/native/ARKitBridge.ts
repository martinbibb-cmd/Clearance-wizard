/**
 * TypeScript wrapper for native ARKit bridge
 * Provides typed interface to Swift ARKit module
 */

import { NativeModules, NativeEventEmitter } from 'react-native';
import type {
  CameraIntrinsics,
  Transform,
  TrackingState,
  TrackingStateReason,
  Point3D,
} from '@clearance-wizard/core';

interface HitTestResult {
  worldTransform: Transform;
  planeDetected: boolean;
  confidence: number;
}

interface AnchorResult {
  anchorId: string;
  transform: Transform;
}

interface TrackingStateResult {
  state: TrackingState;
  reason: TrackingStateReason;
}

interface MeasurementResult {
  distanceMm: number;
  pointA: Point3D;
  pointB: Point3D;
  confidence: number;
}

interface PhotoResult {
  localPath: string;
  width: number;
  height: number;
}

interface FrameEvent {
  intrinsics: CameraIntrinsics;
  cameraTransform: Transform;
  trackingState: TrackingState;
  timestamp: number;
}

interface AnchorUpdateEvent {
  anchorId: string;
  transform: Transform;
  type: 'added' | 'updated';
}

interface ErrorEvent {
  code: string;
  message: string;
}

const { ARKitBridge: NativeARKitBridge } = NativeModules;

if (!NativeARKitBridge) {
  throw new Error(
    'ARKitBridge native module is not available. ' +
    'Make sure you are running on iOS and the module is properly linked.'
  );
}

/**
 * ARKit Bridge - Native module interface
 */
class ARKitBridgeClass {
  private eventEmitter: NativeEventEmitter;
  
  constructor() {
    this.eventEmitter = new NativeEventEmitter(NativeARKitBridge);
  }

  /**
   * Start AR session with world tracking
   */
  async startSession(): Promise<{ success: boolean }> {
    return NativeARKitBridge.startSession();
  }

  /**
   * Stop AR session
   */
  async stopSession(): Promise<{ success: boolean }> {
    return NativeARKitBridge.stopSession();
  }

  /**
   * Perform hit test at screen coordinates
   * @param x Screen X coordinate (normalized 0-1)
   * @param y Screen Y coordinate (normalized 0-1)
   */
  async hitTest(x: number, y: number): Promise<HitTestResult> {
    return NativeARKitBridge.hitTest(x, y);
  }

  /**
   * Create world anchor at transform
   * @param transform 4x4 transformation matrix
   */
  async createAnchor(transform: Transform): Promise<AnchorResult> {
    return NativeARKitBridge.createAnchor(transform);
  }

  /**
   * Get current tracking state
   */
  async getTrackingState(): Promise<TrackingStateResult> {
    return NativeARKitBridge.getTrackingState();
  }

  /**
   * Measure distance between two screen points
   * @param x1 First point X (normalized 0-1)
   * @param y1 First point Y (normalized 0-1)
   * @param x2 Second point X (normalized 0-1)
   * @param y2 Second point Y (normalized 0-1)
   */
  async measureRay(
    x1: number,
    y1: number,
    x2: number,
    y2: number
  ): Promise<MeasurementResult> {
    return NativeARKitBridge.measureRay(x1, y1, x2, y2);
  }

  /**
   * Capture current AR frame as photo
   */
  async capturePhoto(): Promise<PhotoResult> {
    return NativeARKitBridge.capturePhoto();
  }

  /**
   * Subscribe to frame updates
   */
  onFrame(callback: (event: FrameEvent) => void): () => void {
    const subscription = this.eventEmitter.addListener('onFrame', callback);
    return () => subscription.remove();
  }

  /**
   * Subscribe to anchor updates
   */
  onAnchorUpdate(callback: (event: AnchorUpdateEvent) => void): () => void {
    const subscription = this.eventEmitter.addListener('onAnchorUpdate', callback);
    return () => subscription.remove();
  }

  /**
   * Subscribe to error events
   */
  onError(callback: (event: ErrorEvent) => void): () => void {
    const subscription = this.eventEmitter.addListener('onError', callback);
    return () => subscription.remove();
  }
}

export const ARKitBridge = new ARKitBridgeClass();
export type {
  HitTestResult,
  AnchorResult,
  TrackingStateResult,
  MeasurementResult,
  PhotoResult,
  FrameEvent,
  AnchorUpdateEvent,
  ErrorEvent,
};
