// services/notificationservice.js

import messaging from '@react-native-firebase/messaging';

export const initializeNotificationService = async () => {
  const authStatus = await messaging().requestPermission();
  const enabled =
    authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
    authStatus === messaging.AuthorizationStatus.PROVISIONAL;

  if (enabled) {
    const token = await messaging().getToken();
    console.log('FCM Token:', token);
  }
};
