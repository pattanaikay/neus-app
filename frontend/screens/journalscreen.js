// screens/journalscreen.js

import React, { useState } from 'react';
import { View, TextInput, Button, Alert } from 'react-native';
import { saveJournalEntry } from '../services/firebaseservice';

const JournalScreen = () => {
  const [entry, setEntry] = useState('');

  const saveEntry = async () => {
    try {
      await saveJournalEntry({ text: entry, timestamp: new Date(), userId: 'user123' });
      Alert.alert('Saved', 'Your journal entry was saved.');
      setEntry('');
    } catch (error) {
      Alert.alert('Error', 'Could not save entry.');
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <TextInput
        multiline
        placeholder="Write your thoughts here..."
        value={entry}
        onChangeText={setEntry}
        style={{ height: 200, borderWidth: 1, padding: 10, marginBottom: 10 }}
      />
      <Button title="Save Entry" onPress={saveEntry} />
    </View>
  );
};

export default JournalScreen;
