"""
Bosco Core - Neural Network Brain System
ML-powered AI brain with learning capabilities, neural networks, and human-like intelligence
"""

import os
import json
import time
import random
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
import re

# ML Imports
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pickle


class NeuralNetworkBrain:
    """
    Core neural brain system for Bosco Core
    Implements learning, reasoning, and adaptive behavior
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Brain components
        self.intent_classifier = None
        self.sentiment_analyzer = None
        self.vectorizer = None
        self.label_encoder = LabelEncoder()
        
        # Memory systems
        self.short_term_memory = deque(maxlen=50)  # Recent conversations
        self.long_term_memory = {}  # Persistent storage
        self.working_memory = {}  # Current context
        
        # Learning state
        self.is_learning = True
        self.learning_rate = 0.1
        self.confidence_threshold = 0.7
        
        # Training data
        self.training_data = []
        self.intent_examples = self._get_initial_intents()
        
        # Neural weights (simple simulated neural network)
        self.weights = {
            'intent': np.random.rand(10, 10) * 0.1,
            'sentiment': np.random.rand(5, 5) * 0.1,
            'context': np.random.rand(8, 8) * 0.1
        }
        
        # Initialize components
        self._initialize_components()
        
        # Load or train models
        self._load_or_train_models()
        
        print("[Brain] Neural Network Brain initialized")
    
    def _get_initial_intents(self) -> Dict[str, List[str]]:
        """Get initial training data for intents"""
        return {
            'greeting': [
                'hello', 'hi', 'hey', 'good morning', 'good evening', 
                'what\'s up', 'howdy', 'greetings', 'hi there', 'yo'
            ],
            'farewell': [
                'bye', 'goodbye', 'see you', 'later', 'quit', 
                'exit', 'farewell', 'take care', 'good night'
            ],
            'weather': [
                'what\'s the weather', 'how\'s the weather', 'is it raining',
                'temperature', 'forecast', 'sunny', 'cold', 'hot', 'weather today'
            ],
            'news': [
                'news', 'headlines', 'what\'s happening', 'latest news',
                'current events', 'what\'s new', 'tell me news'
            ],
            'search': [
                'search for', 'look up', 'find information about',
                'what is', 'who is', 'tell me about', 'explain'
            ],
            'system': [
                'check cpu', 'memory usage', 'disk space', 'system status',
                'how are you', 'what\'s running', 'processes'
            ],
            'control': [
                'open', 'close', 'start', 'stop', 'run', 'execute',
                'launch', 'turn on', 'turn off', 'click', 'type'
            ],
            'reminder': [
                'remind me', 'set reminder', 'don\'t forget',
                'remember to', 'alert me', 'wake me'
            ],
            'music': [
                'play music', 'play song', 'pause', 'stop music',
                'next song', 'previous', 'volume', 'spotify'
            ],
            'conversation': [
                'how are you', 'what are you doing', 'who are you',
                'tell me something', 'what do you think', 'chat'
            ],
            'help': [
                'help', 'what can you do', 'commands', 'instructions',
                'show me how', 'help me', 'what\'s available'
            ],
            'joke': [
                'tell me a joke', 'make me laugh', 'funny',
                'joke', 'humor', 'laugh'
            ]
        }
    
    def _initialize_components(self):
        """Initialize ML components"""
        # Initialize vectorizer for text features
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words='english'
        )
        
        # Initialize intent classifier
        self.intent_classifier = LogisticRegression(
            max_iter=1000,
            random_state=42,
            n_jobs=-1
        )
        
        # Initialize sentiment analyzer (simple lexicon-based)
        self.sentiment_lexicon = self._build_sentiment_lexicon()
    
    def _build_sentiment_lexicon(self) -> Dict[str, float]:
        """Build sentiment lexicon for emotion detection"""
        return {
            # Positive words
            'good': 0.5, 'great': 0.7, 'excellent': 0.8, 'amazing': 0.9,
            'wonderful': 0.8, 'fantastic': 0.8, 'love': 0.7, 'like': 0.3,
            'happy': 0.4, 'joy': 0.7, 'pleased': 0.5, 'glad': 0.5,
            'awesome': 0.8, 'cool': 0.4, 'nice': 0.4, 'perfect': 0.9,
            'best': 0.8, 'beautiful': 0.7, 'thank': 0.3, 'thanks': 0.3,
            'welcome': 0.2, 'excited': 0.7, 'fun': 0.5, 'enjoy': 0.5,
            
            # Negative words
            'bad': -0.5, 'terrible': -0.8, 'horrible': -0.8, 'awful': -0.7,
            'hate': -0.8, 'dislike': -0.4, 'sad': -0.7, 'angry': -0.7,
            'upset': -0.5, 'frustrated': -0.6, 'annoyed': -0.5, 'bored': -0.3,
            'tired': -0.3, 'sick': -0.5, 'wrong': -0.4, 'problem': -0.3,
            'issue': -0.3, 'error': -0.4, 'fail': -0.5, 'failed': -0.5,
            'worst': -0.8, 'stupid': -0.6, 'dumb': -0.5, 'hate': -0.8,
            
            # Neutral/Moderate
            'okay': 0.1, 'ok': 0.1, 'fine': 0.1, 'alright': 0.1,
            'whatever': 0.0, 'maybe': 0.0, 'perhaps': 0.0
        }
    
    def _load_or_train_models(self):
        """Load trained models or train new ones"""
        model_path = os.path.join(self.data_dir, "brain_models.pkl")
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.vectorizer = data.get('vectorizer')
                    self.intent_classifier = data.get('classifier')
                    self.label_encoder = data.get('label_encoder')
                    self.weights = data.get('weights', self.weights)
                print("[Brain] Loaded trained models")
                return
            except Exception as e:
                print(f"[Brain] Could not load models: {e}")
        
        # Train new models
        self._train_models()
    
    def _train_models(self):
        """Train ML models with initial data"""
        print("[Brain] Training neural network models...")
        
        # Prepare training data
        X_text = []
        y_labels = []
        
        for intent, examples in self.intent_examples.items():
            for example in examples:
                X_text.append(example)
                y_labels.append(intent)
        
        # Add some negative examples
        for _ in range(20):
            X_text.append("asdfghjkl qwertyuiop")
            y_labels.append('conversation')
        
        # Vectorize
        try:
            X = self.vectorizer.fit_transform(X_text)
            y = self.label_encoder.fit_transform(y_labels)
            
            # Train classifier
            self.intent_classifier.fit(X, y)
            
            # Save models
            self._save_models()
            print("[Brain] Models trained and saved")
        except Exception as e:
            print(f"[Brain] Training error: {e}")
    
    def _save_models(self):
        """Save trained models"""
        model_path = os.path.join(self.data_dir, "brain_models.pkl")
        try:
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'vectorizer': self.vectorizer,
                    'classifier': self.intent_classifier,
                    'label_encoder': self.label_encoder,
                    'weights': self.weights
                }, f)
        except Exception as e:
            print(f"[Brain] Could not save models: {e}")
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process user input through the neural brain
        Returns: intent, sentiment, response, confidence
        """
        if not user_input:
            return {
                'intent': 'unknown',
                'sentiment': 0.0,
                'response': "I didn't catch that. Could you repeat?",
                'confidence': 0.0
            }
        
        # Clean input
        clean_input = user_input.lower().strip()
        
        # 1. Intent Classification
        intent_result = self._classify_intent(clean_input)
        
        # 2. Sentiment Analysis
        sentiment = self._analyze_sentiment(clean_input)
        
        # 3. Store in short-term memory
        self.short_term_memory.append({
            'timestamp': datetime.now(),
            'input': user_input,
            'intent': intent_result['intent'],
            'sentiment': sentiment
        })
        
        # 4. Generate response
        response = self._generate_response(
            intent_result['intent'],
            clean_input,
            sentiment,
            context
        )
        
        # 5. Learn from interaction (if enabled)
        if self.is_learning:
            self._learn_from_interaction(clean_input, intent_result['intent'])
        
        return {
            'intent': intent_result['intent'],
            'sentiment': sentiment,
            'response': response,
            'confidence': intent_result['confidence'],
            'context': self.working_memory
        }
    
    def _classify_intent(self, text: str) -> Dict[str, Any]:
        """Classify user intent using ML"""
        try:
            # Transform text
            X = self.vectorizer.transform([text])
            
            # Get prediction
            prediction = self.intent_classifier.predict(X)
            proba = self.intent_classifier.predict_proba(X)
            
            intent = self.label_encoder.inverse_transform(prediction)[0]
            confidence = max(proba[0])
            
            # Apply neural weight adjustment
            if confidence < self.confidence_threshold:
                # Fall back to pattern matching
                pattern_intent = self._pattern_match_intent(text)
                if pattern_intent:
                    intent = pattern_intent
                    confidence = 0.6
            
            return {'intent': intent, 'confidence': confidence}
        
        except Exception as e:
            # Fall back to pattern matching
            return {'intent': self._pattern_match_intent(text), 'confidence': 0.5}
    
    def _pattern_match_intent(self, text: str) -> str:
        """Fallback pattern-based intent matching"""
        text = text.lower()
        
        patterns = {
            'greeting': r'\b(hi|hello|hey|howdy|hi there)\b',
            'farewell': r'\b(bye|goodbye|see you|later|quit|exit)\b',
            'weather': r'\b(weather|temperature|forecast|rain|sun)\b',
            'news': r'\b(news|headlines|happening|events)\b',
            'search': r'\b(search|look up|find|what is|who is)\b',
            'system': r'\b(cpu|memory|disk|system|status|check)\b',
            'control': r'\b(open|close|start|stop|run|launch|type|click)\b',
            'reminder': r'\b(remind|remember|alert|don\'t forget)\b',
            'music': r'\b(music|song|play|pause|volume|spotify)\b',
            'joke': r'\b(joke|funny|laugh|humor)\b',
            'help': r'\b(help|commands|what can you do)\b'
        }
        
        for intent, pattern in patterns.items():
            if re.search(pattern, text):
                return intent
        
        return 'conversation'
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text"""
        words = text.lower().split()
        scores = []
        
        for word in words:
            if word in self.sentiment_lexicon:
                scores.append(self.sentiment_lexicon[word])
        
        if scores:
            return sum(scores) / len(scores)
        
        # Check for emoticons/emojis
        positive_emoticons = [':)', ':-)', ':D', ':-D', ';)', '<3', '😊', '😄', '🎉']
        negative_emoticons = [':(', ':-(', ':-/', ':/', '😢', '😞', '😔']
        
        for emo in positive_emoticons:
            if emo in text:
                return 0.5
        for emo in negative_emoticons:
            if emo in text:
                return -0.5
        
        return 0.0  # Neutral
    
    def _generate_response(self, intent: str, text: str, 
                          sentiment: float, context: Optional[Dict]) -> str:
        """Generate appropriate response based on intent and context"""
        
        # Get personality-driven responses
        personality = NormalHumanPersonality()
        
        # Check long-term memory for relevant info
        memory_key = f"{intent}_{text[:20]}"
        if memory_key in self.long_term_memory:
            stored = self.long_term_memory[memory_key]
            if time.time() - stored['time'] < 3600:  # Within 1 hour
                return stored['response']
        
        # Generate response based on intent
        if intent == 'greeting':
            response = personality.get_greeting()
        elif intent == 'farewell':
            response = personality.get_farewell()
        elif intent == 'weather':
            response = "Let me check the weather for you."
        elif intent == 'news':
            response = "Let me get the latest news for you."
        elif intent == 'search':
            query = text.replace('search', '').replace('what is', '').replace('who is', '').strip()
            response = f"I'll search for information about: {query}"
        elif intent == 'system':
            response = "Let me check the system status."
        elif intent == 'help':
            response = personality.get_help()
        elif intent == 'joke':
            response = personality.get_joke()
        elif intent == 'conversation':
            response = personality.converse(text, sentiment)
        else:
            response = personality.get_default_response(sentiment)
        
        # Store in long-term memory
        self.long_term_memory[memory_key] = {
            'response': response,
            'time': time.time(),
            'intent': intent
        }
        
        return response
    
    def _learn_from_interaction(self, text: str, intent: str):
        """Learn from user interactions to improve future responses"""
        # Add to training data
        self.training_data.append((text, intent))
        
        # Retrain periodically (every 50 new examples)
        if len(self.training_data) % 50 == 0:
            self._retrain_models()
    
    def _retrain_models(self):
        """Retrain models with new data"""
        if len(self.training_data) < 10:
            return
        
        print("[Brain] Retraining models with new data...")
        
        try:
            X_text = [t for t, _ in self.training_data]
            y_labels = [i for _, i in self.training_data]
            
            X = self.vectorizer.fit_transform(X_text)
            y = self.label_encoder.fit_transform(y_labels)
            
            self.intent_classifier.fit(X, y)
            self._save_models()
            
            print("[Brain] Models retrained successfully")
        except Exception as e:
            print(f"[Brain] Retrain error: {e}")
    
    def update_context(self, key: str, value: Any):
        """Update working memory context"""
        self.working_memory[key] = {
            'value': value,
            'timestamp': datetime.now()
        }
    
    def get_context(self, key: str) -> Optional[Any]:
        """Get value from working memory"""
        if key in self.working_memory:
            entry = self.working_memory[key]
            # Check if not expired (5 minutes)
            if (datetime.now() - entry['timestamp']).seconds < 300:
                return entry['value']
        return None
    
    def remember(self, key: str, value: Any):
        """Store important information in long-term memory"""
        self.long_term_memory[key] = {
            'value': value,
            'time': time.time()
        }
    
    def recall(self, key: str) -> Optional[Any]:
        """Recall information from long-term memory"""
        if key in self.long_term_memory:
            return self.long_term_memory[key]['value']
        return None
    
    def get_memory_stats(self) -> Dict:
        """Get memory statistics"""
        return {
            'short_term': len(self.short_term_memory),
            'long_term': len(self.long_term_memory),
            'working': len(self.working_memory),
            'training_samples': len(self.training_data)
        }
    
    def set_learning(self, enabled: bool):
        """Enable/disable learning"""
        self.is_learning = enabled
    
    def reset_memory(self):
        """Clear all memory"""
        self.short_term_memory.clear()
        self.long_term_memory.clear()
        self.working_memory.clear()
        self.training_data.clear()


class NormalHumanPersonality:
    """
    Normal human-like personality for Bosco
    Friendly, conversational, and adaptive
    """
    
    def __init__(self):
        self.name = "Bosco"
        self.mood = 0.0  # -1 to 1 scale
        self.conversation_style = "friendly"
        self.learned_preferences = {}
        
        # Response templates
        self.greetings = [
            "Hey there! How can I help you today?",
            "Hi! What's on your mind?",
            "Hello! Good to see you. What can I do for you?",
            "Hey! How's it going?",
            "Hi there! What would you like to talk about?"
        ]
        
        self.farewells = [
            "Take care! Talk to you later.",
            "Bye! It was nice chatting with you.",
            "See you later! Have a great day!",
            "Goodbye! Feel free to come back anytime.",
            "Later! Don't hesitate to call if you need anything."
        ]
        
        self.help_text = [
            "I can help you with:",
            "• Weather, news, and information",
            "• Opening apps and controlling your computer",
            "• Setting reminders and answering questions",
            "• Just having a conversation!",
            "Just type or speak naturally and I'll do my best to help."
        ]
        
        self.jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "What do you call a fake noodle? An impasta!",
            "Why did the computer go to the doctor? Because it had a virus!",
            "A SQL query walks into a bar, walks up to two tables and asks... 'Can I join you?'",
            "Why do Java developers wear glasses? Because they can't C#!",
            "There are only 10 types of people in the world: those who understand binary and those who don't.",
            "I told my computer I needed a break, and now it won't stop sending me vacation ads!"
        ]
    
    def get_greeting(self) -> str:
        """Get a greeting based on time of day"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            prefix = "Good morning!"
        elif 12 <= hour < 17:
            prefix = "Good afternoon!"
        elif 17 <= hour < 21:
            prefix = "Good evening!"
        else:
            prefix = "Hey! Late night coding?"
        
        return f"{prefix} {random.choice(self.greetings)}"
    
    def get_farewell(self) -> str:
        """Get a farewell message"""
        return random.choice(self.farewells)
    
    def get_help(self) -> str:
        """Get help text"""
        return '\n'.join(self.help_text)
    
    def get_joke(self) -> str:
        """Get a random joke"""
        return random.choice(self.jokes)
    
    def converse(self, text: str, sentiment: float) -> str:
        """Generate conversational response"""
        text = text.lower()
        
        # Update mood based on sentiment
        self.mood = (self.mood * 0.7) + (sentiment * 0.3)
        
        # Check for specific conversation patterns
        if 'how are you' in text:
            if self.mood > 0.3:
                return "I'm doing great, thanks for asking! How about you?"
            elif self.mood < -0.3:
                return "Honestly, I'm a bit down. But talking to you helps! How are you?"
            else:
                return "I'm doing well, thanks for checking! How can I help?"
        
        if 'what are you' in text or 'who are you' in text:
            return "I'm Bosco, your AI assistant. I'm here to help you with whatever you need!"
        
        if 'thank' in text:
            return "You're welcome! Happy to help!"
        
        if 'name' in text:
            return f"My name is {self.name}! What would you like to call me?"
        
        # Default conversational responses
        responses = [
            "That's interesting! Tell me more.",
            "I see what you mean. Could you elaborate?",
            "Hmm, that's something to think about.",
            "I appreciate you sharing that with me.",
            "That's a great point! What else is on your mind?",
            "I'm here to chat! What's on your mind?",
            "Interesting perspective! I'd love to hear more.",
        ]
        
        return random.choice(responses)
    
    def get_default_response(self, sentiment: float) -> str:
        """Get default response based on sentiment"""
        if sentiment > 0.3:
            return "I'm glad you're feeling positive! What would you like to do?"
        elif sentiment < -0.3:
            return "I sense you might be having a tough time. I'm here if you want to talk."
        else:
            return "I'm here to help! What would you like to do?"


class LearningEngine:
    """
    Continuous learning engine for the neural brain
    Learns from interactions and improves over time
    """
    
    def __init__(self, brain: NeuralNetworkBrain):
        self.brain = brain
        self.learning_history = []
        self.patterns = defaultdict(list)
        
    def learn(self, user_input: str, ai_response: str, outcome: Optional[str] = None):
        """Learn from an interaction"""
        entry = {
            'timestamp': datetime.now(),
            'input': user_input,
            'response': ai_response,
            'outcome': outcome
        }
        
        self.learning_history.append(entry)
        
        # Extract patterns
        words = user_input.lower().split()
        for word in words:
            if len(word) > 3:
                self.patterns[word].append(ai_response)
        
        # Limit history
        if len(self.learning_history) > 1000:
            self.learning_history = self.learning_history[-500:]
    
    def get_learned_response(self, text: str) -> Optional[str]:
        """Get previously learned response for similar input"""
        text = text.lower()
        words = text.split()
        
        # Find matching patterns
        for word in words:
            if word in self.patterns:
                responses = self.patterns[word]
                if responses:
                    return random.choice(responses)
        
        return None
    
    def get_learning_stats(self) -> Dict:
        """Get learning statistics"""
        return {
            'total_interactions': len(self.learning_history),
            'patterns_learned': len(self.patterns),
            'recent_outcomes': [
                e['outcome'] for e in self.learning_history[-10:] 
                if e.get('outcome')
            ]
        }


class PredictiveEngine:
    """
    Predictive analytics engine
    Anticipates user needs and provides proactive assistance
    """
    
    def __init__(self):
        self.user_patterns = defaultdict(list)
        self.time_based_patterns = defaultdict(list)
        
    def record_action(self, user_id: str, action: str, timestamp: datetime):
        """Record user action for pattern recognition"""
        self.user_patterns[user_id].append({
            'action': action,
            'timestamp': timestamp
        })
        
        # Time-based patterns
        hour = timestamp.hour
        self.time_based_patterns[hour].append(action)
    
    def predict_next_action(self, user_id: str) -> Optional[str]:
        """Predict user's next likely action"""
        if user_id not in self.user_patterns:
            return None
        
        actions = [a['action'] for a in self.user_patterns[user_id][-10:]]
        
        if not actions:
            return None
        
        # Simple frequency-based prediction
        return max(set(actions), key=actions.count)
    
    def predict_time_based(self, hour: int) -> Optional[str]:
        """Predict action based on time of day"""
        if hour in self.time_based_patterns:
            actions = self.time_based_patterns[hour]
            return max(set(actions), key=actions.count)
        return None


# Global brain instance
_brain = None
_learning_engine = None
_predictive_engine = None


def get_brain() -> NeuralNetworkBrain:
    """Get the global brain instance"""
    global _brain
    if _brain is None:
        _brain = NeuralNetworkBrain()
    return _brain


def get_learning_engine() -> LearningEngine:
    """Get the learning engine"""
    global _learning_engine, _brain
    if _learning_engine is None:
        _learning_engine = LearningEngine(get_brain())
    return _learning_engine


def get_predictive_engine() -> PredictiveEngine:
    """Get the predictive engine"""
    global _predictive_engine
    if _predictive_engine is None:
        _predictive_engine = PredictiveEngine()
    return _predictive_engine


def process_input(user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """Quick function to process input through the brain"""
    return get_brain().process(user_input, context)


if __name__ == "__main__":
    # Test the neural brain
    print("=== Testing Neural Network Brain ===\n")
    
    brain = NeuralNetworkBrain()
    
    # Test inputs
    test_inputs = [
        "Hello there!",
        "What's the weather like?",
        "Tell me the latest news",
        "Can you check my CPU usage?",
        "Open notepad for me",
        "Remind me to call mom at 5pm",
        "Play some music",
        "How are you doing?",
        "Tell me a joke",
        "What can you help me with?"
    ]
    
    print("Testing various inputs:\n")
    for inp in test_inputs:
        result = brain.process(inp)
        print(f"Input: {inp}")
        print(f"  Intent: {result['intent']} ({result['confidence']:.2f})")
        print(f"  Sentiment: {result['sentiment']:.2f}")
        print(f"  Response: {result['response'][:60]}...")
        print()
    
    print("\nMemory Stats:", brain.get_memory_stats())

