/**
 * AR Measure Screen
 * Main AR interface with camera view, anchor placement, and measurements
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Dimensions,
} from 'react-native';
import { ARKitBridge } from '../native/ARKitBridge';
import type { TrackingState, Point3D } from '@clearance-wizard/core';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

interface ARMeasureScreenProps {
  navigation: any;
  route: {
    params: {
      packId: string;
    };
  };
}

type MeasurementMode = 'point-to-point' | 'clearance';

export const ARMeasureScreen: React.FC<ARMeasureScreenProps> = ({
  navigation,
  route,
}) => {
  const { packId } = route.params;
  
  const [sessionActive, setSessionActive] = useState(false);
  const [trackingState, setTrackingState] = useState<TrackingState>('notAvailable' as TrackingState);
  const [anchorSet, setAnchorSet] = useState(false);
  const [measurementMode, setMeasurementMode] = useState<MeasurementMode>('point-to-point');
  const [measurementStart, setMeasurementStart] = useState<Point3D | null>(null);
  const [currentDistance, setCurrentDistance] = useState<number | null>(null);
  const [confidence, setConfidence] = useState<number>(0);

  const unsubscribeFrame = useRef<(() => void) | null>(null);
  const unsubscribeError = useRef<(() => void) | null>(null);

  useEffect(() => {
    startARSession();
    return () => {
      stopARSession();
    };
  }, []);

  const startARSession = async () => {
    try {
      await ARKitBridge.startSession();
      setSessionActive(true);

      // Subscribe to frame updates for tracking state
      unsubscribeFrame.current = ARKitBridge.onFrame(event => {
        setTrackingState(event.trackingState);
      });

      // Subscribe to errors
      unsubscribeError.current = ARKitBridge.onError(event => {
        Alert.alert('AR Error', event.message);
      });
    } catch (error) {
      Alert.alert('Error', 'Failed to start AR session');
      console.error(error);
    }
  };

  const stopARSession = async () => {
    try {
      if (unsubscribeFrame.current) {
        unsubscribeFrame.current();
      }
      if (unsubscribeError.current) {
        unsubscribeError.current();
      }
      await ARKitBridge.stopSession();
      setSessionActive(false);
    } catch (error) {
      console.error('Failed to stop AR session:', error);
    }
  };

  const handleScreenTap = async (x: number, y: number) => {
    if (!sessionActive) return;

    // Normalize coordinates (0-1)
    const normalizedX = x / SCREEN_WIDTH;
    const normalizedY = y / SCREEN_HEIGHT;

    if (!anchorSet) {
      // First tap: create anchor
      try {
        const hitResult = await ARKitBridge.hitTest(normalizedX, normalizedY);
        await ARKitBridge.createAnchor(hitResult.worldTransform);
        setAnchorSet(true);
        Alert.alert('Anchor Set', 'Anchor placed successfully. Tap to measure.');
      } catch (error) {
        Alert.alert('Error', 'No surface detected. Try pointing at a flat surface.');
      }
    } else {
      // Subsequent taps: measure
      if (!measurementStart) {
        // Start measurement
        try {
          const hitResult = await ARKitBridge.hitTest(normalizedX, normalizedY);
          // Extract position from transform matrix
          const transform = hitResult.worldTransform;
          const point: Point3D = {
            x: transform[12],
            y: transform[13],
            z: transform[14],
          };
          setMeasurementStart(point);
        } catch (error) {
          Alert.alert('Error', 'Could not detect surface');
        }
      } else {
        // End measurement
        try {
          const result = await ARKitBridge.measureRay(
            measurementStart.x / SCREEN_WIDTH,
            measurementStart.y / SCREEN_HEIGHT,
            normalizedX,
            normalizedY
          );
          setCurrentDistance(result.distanceMm);
          setConfidence(result.confidence);
          setMeasurementStart(null);
          
          // Show result
          const distanceCm = (result.distanceMm / 10).toFixed(1);
          Alert.alert(
            'Measurement',
            `Distance: ${distanceCm} cm\nConfidence: ${(result.confidence * 100).toFixed(0)}%`,
            [
              { text: 'Discard', style: 'cancel' },
              {
                text: 'Save',
                onPress: () => saveMeasurement(result.distanceMm, result.confidence),
              },
            ]
          );
        } catch (error) {
          Alert.alert('Error', 'Could not complete measurement');
          setMeasurementStart(null);
        }
      }
    }
  };

  const saveMeasurement = async (distanceMm: number, confidence: number) => {
    // TODO: Save measurement to pack database
    console.log('Saving measurement:', distanceMm, confidence);
    Alert.alert('Saved', 'Measurement saved to pack');
  };

  const handleCapture = async () => {
    try {
      const photo = await ARKitBridge.capturePhoto();
      Alert.alert('Photo Captured', `Saved to: ${photo.localPath}`);
      // TODO: Add photo to pack
    } catch (error) {
      Alert.alert('Error', 'Failed to capture photo');
    }
  };

  const getTrackingStateText = () => {
    switch (trackingState) {
      case 'normal':
        return '✓ Tracking';
      case 'limited':
        return '⚠ Limited Tracking';
      case 'notAvailable':
        return '✗ Tracking Unavailable';
      default:
        return 'Unknown';
    }
  };

  const getTrackingStateColor = () => {
    switch (trackingState) {
      case 'normal':
        return '#00ff00';
      case 'limited':
        return '#ffaa00';
      case 'notAvailable':
        return '#ff0000';
      default:
        return '#ffffff';
    }
  };

  return (
    <View style={styles.container}>
      {/* AR Camera View - Native component would go here */}
      <View style={styles.arView}>
        <TouchableOpacity
          style={styles.arTouchable}
          onPress={(e) => {
            const { locationX, locationY } = e.nativeEvent;
            handleScreenTap(locationX, locationY);
          }}
          activeOpacity={1}
        >
          <View style={styles.arOverlay}>
            <View style={styles.statusBar}>
              <Text style={[styles.trackingState, { color: getTrackingStateColor() }]}>
                {getTrackingStateText()}
              </Text>
            </View>

            {!anchorSet && (
              <View style={styles.instructions}>
                <Text style={styles.instructionText}>
                  Tap a flat surface to place anchor
                </Text>
              </View>
            )}

            {anchorSet && !measurementStart && (
              <View style={styles.instructions}>
                <Text style={styles.instructionText}>
                  Tap to start measuring
                </Text>
              </View>
            )}

            {measurementStart && (
              <View style={styles.instructions}>
                <Text style={styles.instructionText}>
                  Tap second point to complete measurement
                </Text>
              </View>
            )}

            {currentDistance !== null && (
              <View style={styles.measurementDisplay}>
                <Text style={styles.measurementValue}>
                  {(currentDistance / 10).toFixed(1)} cm
                </Text>
                <Text style={styles.confidenceText}>
                  Confidence: {(confidence * 100).toFixed(0)}%
                </Text>
              </View>
            )}
          </View>
        </TouchableOpacity>
      </View>

      {/* Bottom Controls */}
      <View style={styles.controls}>
        <TouchableOpacity style={styles.controlButton} onPress={handleCapture}>
          <Text style={styles.controlButtonText}>📷</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.controlButton}
          onPress={() => {
            setMeasurementStart(null);
            setCurrentDistance(null);
          }}
        >
          <Text style={styles.controlButtonText}>🔄</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.controlButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.controlButtonText}>✓ Done</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  arView: {
    flex: 1,
    backgroundColor: '#000',
  },
  arTouchable: {
    flex: 1,
  },
  arOverlay: {
    flex: 1,
  },
  statusBar: {
    position: 'absolute',
    top: 60,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  trackingState: {
    fontSize: 16,
    fontWeight: 'bold',
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  instructions: {
    position: 'absolute',
    bottom: 120,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  instructionText: {
    fontSize: 18,
    color: '#fff',
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
    textAlign: 'center',
  },
  measurementDisplay: {
    position: 'absolute',
    top: '50%',
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  measurementValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#00ff00',
    textShadowColor: '#000',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  confidenceText: {
    fontSize: 16,
    color: '#fff',
    marginTop: 8,
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 8,
  },
  controls: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingVertical: 16,
    paddingBottom: 32,
    backgroundColor: '#1a1a1a',
  },
  controlButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: '#005eb8',
    borderRadius: 8,
  },
  controlButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
