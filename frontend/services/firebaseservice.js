// services/firebaseservice.js

import { db } from '../firebase';
import { collection, addDoc, getDocs, query, where } from 'firebase/firestore';

export const saveJournalEntry = async (entry) => {
  await addDoc(collection(db, 'journalEntries'), entry);
};

export const getMoodStats = async (userId) => {
  const q = query(collection(db, 'moodLogs'), where('userId', '==', userId));
  const snapshot = await getDocs(q);
  const moodCount = {};

  snapshot.forEach(doc => {
    const mood = doc.data().mood;
    moodCount[mood] = (moodCount[mood] || 0) + 1;
  });

  return Object.entries(moodCount).map(([mood, count]) => ({ mood, count }));
};
