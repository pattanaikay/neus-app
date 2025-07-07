// app.js
import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from './screens/homescreen';
import MoodScreen from './screens/moodscreen';
import JournalScreen from './screens/journalscreen';
import InsightsScreen from './screens/InsightsScreen';
import CopingSuggestionsScreen from './screens/CopingSuggestionsScreen';
import { initializeNotificationService } from './services/notificationservice';

const Stack = createStackNavigator();

const App = () => {
  useEffect(() => {
    initializeNotificationService();
  }, []);

  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Mood" component={MoodScreen} />
        <Stack.Screen name="Journal" component={JournalScreen} />
        <Stack.Screen name="Insights" component={InsightsScreen} />
        <Stack.Screen name="CopingSuggestions" component={CopingSuggestionsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;
