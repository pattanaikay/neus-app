// components/moodcard.js

import React from 'react';
import { TouchableOpacity, Text } from 'react-native';

const MoodCard = ({ label, selected, onPress }) => (
  <TouchableOpacity
    onPress={onPress}
    style={{
      padding: 12,
      backgroundColor: selected ? '#2196F3' : '#eee',
      marginVertical: 6,
      borderRadius: 10
    }}
  >
    <Text style={{ color: selected ? '#fff' : '#000', fontSize: 16 }}>{label}</Text>
  </TouchableOpacity>
);

export default MoodCard;
