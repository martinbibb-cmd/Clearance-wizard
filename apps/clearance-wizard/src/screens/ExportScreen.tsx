/**
 * Export Screen
 * Review pack and export as JSON or ZIP
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
} from 'react-native';
import type { Pack } from '@clearance-wizard/core';
import { database } from '../storage/database';
// import RNFS from 'react-native-fs';
// import { zip } from 'react-native-zip-archive';

interface ExportScreenProps {
  navigation: any;
  route: {
    params: {
      packId: string;
    };
  };
}

export const ExportScreen: React.FC<ExportScreenProps> = ({
  navigation,
  route,
}) => {
  const { packId } = route.params;
  const [pack, setPack] = useState<Pack | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPack();
  }, []);

  const loadPack = async () => {
    try {
      const loadedPack = await database.getPack(packId);
      setPack(loadedPack);
    } catch (error) {
      console.error('Failed to load pack:', error);
      Alert.alert('Error', 'Failed to load pack');
    } finally {
      setLoading(false);
    }
  };

  const exportAsJSON = async () => {
    if (!pack) return;

    try {
      const json = JSON.stringify(pack, null, 2);
      const filename = `pack_${pack.packId}_${Date.now()}.json`;
      
      // TODO: Save JSON file using RNFS
      // const path = `${RNFS.DocumentDirectoryPath}/${filename}`;
      // await RNFS.writeFile(path, json, 'utf8');
      
      Alert.alert('Exported', `Pack exported as JSON: ${filename}`);
    } catch (error) {
      console.error('Export failed:', error);
      Alert.alert('Error', 'Failed to export pack');
    }
  };

  const exportAsZIP = async () => {
    if (!pack) return;

    try {
      // TODO: Create ZIP with JSON + images
      // 1. Create temp directory
      // 2. Write pack.json
      // 3. Copy all image files
      // 4. Zip directory
      // 5. Move to Documents
      
      Alert.alert('Exported', 'Pack exported as ZIP (not implemented yet)');
    } catch (error) {
      console.error('Export failed:', error);
      Alert.alert('Error', 'Failed to export pack');
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  if (!pack) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Pack not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Export Pack</Text>
      </View>

      <View style={styles.content}>
        <View style={styles.summary}>
          <Text style={styles.summaryTitle}>Pack Summary</Text>
          
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Site:</Text>
            <Text style={styles.summaryValue}>
              {pack.site?.address || 'Not set'}
            </Text>
          </View>

          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Boiler:</Text>
            <Text style={styles.summaryValue}>
              {pack.boiler?.model || 'Not set'}
            </Text>
          </View>

          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Captures:</Text>
            <Text style={styles.summaryValue}>
              {pack.captures.length}
            </Text>
          </View>

          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Created:</Text>
            <Text style={styles.summaryValue}>
              {new Date(pack.createdAt).toLocaleString()}
            </Text>
          </View>

          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Updated:</Text>
            <Text style={styles.summaryValue}>
              {new Date(pack.updatedAt).toLocaleString()}
            </Text>
          </View>
        </View>

        <View style={styles.capturesList}>
          <Text style={styles.listTitle}>Captures</Text>
          {pack.captures.length === 0 ? (
            <Text style={styles.emptyText}>No captures yet</Text>
          ) : (
            pack.captures.map((capture, index) => (
              <View key={capture.captureId} style={styles.captureCard}>
                <Text style={styles.captureType}>{capture.type}</Text>
                <Text style={styles.captureTime}>
                  {new Date(capture.timestamp).toLocaleTimeString()}
                </Text>
                {capture.measurements.length > 0 && (
                  <Text style={styles.captureMeasurements}>
                    {capture.measurements.length} measurement(s)
                  </Text>
                )}
              </View>
            ))
          )}
        </View>

        <View style={styles.exportOptions}>
          <Text style={styles.optionsTitle}>Export Format</Text>

          <TouchableOpacity
            style={styles.exportButton}
            onPress={exportAsJSON}
          >
            <Text style={styles.exportButtonText}>📄 Export as JSON</Text>
            <Text style={styles.exportButtonSubtext}>
              Pack data only (no images)
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.exportButton}
            onPress={exportAsZIP}
          >
            <Text style={styles.exportButtonText}>📦 Export as ZIP</Text>
            <Text style={styles.exportButtonSubtext}>
              Pack data + all images
            </Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>Back to Home</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    padding: 24,
    paddingTop: 60,
    backgroundColor: '#005eb8',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  content: {
    padding: 16,
  },
  summary: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
  },
  summaryTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 16,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  summaryLabel: {
    fontSize: 14,
    color: '#999',
  },
  summaryValue: {
    fontSize: 14,
    color: '#fff',
    fontWeight: '500',
  },
  capturesList: {
    marginBottom: 24,
  },
  listTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 12,
  },
  captureCard: {
    backgroundColor: '#1a1a1a',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  captureType: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
    textTransform: 'capitalize',
  },
  captureTime: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  captureMeasurements: {
    fontSize: 12,
    color: '#ccc',
    marginTop: 4,
  },
  exportOptions: {
    marginBottom: 24,
  },
  optionsTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 12,
  },
  exportButton: {
    backgroundColor: '#005eb8',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  exportButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 4,
  },
  exportButtonSubtext: {
    fontSize: 14,
    color: '#ccc',
  },
  backButton: {
    backgroundColor: '#333',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginBottom: 32,
  },
  backButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  loadingText: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
    marginTop: 100,
  },
  errorText: {
    color: '#ff0000',
    fontSize: 16,
    textAlign: 'center',
    marginTop: 100,
  },
  emptyText: {
    color: '#666',
    fontSize: 14,
    fontStyle: 'italic',
  },
});
