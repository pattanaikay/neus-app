// screens/moodscreen.js

import React, { useState } from 'react';
import { View, Text, Button, TouchableOpacity } from 'react-native';
import { logMood } from '../services/apiservice';

const moods = ['Happy', 'Sad', 'Anxious', 'Excited'];

export default function MoodScreen({ navigation }) {
  const [selectedMood, setSelectedMood] = useState(null);

  const handleContinue = async () => {
    if (!selectedMood) return;
    const result = await logMood({ mood: selectedMood, userId: 'user123' });
    navigation.navigate('CopingSuggestions', {
      suggestions: result.coping_suggestions,
      mood: selectedMood,
    });
  };

  return (
    <View style={{ padding: 20 }}>
      <Text>Select your mood:</Text>
      {moods.map((mood) => (
        <TouchableOpacity key={mood} onPress={() => setSelectedMood(mood)}>
          <Text style={{ fontSize: 18 }}>{mood}</Text>
        </TouchableOpacity>
      ))}
      {selectedMood && (
        <Button title="Continue" onPress={handleContinue} />
      )}
    </View>
  );
}
