"""
Bosco OS - Event Bus Module
Pub/Sub event system for inter-component communication
"""

import asyncio
from typing import Callable, Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import threading


class EventPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3


@dataclass
class Event:
    """Event data structure"""
    type: str
    data: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"
    priority: EventPriority = EventPriority.NORMAL


class EventBus:
    """Central event bus for Bosco OS"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000
        self._lock = threading.RLock()
        self._async_subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable, priority: EventPriority = EventPriority.NORMAL):
        """Subscribe to an event type"""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append({
                'callback': callback,
                'priority': priority
            })
            # Sort by priority (highest first)
            self._subscribers[event_type].sort(
                key=lambda x: x['priority'].value, 
                reverse=True
            )
    
    def subscribe_async(self, event_type: str, callback: Callable):
        """Subscribe to an event type for async handling"""
        with self._lock:
            if event_type not in self._async_subscribers:
                self._async_subscribers[event_type] = []
            self._async_subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type"""
        with self._lock:
            if event_type in self._subscribers:
                self._subscribers[event_type] = [
                    s for s in self._subscribers[event_type]
                    if s['callback'] != callback
                ]
    
    def publish(self, event: Event):
        """Publish an event to all subscribers"""
        with self._lock:
            # Add to history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history = self._event_history[-self._max_history:]
            
            # Notify synchronous subscribers
            if event.type in self._subscribers:
                for subscriber in self._subscribers[event.type]:
                    try:
                        subscriber['callback'](event)
                    except Exception as e:
                        print(f"Error in event handler: {e}")
            
            # Schedule async subscribers
            if event.type in self._async_subscribers:
                for callback in self._async_subscribers[event.type]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            asyncio.create_task(callback(event))
                        else:
                            callback(event)
                    except Exception as e:
                        print(f"Error in async event handler: {e}")
    
    def publish_sync(self, event_type: str, data: Any = None, source: str = "unknown"):
        """Publish a synchronous event"""
        event = Event(type=event_type, data=data, source=source)
        self.publish(event)
    
    async def publish_async(self, event_type: str, data: Any = None, source: str = "unknown"):
        """Publish an asynchronous event"""
        event = Event(type=event_type, data=data, source=source)
        self.publish(event)
    
    def get_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Event]:
        """Get event history"""
        with self._lock:
            if event_type:
                events = [e for e in self._event_history if e.type == event_type]
            else:
                events = self._event_history
            return events[-limit:]
    
    def clear_history(self):
        """Clear event history"""
        with self._lock:
            self._event_history = []
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for an event type"""
        with self._lock:
            return len(self._subscribers.get(event_type, []))


# Event types
class Events:
    """Event type constants"""
    # Voice events
    VOICE_WAKE = "voice.wake"
    VOICE_LISTENING = "voice.listening"
    VOICE_COMMAND = "voice.command"
    VOICE_RESPONSE = "voice.response"
    
    # Brain events
    BRAIN_INTENT = "brain.intent"
    BRAIN_REASONING = "brain.reasoning"
    BRAIN_RESPONSE = "brain.response"
    
    # Capability events
    CAPABILITY_EXECUTED = "capability.executed"
    CAPABILITY_SUCCESS = "capability.success"
    CAPABILITY_ERROR = "capability.error"
    
    # System events
    SYSTEM_START = "system.start"
    SYSTEM_STOP = "system.stop"
    SYSTEM_STATUS = "system.status"
    
    # Security events
    SECURITY_AUTH = "security.auth"
    SECURITY_POLICY = "security.policy"
    SECURITY_AUDIT = "security.audit"
    
    # Network events (for Kali tools)
    NETWORK_SCAN = "network.scan"
    NETWORK_ATTACK = "network.attack"
    
    # Automation events
    AUTOMATION_START = "automation.start"
    AUTOMATION_COMPLETE = "automation.complete"


# Global event bus instance
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get global event bus instance"""
    return _event_bus


def subscribe(event_type: str, callback: Callable, priority: EventPriority = EventPriority.NORMAL):
    """Quick subscribe function"""
    _event_bus.subscribe(event_type, callback, priority)


def publish(event: Event):
    """Quick publish function"""
    _event_bus.publish(event)


def publish_sync(event_type: str, data: Any = None, source: str = "unknown"):
    """Quick publish sync function"""
    _event_bus.publish_sync(event_type, data, source)


# Event handler decorator
def on_event(event_type: str, priority: EventPriority = EventPriority.NORMAL):
    """Decorator to subscribe to events"""
    def decorator(func: Callable):
        subscribe(event_type, func, priority)
        return func
    return decorator


if __name__ == "__main__":
    # Test event bus
    print("Testing Bosco OS Event Bus...")
    
    @on_event(Events.SYSTEM_START)
    def on_start(event):
        print(f"System started: {event.data}")
    
    @on_event(Events.VOICE_COMMAND)
    def on_command(event):
        print(f"Voice command: {event.data}")
    
    # Publish events
    publish_sync(Events.SYSTEM_START, "Bosco OS initialized")
    publish_sync(Events.VOICE_COMMAND, "check the weather")
    
    print(f"Event history: {len(_event_bus.get_history())} events")

