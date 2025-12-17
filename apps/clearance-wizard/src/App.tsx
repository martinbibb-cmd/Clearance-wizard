/**
 * Main App Component
 * Navigation setup and app entry point
 */

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { HomeScreen } from './screens/HomeScreen';
import { SiteDetailsScreen } from './screens/SiteDetailsScreen';
import { ARMeasureScreen } from './screens/ARMeasureScreen';
import { ExportScreen } from './screens/ExportScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerShown: false,
          animation: 'slide_from_right',
        }}
      >
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="SiteDetails" component={SiteDetailsScreen} />
        <Stack.Screen name="ARMeasure" component={ARMeasureScreen} />
        <Stack.Screen name="Export" component={ExportScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
