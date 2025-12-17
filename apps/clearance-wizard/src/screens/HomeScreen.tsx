/**
 * Home Screen
 * Main entry point - create new pack, continue, or export
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  Alert,
} from 'react-native';
import type { Pack } from '@clearance-wizard/core';
import { database } from '../storage/database';

interface HomeScreenProps {
  navigation: any;
}

export const HomeScreen: React.FC<HomeScreenProps> = ({ navigation }) => {
  const [packs, setPacks] = useState<Pack[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPacks();
  }, []);

  const loadPacks = async () => {
    try {
      setLoading(true);
      const allPacks = await database.listPacks();
      setPacks(allPacks);
    } catch (error) {
      console.error('Failed to load packs:', error);
      Alert.alert('Error', 'Failed to load packs');
    } finally {
      setLoading(false);
    }
  };

  const handleNewPack = () => {
    navigation.navigate('SiteDetails', { packId: null });
  };

  const handleContinuePack = (pack: Pack) => {
    navigation.navigate('ARMeasure', { packId: pack.packId });
  };

  const handleExportPack = (pack: Pack) => {
    navigation.navigate('Export', { packId: pack.packId });
  };

  const renderPack = ({ item }: { item: Pack }) => (
    <View style={styles.packCard}>
      <View style={styles.packHeader}>
        <Text style={styles.packTitle}>
          {item.site?.address || 'Untitled Pack'}
        </Text>
        <Text style={styles.packDate}>
          {new Date(item.updatedAt).toLocaleDateString()}
        </Text>
      </View>
      <Text style={styles.packInfo}>
        {item.captures.length} capture{item.captures.length !== 1 ? 's' : ''}
      </Text>
      <View style={styles.packActions}>
        <TouchableOpacity
          style={[styles.button, styles.buttonSecondary]}
          onPress={() => handleContinuePack(item)}
        >
          <Text style={styles.buttonTextSecondary}>Continue</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.button, styles.buttonSecondary]}
          onPress={() => handleExportPack(item)}
        >
          <Text style={styles.buttonTextSecondary}>Export</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Clearance Wizard</Text>
        <Text style={styles.subtitle}>iOS ARKit Edition</Text>
      </View>

      <TouchableOpacity
        style={[styles.button, styles.buttonPrimary, styles.newPackButton]}
        onPress={handleNewPack}
      >
        <Text style={styles.buttonTextPrimary}>+ New Pack</Text>
      </TouchableOpacity>

      <View style={styles.packsContainer}>
        <Text style={styles.sectionTitle}>Recent Packs</Text>
        {loading ? (
          <Text style={styles.emptyText}>Loading...</Text>
        ) : packs.length === 0 ? (
          <Text style={styles.emptyText}>
            No packs yet. Create your first pack to get started!
          </Text>
        ) : (
          <FlatList
            data={packs}
            renderItem={renderPack}
            keyExtractor={item => item.packId}
            contentContainerStyle={styles.packsList}
          />
        )}
      </View>
    </View>
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
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.8,
  },
  newPackButton: {
    margin: 16,
  },
  packsContainer: {
    flex: 1,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 16,
  },
  packsList: {
    paddingBottom: 16,
  },
  packCard: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  packHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  packTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    flex: 1,
  },
  packDate: {
    fontSize: 14,
    color: '#999',
  },
  packInfo: {
    fontSize: 14,
    color: '#ccc',
    marginBottom: 12,
  },
  packActions: {
    flexDirection: 'row',
    gap: 8,
  },
  button: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonPrimary: {
    backgroundColor: '#005eb8',
  },
  buttonSecondary: {
    backgroundColor: '#333',
    flex: 1,
  },
  buttonTextPrimary: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonTextSecondary: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  emptyText: {
    color: '#666',
    fontSize: 16,
    textAlign: 'center',
    marginTop: 32,
  },
});
