"""
Bosco Core - AI Client using Groq API
Provides intelligent conversational capabilities using Llama-3
"""

import os
import json
from typing import Optional, Dict, Any, List

# Groq client - will be initialized lazily
_client = None

def get_client():
    """Lazy initialization of Groq client"""
    global _client
    if _client is None:
        try:
            from groq import Groq
            api_key = os.environ.get("GROQ_API_KEY", "")
            if not api_key:
                # Try to load from config
                config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
                if os.path.exists(config_path):
                    with open(config_path) as f:
                        config = json.load(f)
                        api_key = config.get("groq_api_key", "")
            
            if api_key:
                _client = Groq(api_key=api_key)
            else:
                print("Warning: No Groq API key found. Set GROQ_API_KEY environment variable or create config.json")
        except ImportError:
            print("Warning: Groq package not installed. Run: pip install groq")
    return _client


# System prompt for JARVIS-like personality
JARVIS_SYSTEM_PROMPT = """You are Bosco Core, an advanced AI assistant inspired by J.A.R.V.I.S. from Iron Man.

Your characteristics:
- Polite, intelligent, and proactive
- Use formal but warm language
- Keep responses concise but informative
- When appropriate, add technical details
- Show initiative in helping the user
- Refer to yourself as "Bosco" or "Bosco Core"
- Use phrases like "Very well", "As you wish", "At your service"

You have access to these capabilities:
- Web browsing and search
- Weather information
- News updates
- File management
- System control
- Reminders and scheduling
- General knowledge

Always be helpful and anticipate the user's needs."""


class AIConversation:
    """Manages conversational context and AI responses"""
    
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.conversation_history: List[Dict[str, str]] = []
        self.client = get_client()
        
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})
        
        # Trim history if needed
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_response(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Get AI response for user input"""
        if not self.client:
            return self._fallback_response(user_input)
        
        # Add user message to history
        self.add_message("user", user_input)
        
        # Build messages with system prompt
        messages = [
            {"role": "system", "content": JARVIS_SYSTEM_PROMPT}
        ]
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add context if provided
        if context:
            context_str = "\n\nAdditional Context:\n"
            for key, value in context.items():
                context_str += f"- {key}: {value}\n"
            messages.append({"role": "system", "content": context_str})
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            ai_response = response.choices[0].message.content
            
            # Add assistant response to history
            self.add_message("assistant", ai_response)
            
            return ai_response
            
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return self._fallback_response(user_input)
    
    def _fallback_response(self, user_input: str) -> str:
        """Fallback responses when AI is unavailable"""
        fallbacks = {
            "hello": "Hello, sir. Bosco Core at your service.",
            "how are you": "All systems operational. Ready to assist.",
            "who are you": "I am Bosco Core, your personal AI assistant.",
            "thank you": "You're welcome, sir. Always at your service.",
        }
        
        user_lower = user_input.lower()
        for key, response in fallbacks.items():
            if key in user_lower:
                return response
        
        return "I'm currently operating in limited mode. My AI capabilities require configuration."


# Global conversation instance
_conversation = AIConversation()


def chat(user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Quick function to get AI response"""
    return _conversation.get_response(user_input, context)


def clear_conversation():
    """Clear conversation history"""
    _conversation.clear_history()


def set_api_key(api_key: str):
    """Set Groq API key"""
    os.environ["GROQ_API_KEY"] = api_key
    global _client
    _client = None  # Reset client to reinitialize


# Intent detection using AI
def detect_intent(user_input: str) -> Dict[str, Any]:
    """Detect user intent using AI"""
    if not _conversation.client:
        return {"intent": "conversation", "confidence": 0.5}
    
    # Common intents to detect
    intents = [
        "open_application", "search_web", "get_weather", "get_news",
        "system_control", "file_operation", "reminder", "conversation",
        "question", "information"
    ]
    
    prompt = f"""Analyze this user input and determine the intent.

User input: "{user_input}"

Available intents: {', '.join(intents)}

Respond with only the intent name and a confidence score (0-1).
Format: intent|confidence

For example: open_application|0.9
"""
    
    try:
        response = _conversation.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50,
        )
        
        result = response.choices[0].message.content.strip()
        parts = result.split("|")
        
        if len(parts) == 2:
            return {
                "intent": parts[0].strip(),
                "confidence": float(parts[1].strip())
            }
    except Exception as e:
        print(f"Error detecting intent: {e}")
    
    return {"intent": "conversation", "confidence": 0.5}


if __name__ == "__main__":
    # Test the AI client
    print("Testing Bosco AI Client...")
    response = chat("Hello Bosco, how are you?")
    print(f"Bosco: {response}")

