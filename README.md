# 🧠 Neus App – Real-Time Emotion Support App

**ANeus App** is a cross-platform mobile application that provides users with real-time emotional support through interactive tools like breathing exercises, journaling, and grounding techniques. The app uses a **pretrained deep learning model** to analyze text input and classify the user's emotional state, offering context-aware suggestions to help them cope.

---

## ✨ Features

- 🌈 **Card-Based Mood Interaction UI** (Flutter)
- 🧠 **Emotion Detection** from short user input (using DistilBERT + FastAPI)
- 🧘‍♀️ **Personalized Coping Tools**:
  - Guided breathing
  - Quick journal
  - Grounding technique
  - Call a friend
- 🔔 **Push Notifications** via Firebase Cloud Messaging
- 🔒 **Privacy-First**: No camera or microphone needed

---

## 🧩 Project Structure

### 1. `frontend/` (Flutter)
- Card-style screens for:
  - Mood selection
  - Journal input
  - Coping tool suggestions
- Integrated with Firebase:
  - `Firestore`: Mood & journal logs
  - `Cloud Messaging`: Push reminders
- Configurable Firebase onboarding

---

### 2. `backend/` (FastAPI)
- Hosts a pretrained emotion classifier (`DistilBERT` fine-tuned on [GoEmotions](https://github.com/google-research/google-research/tree/master/goemotions))
- `/predict` endpoint accepts user input text and returns:
  - Predicted emotion label
  - Confidence score
  - Suggested coping tool

---

### 3. `model/`
- Python script to download and save the model from HuggingFace
- (Optional) Export scripts for ONNX or TFLite
- Easily swappable for different emotion models

---

### 4. `docs/`
- `architecture.drawio`: Editable system architecture diagram
- `architecture.md`: Markdown version of architecture

---

### 5. `docker-compose.yml`
- Quick-start for backend server and model
- One command to launch API server locally

---

## 🚀 Getting Started

### 🔧 Prerequisites
- [Flutter](https://flutter.dev/docs/get-started/install)
- Python 3.8+
- `pip install fastapi transformers torch uvicorn`
- Firebase account + Firebase CLI

---

### ▶️ Run the Backend API

```bash
cd backend/
uvicorn main:app --reload
