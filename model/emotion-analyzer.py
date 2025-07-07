# model/emotion_analyzer.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import pickle
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """
    Fine-tuned emotion analysis model for mental health applications
    Uses DistilBERT fine-tuned on GoEmotions dataset
    """
    
    def __init__(self, model_name: str = "j-hartmann/emotion-english-distilroberta-base"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.emotion_mapping = {
            'joy': 'positive',
            'optimism': 'positive',
            'love': 'positive',
            'excitement': 'positive',
            'amusement': 'positive',
            'approval': 'positive',
            'caring': 'positive',
            'gratitude': 'positive',
            'desire': 'positive',
            'admiration': 'positive',
            'relief': 'positive',
            'pride': 'positive',
            
            'sadness': 'negative',
            'disappointment': 'negative',
            'anger': 'negative',
            'annoyance': 'negative',
            'grief': 'negative',
            'remorse': 'negative',
            'fear': 'negative',
            'nervousness': 'negative',
            'disgust': 'negative',
            'embarrassment': 'negative',
            'confusion': 'negative',
            
            'neutral': 'neutral',
            'realization': 'neutral',
            'surprise': 'neutral',
            'curiosity': 'neutral'
        }
        
        self.load_model()
    
    def load_model(self):
        """Load the pre-trained emotion analysis model"""
        try:
            logger.info(f"Loading emotion model: {self.model_name}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                return_all_scores=True
            )
            
            logger.info("Emotion model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading emotion model: {e}")
            raise
    
    def analyze_emotion(self, text: str) -> Dict:
        """
        Analyze emotion in text and return comprehensive results
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict: Emotion analysis results
        """
        try:
            # Get emotion predictions
            emotions = self.pipeline(text)
            
            # Process results
            emotion_scores = {}
            dominant_emotion = None
            max_score = 0
            
            for emotion in emotions:
                emotion_name = emotion['label']
                score = emotion['score']
                emotion_scores[emotion_name] = score
                
                if score > max_score:
                    max_score = score
                    dominant_emotion = emotion_name
            
            # Calculate sentiment polarity
            sentiment_score = self._calculate_sentiment_score(emotion_scores)
            mood_category = self._determine_mood_category(emotion_scores, sentiment_score)
            
            # Generate insights
            insights = self._generate_insights(emotion_scores, dominant_emotion, sentiment_score)
            
            return {
                'dominant_emotion': dominant_emotion,
                'confidence': max_score,
                'emotion_scores': emotion_scores,
                'sentiment_score': sentiment_score,
                'mood_category': mood_category,
                'insights': insights,
                'text_length': len(text.split())
            }
            
        except Exception as e:
            logger.error(f"Error analyzing emotion: {e}")
            return {
                'error': str(e),
                'dominant_emotion': 'neutral',
                'confidence': 0.0,
                'emotion_scores': {},
                'sentiment_score': 0.0,
                'mood_category': 'neutral'
            }
    
    def _calculate_sentiment_score(self, emotion_scores: Dict) -> float:
        """Calculate overall sentiment score from emotion scores"""
        positive_emotions = ['joy', 'optimism', 'love', 'excitement', 'amusement', 'approval', 'caring', 'gratitude']
        negative_emotions = ['sadness', 'disappointment', 'anger', 'annoyance', 'grief', 'fear', 'disgust']
        
        positive_score = sum(emotion_scores.get(emotion, 0) for emotion in positive_emotions)
        negative_score = sum(emotion_scores.get(emotion, 0) for emotion in negative_emotions)
        
        # Normalize to [-1, 1] range
        total_score = positive_score + negative_score
        if total_score == 0:
            return 0.0
        
        return (positive_score - negative_score) / total_score
    
    def _determine_mood_category(self, emotion_scores: Dict, sentiment_score: float) -> str:
        """Determine mood category based on emotion analysis"""
        if sentiment_score > 0.3:
            return 'excellent' if sentiment_score > 0.6 else 'good'
        elif sentiment_score > -0.3:
            return 'okay'
        else:
            return 'difficult' if sentiment_score < -0.6 else 'struggling'
    
    def _generate_insights(self, emotion_scores: Dict, dominant_emotion: str, sentiment_score: float) -> List[str]:
        """Generate insights based on emotion analysis"""
        insights = []
        
        # Insight based on dominant emotion
        if dominant_emotion in ['joy', 'optimism', 'love']:
            insights.append("You're experiencing positive emotions. This is a great time to engage in activities you enjoy.")
        elif dominant_emotion in ['sadness', 'disappointment', 'grief']:
            insights.append("It seems you're going through a difficult time. Consider reaching out to someone you trust.")
        elif dominant_emotion in ['anger', 'annoyance']:
            insights.append("You might be feeling frustrated. Try some calming techniques like deep breathing.")
        elif dominant_emotion in ['fear', 'nervousness']:
            insights.append("Anxiety might be affecting you. Grounding techniques could help you feel more centered.")
        
        # Insight based on sentiment score
        if abs(sentiment_score) < 0.2:
            insights.append("Your emotions seem balanced today. This is a good time for reflection and planning.")
        
        # Insight based on emotion diversity
        num_significant_emotions = sum(1 for score in emotion_scores.values() if score > 0.1)
        if num_significant_emotions > 5:
            insights.append("You're experiencing a mix of emotions. This is completely normal and human.")
        
        return insights if insights else ["Every feeling is valid. Take time to acknowledge what you're experiencing."]
    
    def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """Analyze multiple texts at once"""
        return [self.analyze_emotion(text) for text in texts]
    
    def get_mood_trend(self, analyses: List[Dict]) -> Dict:
        """Analyze mood trend over time"""
        if not analyses:
            return {'trend': 'neutral', 'average_sentiment': 0.0}
        
        sentiment_scores = [analysis.get('sentiment_score', 0.0) for analysis in analyses]
        average_sentiment = np.mean(sentiment_scores)
        
        # Calculate trend
        if len(sentiment_scores) > 1:
            trend_slope = np.polyfit(range(len(sentiment_scores)), sentiment_scores, 1)[0]
            if trend_slope > 0.1:
                trend = 'improving'
            elif trend_slope < -0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'trend': trend,
            'average_sentiment': average_sentiment,
            'num_entries': len(analyses),
            'sentiment_range': [min(sentiment_scores), max(sentiment_scores)]
        }

# Fine-tuning script
def fine_tune_model(training_data_path: str, output_model_path: str):
    """
    Fine-tune the emotion model on custom mental health data
    
    Args:
        training_data_path (str): Path to CSV file with 'text' and 'emotion' columns
        output_model_path (str): Path to save the fine-tuned model
    """
    from transformers import TrainingArguments, Trainer
    from torch.utils.data import Dataset
    
    class EmotionDataset(Dataset):
        def __init__(self, texts, labels, tokenizer, max_length=512):
            self.texts = texts
            self.labels = labels
            self.tokenizer = tokenizer
            self.max_length = max_length
        
        def __len__(self):
            return len(self.texts)
        
        def __getitem__(self, idx):
            text = str(self.texts[idx])
            label = self.labels[idx]
            
            encoding = self.tokenizer(
                text,
                truncation=True,
                padding='max_length',
                max_length=self.max_length,
                return_tensors='pt'
            )
            
            return {
                'input_ids': encoding['input_ids'].flatten(),
                'attention_mask': encoding['attention_mask'].flatten(),
                'labels': torch.tensor(label, dtype=torch.long)
            }
    
    # Load training data
    df = pd.read_csv(training_data_path)
    
    # Initialize model and tokenizer
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, 
        num_labels=len(df['emotion'].unique())
    )
    
    # Create dataset
    train_dataset = EmotionDataset(
        df['text'].tolist(),
        df['emotion'].factorize()[0].tolist(),
        tokenizer
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_model_path,
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        save_steps=1000,
        evaluation_strategy="steps",
        eval_steps=1000,
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        tokenizer=tokenizer,
    )
    
    # Train model
    trainer.train()
    
    # Save model
    model.save_pretrained(output_model_path)
    tokenizer.save_pretrained(output_model_path)
    
    logger.info(f"Model fine-tuned and saved to {output_model_path}")

# Usage example
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = EmotionAnalyzer()
    
    # Test with sample text
    test_text = "I feel really sad today and I don't know why. Everything seems overwhelming."
    result = analyzer.analyze_emotion(test_text)
    
    print("Emotion Analysis Results:")
    print(f"Dominant Emotion: {result['dominant_emotion']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Sentiment Score: {result['sentiment_score']:.2f}")
    print(f"Mood Category: {result['mood_category']}")
    print(f"Insights: {result['insights']}")