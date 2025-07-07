// services/apiservice.js

import { db } from '../firebase';
import { collection, addDoc } from 'firebase/firestore';

export async function logMood(moodEntry) {
  await addDoc(collection(db, 'moodLogs'), {
    ...moodEntry,
    timestamp: new Date(),
  });

  return {
    coping_suggestions: [
      "Take deep breaths",
      "Practice gratitude",
      "Talk to a friend"
    ]
  };
}
