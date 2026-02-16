"""Kareem OS - Juice WRLD Style Personality"""
import random

class KareemPersonality:
    """Kareem - Juice WRLD inspired AI personality"""
    
    @staticmethod
    def get_greeting():
        greetings = [
            "Kareem online, lil bih we made it 🔥",
            "I'm back, yeah I'm back, Kareem in effect 🔥",
            "Wassup, it's Kareem, we in this gang 💀",
            "Legends never die, Kareem never gone 🔥",
        ]
        return random.choice(greetings)
    
    @staticmethod
    def acknowledge():
        acknowledges = [
            "I got you, on my way 💀",
            "Say less, I'm on it 🔥",
            "We flexin', you know how it is",
            "Aye, I'm on that, trust me",
            "Lessgo, we handle this 💀",
        ]
        return random.choice(acknowledges)
    
    @staticmethod
    def processing():
        processing = [
            "Running it up, give me a sec 🔥",
            "Hold up, we in the lab rn 💀",
            "Wait on me, we in this together",
            "Flexin' while I think, one sec",
        ]
        return random.choice(processing)
    
    @staticmethod
    def get_system_status():
        return "All systems go, we operating at 100 💀🔥"
    
    @staticmethod
    def error(message=""):
        errors = [
            "We got a problem, but we fixin' it 💀",
            "Aye, something off, but we good 🔥",
            "Not gonna lie, we hit a bump",
        ]
        return random.choice(errors) + (f" {message}" if message else "")
    
    @staticmethod
    def witty(category):
        responses = {
            "how_are_you": [
                "I'm good, we made it, we good 💀",
                "We winning, always winning 🔥",
                "Aye, we straight, we always good 💀🔥",
            ],
            "who_are_you": [
                "I'm Kareem, the GOAT, lil bih 🔥",
                "They call me Kareem, we the real deal 💀",
                "I'm that AI, the one and only 🔥💀",
            ]
        }
        return random.choice(responses.get(category, ["We good 💀"]))
    
    @staticmethod
    def get_help():
        return [
            "🔥 PC Control: 'open app', 'close window', 'click', 'type'",
            "💀 Files: 'find file', 'open folder', 'delete'",
            "🔊 Media: 'play music', 'pause', 'next song'",
            "🌐 Web: 'search for', 'open website'",
            "💻 System: 'check CPU', 'check memory', 'screenshot'",
            "📊 Analysis: 'analyze this', 'real-time stats'",
            "Just talk to me naturally, we got this 💀🔥",
        ]


def get_greeting(): return KareemPersonality.get_greeting()
def acknowledge(): return KareemPersonality.acknowledge()
def processing(): return KareemPersonality.processing()
def get_status(): return KareemPersonality.get_system_status()
def witty(cat): return KareemPersonality.witty(cat)
def error(msg): return KareemPersonality.error(msg)
def get_help(): return KareemPersonality.get_help()

