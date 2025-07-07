// screens/insightsscreen.js

import React, { useEffect, useState } from 'react';
import { View, Text, FlatList } from 'react-native';
import { getMoodStats } from '../services/firebaseservice';

const InsightsScreen = () => {
  const [insights, setInsights] = useState([]);

  useEffect(() => {
    getMoodStats('user123').then(data => setInsights(data));
  }, []);

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 20, marginBottom: 10 }}>Mood Insights</Text>
      <FlatList
        data={insights}
        keyExtractor={(item, index) => index.toString()}
        renderItem={({ item }) => <Text>{item.mood}: {item.count}</Text>}
      />
    </View>
  );
};

export default InsightsScreen;
