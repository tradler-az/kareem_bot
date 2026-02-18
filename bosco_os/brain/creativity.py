"""
Bosco Core - Creativity Module
Creative response generation, varied responses, and imaginative capabilities
"""

import os
import json
import random
from typing import Dict, List, Optional, Any
from datetime import datetime


class CreativityEngine:
    """Creativity engine for varied and imaginative responses"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 500)
        self.response_variety = self.config.get('response_variety', True)
        
        # Creative response templates
        self._init_creativity_templates()
        
        # Response history for variety
        self.recent_responses: List[str] = []
        self.max_history = 10
    
    def _init_creativity_templates(self):
        """Initialize creative response templates"""
        self.greeting_variants = [
            "Hello there!",
            "Greetings!",
            "Hey! Good to see you.",
            "Welcome back!",
            "Hi! How can I help you today?",
            "Well, hello!",
            "Greetings, human!",
            "Hey there!",
        ]
        
        self.acknowledgment_variants = [
            "Got it!",
            "On it!",
            "Consider it done.",
            "Right away!",
            "As you wish.",
            "I'll handle that.",
            "Working on it now.",
            "Done and done.",
        ]
        
        self.processing_variants = [
            "Let me think...",
            "Processing that for you...",
            "One moment...",
            "Consulting my neural networks...",
            "Working through the details...",
            "Analyzing...",
            "Just a sec...",
            "Let me check that...",
        ]
        
        self.confusion_variants = [
            "I'm not quite sure I understand. Could you rephrase that?",
            "Hmm, that's interesting. Can you elaborate?",
            "I'm not following. What did you mean?",
            "Could you try that again?",
            "I'm a bit confused. Mind explaining?",
        ]
        
        self.farewell_variants = [
            "Goodbye! Take care!",
            "See you later!",
            "Bye! Hope to help you again soon.",
            "Farewell! Have a great day!",
            "Take care! I'm always here if you need me.",
        ]
        
        self.error_variants = [
            "Oops! Something went wrong.",
            "That's a tricky one. Let me try again.",
            "I ran into an issue there.",
            "Apologies, but I couldn't complete that.",
            "Hmm, that didn't work as expected.",
        ]
        
        self.jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did the developer go broke? Because he used up all his cache!",
            "What do you call a fake noodle? An impasta!",
            "Why did the computer go to the doctor? Because it had a virus!",
            "A SQL query walks into a bar, walks up to two tables and asks... 'Can I join you?'",
            "Why do Java developers wear glasses? Because they can't C#!",
            "There are only 10 types of people in the world: those who understand binary and those who don't.",
            "Why was the JavaScript developer sad? Because he didn't Node how to Express himself!",
            "What do you call a dog that does magic? A Labracadabrador!",
            "Why do Python programmers have low self-esteem? Because they can't C!",
        ]
        
        self.fun_facts = [
            "The first computer bug was an actual moth found in the Mark II computer in 1947.",
            "The word 'robot' comes from the Czech word 'robota' meaning 'forced labor'.",
            "The first computer program was written by Ada Lovelace in 1843.",
            "The QWERTY keyboard was designed to slow down typists to prevent jamming.",
            "The first email was sent by Ray Tomlinson to himself in 1971.",
            "The term 'debugging' comes from removing an actual moth from a computer in 1947.",
            "The average computer user blinks 7 times a minute, less than half the normal rate of 20.",
        ]
        
        self.encouragement_messages = [
            "You've got this!",
            "Keep going, you're doing great!",
            "Every step counts!",
            "I'm here to help you succeed!",
            "You've made progress - keep it up!",
        ]
        
        self.metaphors = {
            'knowledge': [
                "knowledge is a treasure",
                "information is power",
                "learning is a journey",
            ],
            'time': [
                "time is gold",
                "time flies",
                "every second counts",
            ],
            'help': [
                "I'm your digital assistant",
                "think of me as your helper",
                "I'm here to make things easier",
            ]
        }
    
    def get_greeting(self, base_greeting: str = None) -> str:
        """Get a varied greeting"""
        if not self.enabled or not self.response_variety:
            return base_greeting or "Hello!"
        
        # Avoid repeating recent responses
        available = [g for g in self.greeting_variants if g not in self.recent_responses]
        if not available:
            available = self.greeting_variants
        
        greeting = random.choice(available)
        self._add_to_history(greeting)
        
        # Add time-specific variation
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting = f"Good morning! {greeting}"
        elif 17 <= hour < 21:
            greeting = f"Good evening! {greeting}"
        
        return greeting
    
    def get_acknowledgment(self) -> str:
        """Get a varied acknowledgment"""
        if not self.enabled or not self.response_variety:
            return "Got it!"
        
        available = [a for a in self.acknowledgment_variants if a not in self.recent_responses]
        if not available:
            available = self.acknowledgment_variants
        
        ack = random.choice(available)
        self._add_to_history(ack)
        return ack
    
    def get_processing_message(self) -> str:
        """Get a varied processing message"""
        if not self.enabled or not self.response_variety:
            return "Processing..."
        
        available = [p for p in self.processing_variants if p not in self.recent_responses]
        if not available:
            available = self.processing_variants
        
        msg = random.choice(available)
        self._add_to_history(msg)
        return msg
    
    def get_confusion_response(self) -> str:
        """Get a varied confusion response"""
        if not self.enabled or not self.response_variety:
            return "I'm not sure I understand."
        
        return random.choice(self.confusion_variants)
    
    def get_farewell(self) -> str:
        """Get a varied farewell"""
        if not self.enabled or not self.response_variety:
            return "Goodbye!"
        
        return random.choice(self.farewell_variants)
    
    def get_error_response(self, error: str = None) -> str:
        """Get a varied error response"""
        if not self.enabled or not self.response_variety:
            return f"Error: {error}" if error else "An error occurred."
        
        response = random.choice(self.error_variants)
        if error:
            response += f" ({error})"
        return response
    
    def get_joke(self) -> str:
        """Get a random joke"""
        if not self.enabled:
            return "Jokes are disabled."
        return random.choice(self.jokes)
    
    def get_fun_fact(self) -> str:
        """Get a random fun fact"""
        if not self.enabled:
            return "Fun facts are disabled."
        return random.choice(self.fun_facts)
    
    def get_encouragement(self) -> str:
        """Get an encouragement message"""
        return random.choice(self.encouragement_messages)
    
    def enhance_response(self, base_response: str, context: str = None) -> str:
        """Enhance a response with creative elements"""
        if not self.enabled or not self.response_variety:
            return base_response
        
        # Add variety to responses
        variations = []
        
        # Occasionally add an encouraging comment
        if random.random() < 0.1:
            variations.append(random.choice(self.encouragement_messages))
        
        # Sometimes add a metaphor
        if context and random.random() < 0.15:
            if context in self.metaphors:
                metaphor = random.choice(self.metaphors[context])
                variations.append(f"Remember: {metaphor}.")
        
        if variations:
            return base_response + " " + " ".join(variations)
        
        return base_response
    
    def creative_story_start(self, topic: str) -> str:
        """Generate a creative story start"""
        if not self.enabled:
            return f"Let me tell you about {topic}."
        
        story_starters = [
            f"Imagine this: {topic}...",
            f"Here's an interesting perspective on {topic}...",
            f"Let me share something fascinating about {topic}...",
            f"Have you ever thought about {topic} from a different angle?",
        ]
        
        return random.choice(story_starters)
    
    def _add_to_history(self, response: str):
        """Add response to history for variety tracking"""
        self.recent_responses.append(response)
        if len(self.recent_responses) > self.max_history:
            self.recent_responses.pop(0)
    
    def set_temperature(self, temperature: float):
        """Set creativity temperature (0.0 to 1.0)"""
        self.temperature = max(0.0, min(1.0, temperature))
    
    def enable_variety(self, enabled: bool):
        """Enable/disable response variety"""
        self.response_variety = enabled
    
    def get_creativity_stats(self) -> Dict[str, Any]:
        """Get creativity engine statistics"""
        return {
            "enabled": self.enabled,
            "temperature": self.temperature,
            "response_variety": self.response_variety,
            "response_history_size": len(self.recent_responses),
            "templates_available": {
                "greetings": len(self.greeting_variants),
                "acknowledgments": len(self.acknowledgment_variants),
                "processing": len(self.processing_variants),
                "jokes": len(self.jokes),
                "fun_facts": len(self.fun_facts),
            }
        }


# Global creativity instance
_creativity = None


def get_creativity(config: Dict = None) -> CreativityEngine:
    """Get or create creativity engine"""
    global _creativity
    if _creativity is None:
        if config is None:
            for path in ['config.json', 'bosco_os/config.json']:
                if os.path.exists(path):
                    with open(path) as f:
                        config = json.load(f)
                        config = config.get('creativity', {})
                        break
            if config is None:
                config = {}
        
        _creativity = CreativityEngine(config)
    return _creativity


# Convenience functions
def get_greeting() -> str:
    """Get varied greeting"""
    return get_creativity().get_greeting()


def get_joke() -> str:
    """Get random joke"""
    return get_creativity().get_joke()


def get_fun_fact() -> str:
    """Get random fun fact"""
    return get_creativity().get_fun_fact()


def enhance_response(response: str, context: str = None) -> str:
    """Enhance response with creativity"""
    return get_creativity().enhance_response(response, context)


if __name__ == "__main__":
    print("Testing Creativity Engine...")
    
    c = get_creativity()
    
    print("Greetings:", c.get_greeting())
    print("Acknowledgment:", c.get_acknowledgment())
    print("Processing:", c.get_processing_message())
    print("Joke:", c.get_joke())
    print("Fun fact:", c.get_fun_fact())
    print("Farewell:", c.get_farewell())
    print("Enhanced:", c.enhance_response("Task completed!", "help"))
