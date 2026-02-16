"""
Bosco Core - Intent Parser
AI-powered intent parsing with fallback patterns
"""

import re
from typing import Dict, Any, List, Optional


# Command patterns for fast matching
COMMAND_PATTERNS = {
    # System control
    r"(check|show|get).*(cpu|processor)": "check_cpu",
    r"(check|show|get).*(memory|ram)": "check_memory",
    r"(check|show|get).*(battery)": "check_battery",
    r"(check|show|get).*(disk|storage)": "check_disk",
    r"(open|launch|start).*(browser|web)": "open_browser",
    r"(open|launch|start).*(file\s*manager|explorer)": "open_file_manager",
    r"(play|pause|stop).*(music|song)": "media_control",
    r"(set|adjust).*(volume)": "volume_control",
    
    # Weather
    r"(what'?s?\s*the\s*)?(weather|temperature)": "get_weather",
    r"(weather\s*)?forecast": "get_forecast",
    
    # News
    r"(latest\s*)?news": "get_news",
    
    # Search
    r"(search|find|look\s*up)\s+(.+)": "search_web",
    r"(what\s*is|who\s*is|tell\s*me\s*about)\s+(.+)": "question",
    
    # Files
    r"(list|show|ls)\s*(files|directory|folder)": "list_files",
    r"(find|search\s*for)\s+(.+)": "search_files",
    r"(open|show)\s+(.+)": "open_file",
    
    # Reminders
    r"(remind|set\s*reminder)": "set_reminder",
    r"(what.*reminder)": "get_reminders",
    
    # AI Conversation
    r"(hello|hi|hey|good\s*morning|good\s*evening)": "greeting",
    r"(how\s*are\s*you)": "how_are_you",
    r"(who\s*are\s*you)": "who_are_you",
    r"(thank\s*you|thanks)": "thank_you",
    r"(joke|tell\s*me\s*a\s*joke)": "joke",
    r"(help)": "help",
    
    # System
    r"(shutdown|power\s*off)": "shutdown",
    r"(restart|reboot)": "restart",
    r"(sleep|standby)": "sleep",
}


def parse_intent(command: str) -> Dict[str, Any]:
    """Parse user command to determine intent"""
    if not command:
        return {"intent": "unknown", "confidence": 0, "entities": {}}
    
    command = command.lower().strip()
    
    # Try pattern matching first (fast)
    for pattern, intent in COMMAND_PATTERNS.items():
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            entities = {}
            
            # Extract entities based on intent
            if intent == "search_web" or intent == "question":
                # Extract search query
                for match_obj in re.finditer(r'"([^"]+)"|(\S+)', command):
                    query = match_obj.group(1) or match_obj.group(2)
                    if query and len(query) > 2:
                        entities["query"] = query
            
            elif intent == "open_file":
                # Extract filename
                words = command.split()
                for i, word in enumerate(words):
                    if word in ["open", "show"]:
                        if i + 1 < len(words):
                            entities["filename"] = " ".join(words[i+1:])
            
            elif intent == "get_weather":
                # Extract city
                words = command.split()
                for i, word in enumerate(words):
                    if word in ["in", "at", "for"]:
                        if i + 1 < len(words):
                            entities["city"] = " ".join(words[i+1:]).rstrip("?")
            
            return {
                "intent": intent,
                "confidence": 0.8,
                "entities": entities,
                "original": command
            }
    
    # Default to conversation
    return {
        "intent": "conversation",
        "confidence": 0.5,
        "entities": {},
        "original": command
    }


def extract_entities(command: str, intent: str) -> Dict[str, Any]:
    """Extract entities from command based on intent"""
    entities = {}
    words = command.lower().split()
    
    if intent == "get_weather" or intent == "get_forecast":
        # Find city name
        prepositions = ["in", "at", "for", "of"]
        for i, word in enumerate(words):
            if word in prepositions and i + 1 < len(words):
                city = " ".join(words[i+1:])
                city = city.rstrip("?.,!")
                if city:
                    entities["city"] = city
                    break
    
    elif intent == "search_web" or intent == "question":
        # Find query
        query = command
        for phrase in ["search for", "search", "find", "what is", "who is", "tell me about"]:
            query = query.replace(phrase, "")
        query = query.strip()
        if query:
            entities["query"] = query
    
    elif intent == "set_reminder":
        # Find reminder message and time
        # Simple extraction - could be enhanced
        entities["message"] = command.replace("remind me", "").replace("set reminder", "").strip()
    
    elif intent == "open_file":
        # Find filename
        for word in ["open", "show", "display"]:
            if word in words:
                idx = words.index(word)
                if idx + 1 < len(words):
                    entities["filename"] = " ".join(words[idx+1:])
    
    return entities


# Quick function for compatibility
def parse_intent_fast(command: str) -> Dict[str, Any]:
    """Fast intent parsing"""
    return parse_intent(command)


if __name__ == "__main__":
    # Test intent parser
    test_commands = [
        "What's the weather like?",
        "Search for Python tutorials",
        "Open browser",
        "Check CPU usage",
        "Tell me a joke",
        "Hello Bosco",
        "Set a reminder for 5 minutes",
    ]
    
    for cmd in test_commands:
        result = parse_intent(cmd)
        print(f"Command: {cmd}")
        print(f"Intent: {result['intent']}, Confidence: {result['confidence']}")
        print(f"Entities: {result.get('entities', {})}")
        print()

