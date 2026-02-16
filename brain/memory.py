"""
Bosco Core - Memory System
Persistent storage for conversations, user preferences, and learned information
"""

import os
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pathlib import Path


class Memory:
    """Persistent memory for Bosco Core"""
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.conversations_file = self.storage_dir / "conversations.json"
        self.preferences_file = self.storage_dir / "preferences.json"
        self.learned_file = self.storage_dir / "learned.json"
        self.reminders_file = self.storage_dir / "reminders.json"
        
        # In-memory caches
        self._conversations: List[Dict] = []
        self._preferences: Dict = {}
        self._learned: Dict = {}
        self._reminders: List[Dict] = []
        
        # Load existing data
        self._load_all()
    
    def _load_all(self):
        """Load all stored data"""
        self._conversations = self._load_json(self.conversations_file, [])
        self._preferences = self._load_json(self.preferences_file, {})
        self._learned = self._load_json(self.learned_file, {})
        self._reminders = self._load_json(self.reminders_file, [])
    
    def _load_json(self, filepath: Path, default: Any) -> Any:
        """Load JSON file with fallback to default"""
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: Path, data: Any):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except IOError as e:
            print(f"Error saving to {filepath}: {e}")
    
    # ========== Conversation History ==========
    
    def add_conversation(self, user_message: str, bot_response: str, intent: str = ""):
        """Add a conversation exchange to history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "bot": bot_response,
            "intent": intent
        }
        self._conversations.append(entry)
        
        # Keep only last 1000 conversations
        if len(self._conversations) > 1000:
            self._conversations = self._conversations[-1000:]
        
        self._save_json(self.conversations_file, self._conversations)
    
    def get_conversation_history(self, limit: int = 20) -> List[Dict]:
        """Get recent conversation history"""
        return self._conversations[-limit:]
    
    def search_conversations(self, query: str) -> List[Dict]:
        """Search past conversations"""
        query_lower = query.lower()
        results = []
        for conv in self._conversations:
            if query_lower in conv.get("user", "").lower() or query_lower in conv.get("bot", "").lower():
                results.append(conv)
        return results
    
    def clear_conversations(self):
        """Clear conversation history"""
        self._conversations = []
        self._save_json(self.conversations_file, [])
    
    # ========== User Preferences ==========
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference value"""
        return self._preferences.get(key, default)
    
    def set_preference(self, key: str, value: Any):
        """Set a preference value"""
        self._preferences[key] = value
        self._save_json(self.preferences_file, self._preferences)
    
    def get_all_preferences(self) -> Dict:
        """Get all preferences"""
        return self._preferences.copy()
    
    def set_defaults(self):
        """Set default preferences if not already set"""
        defaults = {
            "name": "Sir",
            "voice_speed": 200,
            "voice_volume": 1.0,
            "wake_word": "hey bosco",
            "language": "en-US",
            "theme": "blue",
            "continuous_mode": False,
            "sound_effects": True,
            "notifications_enabled": True,
            "response_verbosity": "normal"  # short, normal, detailed
        }
        
        for key, value in defaults.items():
            if key not in self._preferences:
                self._preferences[key] = value
        
        self._save_json(self.preferences_file, self._preferences)
    
    # ========== Learned Information ==========
    
    def learn(self, key: str, value: Any):
        """Learn a piece of information"""
        self._learned[key] = {
            "value": value,
            "learned_at": datetime.now().isoformat()
        }
        self._save_json(self.learned_file, self._learned)
    
    def remember(self, key: str) -> Optional[Any]:
        """Recall learned information"""
        if key in self._learned:
            return self._learned[key].get("value")
        return None
    
    def forget(self, key: str):
        """Forget learned information"""
        if key in self._learned:
            del self._learned[key]
            self._save_json(self.learned_file, self._learned)
    
    def get_all_learned(self) -> Dict:
        """Get all learned information"""
        return {k: v["value"] for k, v in self._learned.items()}
    
    # ========== Reminders ==========
    
    def add_reminder(self, message: str, time: datetime, repeat: str = None) -> str:
        """Add a reminder"""
        reminder_id = f"rem_{datetime.now().timestamp()}"
        reminder = {
            "id": reminder_id,
            "message": message,
            "time": time.isoformat(),
            "repeat": repeat,  # None, "daily", "weekly", "monthly"
            "created_at": datetime.now().isoformat(),
            "completed": False
        }
        self._reminders.append(reminder)
        self._save_json(self.reminders_file, self._reminders)
        return reminder_id
    
    def get_reminders(self, pending_only: bool = True) -> List[Dict]:
        """Get reminders"""
        if pending_only:
            now = datetime.now()
            pending = []
            for rem in self._reminders:
                if not rem.get("completed"):
                    rem_time = datetime.fromisoformat(rem["time"])
                    if rem_time <= now:
                        pending.append(rem)
            return pending
        return self._reminders
    
    def complete_reminder(self, reminder_id: str):
        """Mark a reminder as completed"""
        for rem in self._reminders:
            if rem.get("id") == reminder_id:
                rem["completed"] = True
                rem["completed_at"] = datetime.now().isoformat()
        self._save_json(self.reminders_file, self._reminders)
    
    def delete_reminder(self, reminder_id: str):
        """Delete a reminder"""
        self._reminders = [r for r in self._reminders if r.get("id") != reminder_id]
        self._save_json(self.reminders_file, self._reminders)
    
    # ========== System Stats ==========
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        return {
            "total_conversations": len(self._conversations),
            "preferences_count": len(self._preferences),
            "learned_items": len(self._learned),
            "total_reminders": len(self._reminders),
            "pending_reminders": len(self.get_reminders(pending_only=True))
        }


# Global memory instance
_memory = Memory()


# Convenience functions
def get_memory() -> Memory:
    """Get the global memory instance"""
    return _memory


def add_conversation(user: str, bot: str, intent: str = ""):
    """Quick add to conversation history"""
    _memory.add_conversation(user, bot, intent)


def get_preference(key: str, default: Any = None) -> Any:
    """Quick get preference"""
    return _memory.get_preference(key, default)


def set_preference(key: str, value: Any):
    """Quick set preference"""
    _memory.set_preference(key, value)


def learn(key: str, value: Any):
    """Quick learn information"""
    _memory.learn(key, value)


def remember(key: str) -> Optional[Any]:
    """Quick recall information"""
    return _memory.remember(key)


if __name__ == "__main__":
    # Test memory system
    print("Testing Bosco Memory System...")
    
    # Set defaults
    _memory.set_defaults()
    
    # Add a conversation
    add_conversation("Hello Bosco", "Hello, sir. How may I assist you?", "greeting")
    
    # Learn something
    learn("favorite_app", "Chrome")
    
    # Get preference
    print(f"User name: {get_preference('name', 'Sir')}")
    
    # Get stats
    print(f"Stats: {_memory.get_stats()}")

