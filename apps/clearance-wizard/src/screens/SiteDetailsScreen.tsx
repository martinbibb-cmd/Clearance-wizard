/**
 * Site Details Screen
 * Optional minimal site information entry
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
} from 'react-native';
import type { Pack, SiteMetadata, BoilerContext } from '@clearance-wizard/core';
import { database } from '../storage/database';
import { generatePackId } from '../utils/uuid';

interface SiteDetailsScreenProps {
  navigation: any;
  route: {
    params: {
      packId: string | null;
    };
  };
}

export const SiteDetailsScreen: React.FC<SiteDetailsScreenProps> = ({
  navigation,
  route,
}) => {
  const [address, setAddress] = useState('');
  const [leadRef, setLeadRef] = useState('');
  const [customerRef, setCustomerRef] = useState('');
  const [boilerModel, setBoilerModel] = useState('');
  const [boilerLocation, setBoilerLocation] = useState('');
  const [notes, setNotes] = useState('');

  const handleContinue = async () => {
    try {
      const site: SiteMetadata = {
        address: address || undefined,
        leadRef: leadRef || undefined,
        customerRef: customerRef || undefined,
        notes: notes || undefined,
      };

      const boiler: BoilerContext = {
        model: boilerModel || undefined,
        location: boilerLocation || undefined,
      };

      const pack: Pack = {
        packId: route.params.packId || generatePackId(),
        createdAt: Date.now(),
        updatedAt: Date.now(),
        site,
        boiler,
        captures: [],
      };

      await database.createPack(pack);
      
      navigation.navigate('ARMeasure', { packId: pack.packId });
    } catch (error) {
      console.error('Failed to create pack:', error);
      Alert.alert('Error', 'Failed to create pack');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Site Details</Text>
        <Text style={styles.subtitle}>Optional - can be added later</Text>
      </View>

      <View style={styles.form}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Site Information</Text>
          
          <Text style={styles.label}>Address</Text>
          <TextInput
            style={styles.input}
            value={address}
            onChangeText={setAddress}
            placeholder="Street address"
            placeholderTextColor="#666"
          />

          <Text style={styles.label}>Lead Reference</Text>
          <TextInput
            style={styles.input}
            value={leadRef}
            onChangeText={setLeadRef}
            placeholder="Lead ID or reference"
            placeholderTextColor="#666"
          />

          <Text style={styles.label}>Customer Reference</Text>
          <TextInput
            style={styles.input}
            value={customerRef}
            onChangeText={setCustomerRef}
            placeholder="Customer ID or name"
            placeholderTextColor="#666"
          />
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Boiler Context</Text>
          
          <Text style={styles.label}>Model</Text>
          <TextInput
            style={styles.input}
            value={boilerModel}
            onChangeText={setBoilerModel}
            placeholder="Boiler model"
            placeholderTextColor="#666"
          />

          <Text style={styles.label}>Location</Text>
          <TextInput
            style={styles.input}
            value={boilerLocation}
            onChangeText={setBoilerLocation}
            placeholder="e.g., Kitchen, Utility Room"
            placeholderTextColor="#666"
          />
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>Notes</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={notes}
            onChangeText={setNotes}
            placeholder="Additional notes"
            placeholderTextColor="#666"
            multiline
            numberOfLines={4}
          />
        </View>

        <TouchableOpacity
          style={styles.continueButton}
          onPress={handleContinue}
        >
          <Text style={styles.continueButtonText}>Continue to AR</Text>
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
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.8,
  },
  form: {
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ccc',
    marginBottom: 8,
    marginTop: 12,
  },
  input: {
    backgroundColor: '#1a1a1a',
    color: '#fff',
    padding: 12,
    borderRadius: 8,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#333',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  continueButton: {
    backgroundColor: '#005eb8',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 24,
    marginBottom: 32,
  },
  continueButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
});
