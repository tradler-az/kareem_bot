"""
Bosco Core - Reminders Capability
Set and manage reminders
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path


class Reminders:
    """Reminder management"""
    
    def __init__(self, storage_path: str = "data/reminders.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(exist_ok=True)
        self.reminders = self._load()
    
    def _load(self) -> List[Dict]:
        """Load reminders from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save(self):
        """Save reminders to storage"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.reminders, f, indent=2, default=str)
        except:
            pass
    
    def add_reminder(self, message: str, minutes: int = 0, hours: int = 0, days: int = 0) -> str:
        """Add a reminder"""
        reminder_time = datetime.now() + timedelta(minutes=minutes, hours=hours, days=days)
        
        reminder = {
            "id": f"rem_{datetime.now().timestamp()}",
            "message": message,
            "time": reminder_time.isoformat(),
            "created": datetime.now().isoformat(),
            "completed": False
        }
        
        self.reminders.append(reminder)
        self._save()
        
        return reminder["id"]
    
    def get_pending(self) -> List[Dict]:
        """Get pending reminders"""
        now = datetime.now()
        pending = []
        
        for rem in self.reminders:
            if rem.get("completed"):
                continue
            
            rem_time = datetime.fromisoformat(rem["time"])
            if rem_time <= now:
                pending.append(rem)
        
        return pending
    
    def complete(self, reminder_id: str) -> bool:
        """Mark reminder as completed"""
        for rem in self.reminders:
            if rem.get("id") == reminder_id:
                rem["completed"] = True
                rem["completed_at"] = datetime.now().isoformat()
                self._save()
                return True
        return False
    
    def delete(self, reminder_id: str) -> bool:
        """Delete a reminder"""
        self.reminders = [r for r in self.reminders if r.get("id") != reminder_id]
        self._save()
        return True
    
    def list_all(self) -> List[Dict]:
        """List all reminders"""
        return self.reminders
    
    def format_response(self, reminder: Dict) -> str:
        """Format reminder as speech"""
        return f"Reminder: {reminder.get('message', 'No message')}"


_reminders = Reminders()


def add_reminder(message: str, minutes: int = 0, hours: int = 0, days: int = 0) -> str:
    return _reminders.add_reminder(message, minutes, hours, days)


def get_pending() -> List[Dict]:
    return _reminders.get_pending()


def complete_reminder(reminder_id: str) -> bool:
    return _reminders.complete(reminder_id)


def delete_reminder(reminder_id: str) -> bool:
    return _reminders.delete(reminder_id)


if __name__ == "__main__":
    print("Testing Reminders...")
    rem_id = add_reminder("Test reminder", minutes=5)
    print(f"Added: {rem_id}")
    print(f"Pending: {get_pending()}")

