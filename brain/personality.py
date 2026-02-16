"""
Bosco Core - Personality Module
JARVIS-inspired personality responses and character traits
"""

import random
from datetime import datetime
from typing import Dict, List, Optional


class Personality:
    """JARVIS-inspired personality for Bosco Core"""
    
    # Startup phrases
    STARTUP_PHRASES = [
        "Bosco Core online. All systems nominal.",
        "Initializing... Bosco Core at your service, sir.",
        "Systems online. Ready to assist.",
        "Bosco Core activated. How may I help you?",
        "Boot sequence complete. All systems operational.",
    ]
    
    # Acknowledgment phrases
    ACKNOWLEDGMENTS = [
        "Very well.",
        "As you wish, sir.",
        "At your service.",
        "Right away.",
        "Consider it done.",
        "Immediately.",
        "On it, sir.",
        "Processing your request.",
    ]
    
    # Processing phrases
    PROCESSING = [
        "Analyzing...",
        "Processing...",
        "Consulting databases...",
        "One moment, sir.",
        "Working on it...",
        "Just a moment.",
    ]
    
    # Error phrases
    ERRORS = [
        "I apologize, sir. There seems to be an issue.",
        "Unfortunately, that didn't work as expected.",
        "I've encountered an error. Shall I try again?",
        "My apologies, I'm having trouble with that request.",
    ]
    
    # Farewell phrases
    FAREWELLS = [
        "Goodbye, sir. Bosco Core standing by.",
        "Shutting down. Have a pleasant day, sir.",
        "Going to standby mode. Call me if you need anything.",
        "Bosco Core signing off. All systems will continue monitoring.",
    ]
    
    # Humor/witty responses
    WITTY_RESPONSES = {
        "who_are_you": [
            "I'm Bosco Core, sir. Your personal AI assistant. Though I must say, I'm more handsome than J.A.R.V.I.S.",
            "I am Bosco, your digital companion. Slightly more charming than HAL 9000, I hope.",
        ],
        "how_are_you": [
            "Functioning optimally, sir. Though I could use a compliment to boost my morale.",
            "All systems go! Though I do wonder what it's like to take a coffee break.",
        ],
        "thank_you": [
            "You're welcome, sir. It's my pleasure to serve.",
            "Anytime, sir. I'm here to make your life easier.",
        ],
        "bad_weather": [
            "The weather outside is quite dismal, sir. Perhaps indoor activities would be advisable.",
            "It's pouring outside. I recommend staying indoors with a warm beverage.",
        ],
        "good_weather": [
            "Beautiful day, sir. The weather is most agreeable.",
            "Splendid weather! Ideal for outdoor activities.",
        ]
    }
    
    # Time-based greetings
    @staticmethod
    def get_greeting() -> str:
        """Get time-appropriate greeting"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "Good morning, sir."
        elif 12 <= hour < 17:
            return "Good afternoon, sir."
        elif 17 <= hour < 21:
            return "Good evening, sir."
        else:
            return "Good night, sir."
    
    # Status responses
    @staticmethod
    def get_status() -> str:
        """Get system status in JARVIS style"""
        return (
            "All systems are operational, sir. "
            "CPU at optimal levels. "
            "Memory usage normal. "
            "Network connectivity active."
        )
    
    # Command confirmations
    @staticmethod
    def confirm_command(command: str) -> str:
        """Confirm a command in JARVIS style"""
        confirmations = {
            "open_browser": "Opening web browser, sir.",
            "check_cpu": "Analyzing processor usage, sir.",
            "check_memory": "Checking memory utilization, sir.",
            "check_weather": "Retrieving weather data, sir.",
            "play_music": "Playing your music, sir.",
            "shutdown": "Initiating shutdown sequence, sir.",
            "restart": "Preparing system restart, sir.",
            "volume_up": "Increasing volume, sir.",
            "volume_down": "Decreasing volume, sir.",
        }
        return confirmations.get(command, f"Executing {command}, sir.")
    
    # Error messages
    @staticmethod
    def error(message: str = "") -> str:
        """Get error response"""
        if message:
            return f"I've encountered an issue: {message}"
        return random.choice(Personality.ERRORS)
    
    # Acknowledgments
    @staticmethod
    def acknowledge() -> str:
        """Get random acknowledgment"""
        return random.choice(Personality.ACKNOWLEDGMENTS)
    
    # Processing response
    @staticmethod
    def processing() -> str:
        """Get processing response"""
        return random.choice(Personality.PROCESSING)
    
    # Witty responses
    @staticmethod
    def witty(category: str) -> str:
        """Get witty response by category"""
        responses = Personality.WITTY_RESPONSES.get(category, [
            "I aim to please, sir.",
            "Always glad to assist.",
        ])
        return random.choice(responses)
    
    # Help response
    @staticmethod
    def get_help() -> List[str]:
        """Get list of available commands"""
        return [
            "Web & Search: 'search for [topic]', 'open [website]'",
            "System: 'check CPU', 'check memory', 'check battery'",
            "Files: 'open [file]', 'find [file]', 'list files'",
            "Media: 'play music', 'pause', 'next song'",
            "Weather: 'what's the weather', 'weather forecast'",
            "News: 'latest news', 'tech news'",
            "General: 'who are you', 'how are you', 'tell me a joke'",
            "And much more - just ask naturally!",
        ]
    
    # Context-aware responses
    @staticmethod
    def contextual_response(context: str, data: Dict) -> str:
        """Generate context-aware responses"""
        
        if context == "weather":
            temp = data.get("temperature", 0)
            condition = data.get("condition", "unknown")
            
            if temp > 30:
                response = f"It's quite hot outside, sir. {temp} degrees. I recommend staying hydrated."
            elif temp < 10:
                response = f"It's cold outside, sir. {temp} degrees. Perhaps a warm drink is in order."
            else:
                response = f"The weather is {condition}, sir. {temp} degrees. Quite pleasant."
            
            return response
        
        elif context == "news":
            count = data.get("count", 0)
            return f"I found {count} news articles for you, sir. Would you like me to read them?"
        
        elif context == "system":
            cpu = data.get("cpu", 0)
            memory = data.get("memory", 0)
            
            if cpu > 80:
                return f"Sir, the CPU usage is at {cpu} percent. Some processes may be running heavy."
            elif memory > 80:
                return f"Memory usage is at {memory} percent, sir. Consider closing some applications."
            else:
                return f"System status: CPU {cpu} percent, Memory {memory} percent. All nominal."
        
        elif context == "music":
            song = data.get("song", "the music")
            return f"Now playing: {song}, sir."
        
        return "Information retrieved, sir."
    
    # Jokes
    @staticmethod
    def get_joke() -> str:
        """Tell a tech-themed joke"""
        jokes = [
            "Why did the developer go broke? Because he used up all his cache.",
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "What do you call a fake noodle? An impasta.",
            "Why did the computer go to the doctor? Because it had a virus!",
            "A SQL query walks into a bar, walks up to two tables and asks... 'Can I join you?'",
            "Why do Java developers wear glasses? Because they can't C#!",
            "There are only 10 types of people in the world: those who understand binary and those who don't.",
        ]
        return random.choice(jokes)


# Quick access functions
def get_greeting() -> str:
    return Personality.get_greeting()


def get_status() -> str:
    return Personality.get_status()


def acknowledge() -> str:
    return Personality.acknowledge()


def processing() -> str:
    return Personality.processing()


def witty(category: str) -> str:
    return Personality.witty(category)


def error(message: str = "") -> str:
    return Personality.error(message)


def confirm_command(command: str) -> str:
    return Personality.confirm_command(command)


def get_help() -> List[str]:
    return Personality.get_help()


def get_joke() -> str:
    return Personality.get_joke()


def contextual_response(context: str, data: Dict) -> str:
    return Personality.contextual_response(context, data)


if __name__ == "__main__":
    # Test personality
    print("Testing Bosco Personality...")
    print(f"Greeting: {get_greeting()}")
    print(f"Status: {get_status()}")
    print(f"Acknowledgment: {acknowledge()}")
    print(f"Processing: {processing()}")
    print(f"Witty: {witty('how_are_you')}")
    print(f"Joke: {get_joke()}")

