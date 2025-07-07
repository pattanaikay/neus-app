# backend/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
import os
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import firebase_admin
from firebase_admin import credentials, firestore, messaging
import json

app = FastAPI(title="Mental Health App API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase
cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Load emotion analysis model
emotion_model = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=True
)

# Data models
class MoodEntry(BaseModel):
    mood: str
    journal: Optional[str] = ""
    timestamp: datetime = datetime.now()
    user_id: str

class CopingSuggestion(BaseModel):
    suggestion: str
    category: str
    is_social: bool = False
    friend_name: Optional[str] = None
    activity: Optional[str] = None

class Friend(BaseModel):
    name: str
    favorite_show: str
    last_talked: str
    phone: Optional[str] = None
    
class PushNotification(BaseModel):
    user_id: str
    title: str
    body: str
    data: Optional[dict] = None

# Close friends database
CLOSE_FRIENDS = [
    {"name": "Pratik", "favorite_show": "Silo", "last_talked": "2 days ago", "phone": "+1234567890"},
    {"name": "Maya", "favorite_show": "The Bear", "last_talked": "1 week ago", "phone": "+1234567891"},
    {"name": "Arjun", "favorite_show": "Stranger Things", "last_talked": "3 days ago", "phone": "+1234567892"},
    {"name": "Riya", "favorite_show": "Wednesday", "last_talked": "5 days ago", "phone": "+1234567893"}
]

# Emotion analysis endpoint
@app.post("/predict", response_model=dict)
async def predict_mood_and_suggestions(entry: MoodEntry):
    """
    Analyze journal text and return mood prediction with personalized coping suggestions
    """
    try:
        # Analyze journal text if provided
        emotion_scores = {}
        if entry.journal:
            emotions = emotion_model(entry.journal)
            emotion_scores = {emotion['label']: emotion['score'] for emotion in emotions}
        
        # Get personalized coping suggestions
        suggestions = get_coping_suggestions(entry.mood, entry.user_id)
        
        # Store in Firestore
        doc_ref = db.collection('mood_entries').add({
            'user_id': entry.user_id,
            'mood': entry.mood,
            'journal': entry.journal,
            'timestamp': entry.timestamp,
            'emotion_scores': emotion_scores
        })
        
        return {
            "mood": entry.mood,
            "emotion_analysis": emotion_scores,
            "coping_suggestions": suggestions,
            "entry_id": doc_ref[1].id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_coping_suggestions(mood: str, user_id: str) -> List[CopingSuggestion]:
    """Generate personalized coping suggestions based on mood"""
    import random
    
    # Get user's friends (in production, fetch from user's profile)
    friends = CLOSE_FRIENDS
    random_friend = random.choice(friends)
    
    suggestions_map = {
        "excellent": [
            CopingSuggestion(
                suggestion=f"Let's call {random_friend['name']} and talk about your favorite show {random_friend['favorite_show']}!",
                category="social",
                is_social=True,
                friend_name=random_friend['name'],
                activity=random_friend['favorite_show']
            ),
            CopingSuggestion(
                suggestion="Share your positive energy with someone today",
                category="social",
                is_social=False
            ),
            CopingSuggestion(
                suggestion="Practice gratitude - write down 3 things you're thankful for",
                category="mindfulness",
                is_social=False
            )
        ],
        "good": [
            CopingSuggestion(
                suggestion=f"Text {random_friend['name']} about the latest episode of {random_friend['favorite_show']}",
                category="social",
                is_social=True,
                friend_name=random_friend['name'],
                activity=random_friend['favorite_show']
            ),
            CopingSuggestion(
                suggestion="Take a mindful walk outside",
                category="physical",
                is_social=False
            )
        ],
        "okay": [
            CopingSuggestion(
                suggestion=f"Reach out to {random_friend['name']} - you haven't talked in {random_friend['last_talked']}",
                category="social",
                is_social=True,
                friend_name=random_friend['name']
            ),
            CopingSuggestion(
                suggestion="Practice deep breathing exercises",
                category="mindfulness",
                is_social=False
            )
        ],
        "struggling": [
            CopingSuggestion(
                suggestion=f"Call {random_friend['name']} and catch up about {random_friend['favorite_show']} - connection helps",
                category="social",
                is_social=True,
                friend_name=random_friend['name'],
                activity=random_friend['favorite_show']
            ),
            CopingSuggestion(
                suggestion="Try progressive muscle relaxation",
                category="mindfulness",
                is_social=False
            )
        ],
        "difficult": [
            CopingSuggestion(
                suggestion=f"Text {random_friend['name']} that you need someone to talk to - they care about you",
                category="social",
                is_social=True,
                friend_name=random_friend['name']
            ),
            CopingSuggestion(
                suggestion="Consider professional support",
                category="professional",
                is_social=False
            )
        ]
    }
    
    return suggestions_map.get(mood, [])

# Get mood history
@app.get("/mood-history/{user_id}")
async def get_mood_history(user_id: str, limit: int = 10):
    """Get user's mood history from Firestore"""
    try:
        docs = db.collection('mood_entries')\
                 .where('user_id', '==', user_id)\
                 .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                 .limit(limit)\
                 .stream()
        
        history = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            history.append(data)
        
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Push notification endpoint
@app.post("/send-notification")
async def send_push_notification(notification: PushNotification):
    """Send push notification to user"""
    try:
        # Get user's FCM token from Firestore
        user_doc = db.collection('users').document(notification.user_id).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_doc.to_dict()
        fcm_token = user_data.get('fcm_token')
        
        if not fcm_token:
            raise HTTPException(status_code=400, detail="User has no FCM token")
        
        # Create message
        message = messaging.Message(
            notification=messaging.Notification(
                title=notification.title,
                body=notification.body,
            ),
            data=notification.data or {},
            token=fcm_token,
        )
        
        # Send message
        response = messaging.send(message)
        return {"success": True, "message_id": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get friends list
@app.get("/friends/{user_id}")
async def get_friends(user_id: str):
    """Get user's close friends list"""
    try:
        # In production, fetch from user's profile in Firestore
        return {"friends": CLOSE_FRIENDS}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)