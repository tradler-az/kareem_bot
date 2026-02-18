"""
Bosco Core - Perception Module
Contextual awareness, pattern recognition, and situational understanding
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import deque
import random


class PerceptionEngine:
    """Perception engine for contextual awareness"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.context_window = self.config.get('context_window', 10)
        
        # Context buffers
        self.conversation_history: deque = deque(maxlen=self.context_window)
        self.command_history: deque = deque(maxlen=50)
        self.time_patterns: Dict[str, List[str]] = {}
        self.mood_history: deque = deque(maxlen=20)
        
        # Current context
        self.current_context: Dict[str, Any] = {
            'time_of_day': self._get_time_of_day(),
            'day_of_week': datetime.now().strftime('%A'),
            'recent_topics': [],
            'user_mood': 'neutral',
            'active_tasks': [],
        }
        
        # Pattern recognition
        self.user_patterns: Dict[str, Any] = {}
        self._load_patterns()
    
    def _get_time_of_day(self) -> str:
        """Get time of day category"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 < hour < 21:
            return 'evening'
        else:
            return 'night'
    
    def _load_patterns(self):
        """Load user patterns from storage"""
        patterns_file = 'data/user_patterns.json'
        if os.path.exists(patterns_file):
            try:
                with open(patterns_file, 'r') as f:
                    self.user_patterns = json.load(f)
            except:
                pass
    
    def _save_patterns(self):
        """Save user patterns"""
        os.makedirs('data', exist_ok=True)
        try:
            with open('data/user_patterns.json', 'w') as f:
                json.dump(self.user_patterns, f, indent=2)
        except:
            pass
    
    def add_interaction(self, user_input: str, response: str, intent: str = None):
        """Add an interaction to the perception buffer"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'response': response,
            'intent': intent,
            'time_of_day': self._get_time_of_day(),
        }
        
        self.conversation_history.append(interaction)
        
        # Track time patterns
        time_key = self._get_time_of_day()
        if time_key not in self.time_patterns:
            self.time_patterns[time_key] = []
        self.time_patterns[time_key].append(user_input)
        
        # Learn from command patterns
        if intent:
            self._learn_pattern(intent, user_input)
    
    def add_command(self, command: str, result: str):
        """Add a command execution to history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'result': result,
        }
        self.command_history.append(entry)
        
        # Learn frequently used commands
        self._learn_command_pattern(command)
    
    def _learn_pattern(self, intent: str, user_input: str):
        """Learn user pattern for an intent"""
        if intent not in self.user_patterns:
            self.user_patterns[intent] = {
                'count': 0,
                'phrases': [],
                'time_preferences': {}
            }
        
        self.user_patterns[intent]['count'] += 1
        self.user_patterns[intent]['phrases'].append(user_input)
        
        # Track time preference
        time_key = self._get_time_of_day()
        time_prefs = self.user_patterns[intent].get('time_preferences', {})
        time_prefs[time_key] = time_prefs.get(time_key, 0) + 1
        
        self._save_patterns()
    
    def _learn_command_pattern(self, command: str):
        """Learn command usage pattern"""
        if 'commands' not in self.user_patterns:
            self.user_patterns['commands'] = {}
        
        if command not in self.user_patterns['commands']:
            self.user_patterns['commands'][command] = {'count': 0, 'last_used': None}
        
        self.user_patterns['commands'][command]['count'] += 1
        self.user_patterns['commands'][command]['last_used'] = datetime.now().isoformat()
        
        self._save_patterns()
    
    def update_mood(self, mood: str):
        """Update current mood perception"""
        self.mood_history.append({
            'mood': mood,
            'timestamp': datetime.now().isoformat()
        })
        self.current_context['user_mood'] = mood
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context"""
        self.current_context['time_of_day'] = self._get_time_of_day()
        self.current_context['recent_topics'] = self._get_recent_topics()
        return self.current_context
    
    def _get_recent_topics(self) -> List[str]:
        """Extract recent conversation topics"""
        topics = []
        for interaction in list(self.conversation_history)[-5:]:
            # Simple keyword extraction
            text = interaction.get('user_input', '').lower()
            words = text.split()
            # Common topic words
            topic_keywords = ['weather', 'news', 'music', 'file', 'system', 'email', 'reminder', 'task']
            for word in words:
                if word in topic_keywords:
                    topics.append(word)
        return list(set(topics))[:5]
    
    def get_predicted_intent(self) -> Optional[str]:
        """Predict next likely intent based on patterns"""
        if not self.user_patterns:
            return None
        
        time_key = self._get_time_of_day()
        
        # Find most likely intent at this time
        best_intent = None
        best_score = 0
        
        for intent, data in self.user_patterns.items():
            if intent == 'commands':
                continue
            
            score = 0
            time_prefs = data.get('time_preferences', {})
            
            # Score based on time preference
            if time_key in time_prefs:
                score += time_prefs[time_key] * 2
            
            # Score based on frequency
            score += data.get('count', 0)
            
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return best_intent
    
    def get_frequent_commands(self, limit: int = 5) -> List[str]:
        """Get most frequently used commands"""
        commands = self.user_patterns.get('commands', {})
        
        sorted_commands = sorted(
            commands.items(),
            key=lambda x: x[1].get('count', 0),
            reverse=True
        )
        
        return [cmd for cmd, _ in sorted_commands[:limit]]
    
    def get_suggestions(self) -> List[str]:
        """Get contextual suggestions"""
        suggestions = []
        
        # Suggest frequent commands
        frequent = self.get_frequent_commands(3)
        if frequent:
            suggestions.append(f"Frequently used: {', '.join(frequent)}")
        
        # Suggest based on time
        time_suggestions = {
            'morning': ["Check weather", "Review tasks"],
            'afternoon': ["Check system status", "Take a break"],
            'evening': ["Set reminders", "Check tomorrow's tasks"],
            'night': ["Good night wishes", "Set alarm"]
        }
        
        tod = self._get_time_of_day()
        if tod in time_suggestions:
            suggestions.extend(time_suggestions[tod])
        
        return suggestions
    
    def analyze_situation(self) -> str:
        """Analyze current situation and return description"""
        context = self.get_context()
        
        parts = [
            f"Time: {context['time_of_day'].title()}",
            f"Day: {context['day_of_week']}",
        ]
        
        if context.get('user_mood') != 'neutral':
            parts.append(f"Mood: {context['user_mood']}")
        
        if context.get('recent_topics'):
            parts.append(f"Recent topics: {', '.join(context['recent_topics'])}")
        
        # Check for active patterns
        predicted = self.get_predicted_intent()
        if predicted:
            parts.append(f"Likely need: {predicted}")
        
        return " | ".join(parts)
    
    def get_contextual_response(self, base_response: str) -> str:
        """Enhance response with contextual awareness"""
        if not self.enabled:
            return base_response
        
        # Add contextual nuance based on time
        tod = self._get_time_of_day()
        
        time_prefixes = {
            'morning': "Good morning! ",
            'afternoon': "Good afternoon! ",
            'evening': "Good evening! ",
            'night': "Good evening. "
        }
        
        # Check if we should add time greeting
        if self.conversation_history:
            last_time = self.conversation_history[-1].get('time_of_day', '')
            if last_time != tod:
                # Time changed, add greeting
                return time_prefixes.get(tod, "") + base_response
        
        return base_response


# Global perception instance
_perception = None


def get_perception(config: Dict = None) -> PerceptionEngine:
    """Get or create perception engine"""
    global _perception
    if _perception is None:
        if config is None:
            for path in ['config.json', 'bosco_os/config.json']:
                if os.path.exists(path):
                    with open(path) as f:
                        config = json.load(f)
                        config = config.get('perception', {})
                        break
            if config is None:
                config = {}
        
        _perception = PerceptionEngine(config)
    return _perception


if __name__ == "__main__":
    print("Testing Perception Engine...")
    
    p = get_perception()
    
    # Add some test interactions
    p.add_interaction("What's the weather?", "The weather is sunny", "weather")
    p.add_interaction("Check my tasks", "You have 3 pending tasks", "tasks")
    p.add_command("screenshot", "Screenshot saved")
    
    print("Context:", p.get_context())
    print("Analysis:", p.analyze_situation())
    print("Suggestions:", p.get_suggestions())

