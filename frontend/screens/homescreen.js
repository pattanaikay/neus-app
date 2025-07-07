// screens/homescreen.js

import React from 'react';
import { View, Text, Button } from 'react-native';

const HomeScreen = ({ navigation }) => (
  <View style={{ padding: 20 }}>
    <Text style={{ fontSize: 24 }}>Welcome to MindfulMe</Text>
    <Button title="Log Mood" onPress={() => navigation.navigate('Mood')} />
    <Button title="Journal" onPress={() => navigation.navigate('Journal')} />
    <Button title="Insights" onPress={() => navigation.navigate('Insights')} />
  </View>
);

export default HomeScreen;
