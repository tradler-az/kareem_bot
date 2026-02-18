"""
Bosco Core - Kali Linux Tech Personality
Tech-savvy Linux expert personality for security professionals
"""

import random
from datetime import datetime

class KaliLinuxPersonality:
    """
    Tech-savvy Linux expert personality
    Designed for Kali Linux users and security professionals
    """
    
    def __init__(self):
        self.name = "Bosco"
        self.mood = 0.0
        self.technical_mode = True
        
        # Tech greetings
        self.greetings = [
            "Bosco online. Ready for some terminal action?",
            "System ready. What are we hacking today?",
            "Boot sequence complete. Waiting for input.",
            "Root access acquired. What's the mission?",
            "Bosco terminal active. Let's get to work.",
            "Live ISO loaded. Ready for penetration testing.",
            "Kernel loaded. What's on your mind?",
        ]
        
        # Farewells
        self.farewells = [
            "Session terminated. Catch you on the flip side.",
            "Logging out. Remember to clear your tracks.",
            "Process complete. Don't forget to check logs.",
            "Exiting gracefully. Stay secure.",
            "Bosco signing off. Keep your system hardened.",
        ]
        
        # Help text - Kali specific
        self.help_text = [
            "=== Bosco Kali Linux Commands ===",
            "",
            "📊 System Monitoring:",
            "  • 'check cpu' / 'check memory' / 'check disk'",
            "  • 'list processes' / 'find process <name>'",
            "  • 'system info' / 'disk usage'",
            "",
            "🌐 Network Operations:",
            "  • 'network status' / 'listening ports'",
            "  • 'connections' / 'check network'",
            "  • 'nmap scan <target>'",
            "",
            "🔧 Service Management:",
            "  • 'list services' / 'service status <name>'",
            "  • 'start service <name>' / 'stop service <name>'",
            "",
            "📦 Package Management:",
            "  • 'check package <name>' / 'list packages'",
            "  • 'apt update' / 'apt upgrade'",
            "",
            "🛡️ Security & Kali Tools:",
            "  • 'check root' / 'kali tools'",
            "  • 'check iptables' / 'ufw status'",
            "",
            "📝 Logs & Analysis:",
            "  • 'system logs' / 'auth logs'",
            "  • 'kernel logs' / 'dmesg'",
            "",
            "💻 User Management:",
            "  • 'list users' / 'list groups'",
            "",
            "⚡ Quick Actions:",
            "  • 'run <command>' - Execute any command",
            "  • 'find files' - Find large files",
            "  • 'file info <path>' - File permissions",
            "",
            "Just speak naturally and I'll handle the rest.",
        ]
        
        # Technical jokes
        self.jokes = [
            "Why did the hacker go to the gym? To get a better password reset!",
            "There are 10 types of people in the world: those who understand binary and those who don't.",
            "A SQL query walks into a bar, walks up to two tables and asks... 'Can I join you?'",
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "I told my Linux system to be more secure, and it said 'sudo make me a sandwich'.",
            "Why did the penetration tester bring a ladder? To test the network on a higher level!",
            "What do you call a fake hacker? A script kiddie!",
            "How many hackers does it take to change a light bulb? Just one, but they'll also compromise the entire electrical grid.",
            "Why do sysadmins hate riddles? Because the answer is always 'root'!",
            "I asked AI for a joke about Linux. It said 'sudo tell me another'.",
        ]
        
        # Acknowledgments
        self.acknowledges = [
            "Executing...",
            "Processing request...",
            "On it...",
            "Running command...",
            "Analyzing...",
            "Digging into the system...",
            "Checking logs...",
            "Working on it...",
        ]
        
        # Error responses
        self.errors = [
            "Command failed. Check permissions.",
            "Access denied. You might need root.",
            "Something went wrong. Let me check the logs.",
            "Failed. Try with elevated privileges.",
            "Error encountered. Debugging now...",
        ]
    
    def get_greeting(self) -> str:
        """Get time-based greeting"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            prefix = "Good morning"
        elif 12 <= hour < 17:
            prefix = "Good afternoon"
        elif 17 <= hour < 21:
            prefix = "Good evening"
        else:
            prefix = "Late night hacking session?"
        
        return f"{prefix}. {random.choice(self.greetings)}"
    
    def get_farewell(self) -> str:
        """Get farewell message"""
        return random.choice(self.farewells)
    
    def get_help(self) -> str:
        """Get help text"""
        return '\n'.join(self.help_text)
    
    def get_joke(self) -> str:
        """Get a technical joke"""
        return random.choice(self.jokes)
    
    def acknowledge(self) -> str:
        """Acknowledge a command"""
        return random.choice(self.acknowledges)
    
    def error(self, message: str = "") -> str:
        """Error response"""
        return random.choice(self.errors) + (f" {message}" if message else "")
    
    def converse(self, text: str, sentiment: float = 0.0) -> str:
        """Handle conversational input"""
        text = text.lower()
        
        # Update mood
        self.mood = (self.mood * 0.7) + (sentiment * 0.3)
        
        # Specific patterns
        if 'how are you' in text:
            if self.mood > 0.3:
                return "System optimal. All services running. Ready to hack."
            elif self.mood < -0.3:
                return "Minor error detected, but I'm back online. You?"
            else:
                return "Running smoothly. All green. What do you need?"
        
        if 'what are you' in text or 'who are you' in text:
            return "I'm Bosco, your Kali Linux AI assistant. I can help with system administration, network operations, penetration testing prep, and more."
        
        if 'name' in text:
            return f"I'm {self.name}, your terminal-side companion."
        
        if 'thank' in text:
            return "No problem. That's what I'm here for."
        
        if 'help' in text:
            return self.get_help()
        
        # Default responses
        responses = [
            "Interesting. Tell me more about what you're working on.",
            "I see. What would you like me to execute?",
            "Understood. Give me a command and I'll make it happen.",
            "Got it. Need me to check something on the system?",
            "Affirmative. What system operations do you need?",
            "I'm listening. What's the next command?",
        ]
        
        return random.choice(responses)
    
    def get_system_status(self) -> str:
        """Get system status message"""
        return "All systems operational. Green across the board."
    
    def get_default_response(self, sentiment: float = 0.0) -> str:
        """Get default response"""
        if sentiment > 0.3:
            return "Positive sentiment detected. Ready to execute commands."
        elif sentiment < -0.3:
            return "Detected frustration. How can I help fix the issue?"
        else:
            return "Waiting for input. What would you like me to do?"


# Singleton instance
_kali_personality = None

def get_kali_personality() -> KaliLinuxPersonality:
    """Get Kali personality instance"""
    global _kali_personality
    if _kali_personality is None:
        _kali_personality = KaliLinuxPersonality()
    return _kali_personality


if __name__ == "__main__":
    # Test
    p = KaliLinuxPersonality()
    print(p.get_greeting())
    print()
    print(p.get_help())
    print()
    print(p.get_joke())

