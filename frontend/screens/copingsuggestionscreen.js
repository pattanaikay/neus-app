// screens/copingsuggestionsscreen.js

import React from 'react';
import { View, Text } from 'react-native';

const CopingSuggestionsScreen = ({ route }) => {
  const { suggestions, mood } = route.params;

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 20, marginBottom: 10 }}>
        Suggestions for feeling {mood}:
      </Text>
      {suggestions.map((suggestion, index) => (
        <Text key={index} style={{ marginBottom: 6 }}>• {suggestion}</Text>
      ))}
    </View>
  );
};

export default CopingSuggestionsScreen;
