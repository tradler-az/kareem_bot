"""
Bosco Core - Task Management Module
Day-to-day task management with recurring tasks, reminders, and persistence
"""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import uuid


# Task priority levels
PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW = "low"

# Task categories
CATEGORY_WORK = "work"
CATEGORY_PERSONAL = "personal"
CATEGORY_SHOPPING = "shopping"
CATEGORY_HEALTH = "health"
CATEGORY_LEARNING = "learning"
CATEGORY_OTHER = "other"


@dataclass
class Task:
    """Task data structure"""
    id: str
    title: str
    description: str = ""
    priority: str = PRIORITY_MEDIUM
    category: str = CATEGORY_OTHER
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    completed: bool = False
    completed_at: Optional[str] = None
    created_at: str = ""
    recurring: bool = False
    recurrence_pattern: Optional[str] = None  # daily, weekly, monthly
    reminder_minutes: int = 15
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class TaskManager:
    """Task management with persistence and reminders"""
    
    def __init__(self, data_file: str = "data/tasks.json"):
        self.data_file = data_file
        self.tasks: Dict[str, Task] = {}
        self.reminder_callbacks: List[callable] = []
        self._lock = threading.Lock()
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(data_file) if os.path.dirname(data_file) else "data", exist_ok=True)
        
        # Load existing tasks
        self.load_tasks()
        
        # Start reminder checker
        self._running = True
        self._reminder_thread = threading.Thread(target=self._check_reminders, daemon=True)
        self._reminder_thread.start()
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for task_data in data.get('tasks', []):
                        task = Task(**task_data)
                        self.tasks[task.id] = task
                print(f"Loaded {len(self.tasks)} tasks")
            except Exception as e:
                print(f"Error loading tasks: {e}")
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            data = {
                'tasks': [asdict(task) for task in self.tasks.values()],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def add_task(self, title: str, description: str = "", priority: str = PRIORITY_MEDIUM,
                 category: str = CATEGORY_OTHER, due_date: str = None, due_time: str = None,
                 recurring: bool = False, recurrence_pattern: str = None, 
                 reminder_minutes: int = 15, tags: List[str] = None) -> str:
        """Add a new task"""
        with self._lock:
            task_id = str(uuid.uuid4())[:8]
            task = Task(
                id=task_id,
                title=title,
                description=description,
                priority=priority,
                category=category,
                due_date=due_date,
                due_time=due_time,
                recurring=recurring,
                recurrence_pattern=recurrence_pattern,
                reminder_minutes=reminder_minutes,
                tags=tags or []
            )
            self.tasks[task_id] = task
            self.save_tasks()
            return task_id
    
    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed"""
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.completed = True
            task.completed_at = datetime.now().isoformat()
            
            # Handle recurring tasks
            if task.recurring and task.recurrence_pattern:
                self._create_next_recurrence(task)
            
            self.save_tasks()
            return True
    
    def _create_next_recurrence(self, task: Task):
        """Create next occurrence for recurring task"""
        now = datetime.now()
        
        if task.recurrence_pattern == "daily":
            next_due = now + timedelta(days=1)
        elif task.recurrence_pattern == "weekly":
            next_due = now + timedelta(weeks=1)
        elif task.recurrence_pattern == "monthly":
            next_due = now + timedelta(days=30)
        else:
            return
        
        new_task = Task(
            id=str(uuid.uuid4())[:8],
            title=task.title,
            description=task.description,
            priority=task.priority,
            category=task.category,
            due_date=next_due.strftime("%Y-%m-%d"),
            due_time=task.due_time,
            recurring=True,
            recurrence_pattern=task.recurrence_pattern,
            reminder_minutes=task.reminder_minutes,
            tags=task.tags.copy()
        )
        self.tasks[new_task.id] = new_task
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        with self._lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                self.save_tasks()
                return True
            return False
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update task fields"""
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            self.save_tasks()
            return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks(self, completed: bool = None, priority: str = None, 
                  category: str = None, due_today: bool = False) -> List[Task]:
        """Get tasks with optional filters"""
        result = []
        
        for task in self.tasks.values():
            # Apply filters
            if completed is not None and task.completed != completed:
                continue
            if priority and task.priority != priority:
                continue
            if category and task.category != category:
                continue
            if due_today and task.due_date:
                today = datetime.now().strftime("%Y-%m-%d")
                if task.due_date != today:
                    continue
            
            result.append(task)
        
        # Sort by priority and due date
        priority_order = {PRIORITY_HIGH: 0, PRIORITY_MEDIUM: 1, PRIORITY_LOW: 2}
        result.sort(key=lambda t: (priority_order.get(t.priority, 1), t.due_date or ""))
        
        return result
    
    def get_upcoming_tasks(self, days: int = 7) -> List[Task]:
        """Get tasks due in the next N days"""
        result = []
        now = datetime.now()
        end_date = now + timedelta(days=days)
        
        for task in self.tasks.values():
            if task.completed or not task.due_date:
                continue
            
            try:
                due = datetime.strptime(task.due_date, "%Y-%m-%d")
                if now <= due <= end_date:
                    result.append(task)
            except:
                continue
        
        return sorted(result, key=lambda t: t.due_date)
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks"""
        result = []
        today = datetime.now().strftime("%Y-%m-%d")
        
        for task in self.tasks.values():
            if task.completed or not task.due_date:
                continue
            if task.due_date < today:
                result.append(task)
        
        return result
    
    def add_reminder_callback(self, callback: callable):
        """Add a callback for task reminders"""
        self.reminder_callbacks.append(callback)
    
    def _check_reminders(self):
        """Check for upcoming task reminders"""
        while self._running:
            try:
                now = datetime.now()
                
                for task in self.tasks.values():
                    if task.completed or not task.due_date or not task.due_time:
                        continue
                    
                    # Parse due datetime
                    try:
                        due_datetime = datetime.strptime(
                            f"{task.due_date} {task.due_time}", 
                            "%Y-%m-%d %H:%M"
                        )
                    except:
                        continue
                    
                    # Check if reminder time
                    reminder_time = due_datetime - timedelta(minutes=task.reminder_minutes)
                    if now >= reminder_time and now < due_datetime:
                        # Trigger reminder
                        for callback in self.reminder_callbacks:
                            try:
                                callback(task)
                            except:
                                pass
                
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"Reminder check error: {e}")
                time.sleep(30)
    
    def stop(self):
        """Stop the reminder checker"""
        self._running = False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get task statistics"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.completed)
        pending = total - completed
        overdue = len(self.get_overdue_tasks())
        
        by_priority = {
            PRIORITY_HIGH: sum(1 for t in self.tasks.values() if t.priority == PRIORITY_HIGH and not t.completed),
            PRIORITY_MEDIUM: sum(1 for t in self.tasks.values() if t.priority == PRIORITY_MEDIUM and not t.completed),
            PRIORITY_LOW: sum(1 for t in self.tasks.values() if t.priority == PRIORITY_LOW and not t.completed),
        }
        
        by_category = {}
        for task in self.tasks.values():
            if not task.completed:
                by_category[task.category] = by_category.get(task.category, 0) + 1
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "overdue": overdue,
            "by_priority": by_priority,
            "by_category": by_category
        }
    
    def format_task_list(self, tasks: List[Task] = None) -> str:
        """Format task list as readable text"""
        if tasks is None:
            tasks = self.get_tasks(completed=False)
        
        if not tasks:
            return "No tasks found."
        
        lines = ["📋 Your Tasks:", "=" * 40]
        
        for i, task in enumerate(tasks, 1):
            status = "✅" if task.completed else "⬜"
            priority_emoji = {
                PRIORITY_HIGH: "🔴",
                PRIORITY_MEDIUM: "🟡",
                PRIORITY_LOW: "🟢"
            }.get(task.priority, "⬜")
            
            line = f"{i}. {status} {priority_emoji} {task.title}"
            if task.due_date:
                line += f" (Due: {task.due_date})"
            if task.recurring:
                line += " 🔄"
            
            lines.append(line)
            
            if task.description:
                lines.append(f"   📝 {task.description}")
        
        return "\n".join(lines)


# Global task manager instance
_task_manager = None


def get_task_manager(data_file: str = None) -> TaskManager:
    """Get or create the global task manager"""
    global _task_manager
    if _task_manager is None:
        if data_file is None:
            # Load from config
            import json
            for path in ['config.json', 'bosco_os/config.json']:
                if os.path.exists(path):
                    with open(path) as f:
                        config = json.load(f)
                        task_config = config.get('task_management', {})
                        data_file = task_config.get('data_file', 'data/tasks.json')
                        break
            if data_file is None:
                data_file = 'data/tasks.json'
        
        _task_manager = TaskManager(data_file)
    return _task_manager


# Quick functions for CLI
def add_task(title: str, **kwargs) -> str:
    """Add a new task"""
    manager = get_task_manager()
    task_id = manager.add_task(title, **kwargs)
    return f"Task added: {title} (ID: {task_id})"


def list_tasks(completed: bool = None, priority: str = None) -> str:
    """List tasks"""
    manager = get_task_manager()
    tasks = manager.get_tasks(completed=completed, priority=priority)
    return manager.format_task_list(tasks)


def complete_task(task_id: str) -> str:
    """Complete a task"""
    manager = get_task_manager()
    if manager.complete_task(task_id):
        return "Task completed! ✅"
    return "Task not found."


def delete_task(task_id: str) -> str:
    """Delete a task"""
    manager = get_task_manager()
    if manager.delete_task(task_id):
        return "Task deleted."
    return "Task not found."


def show_stats() -> str:
    """Show task statistics"""
    manager = get_task_manager()
    stats = manager.get_stats()
    
    return f"""
📊 Task Statistics:
━━━━━━━━━━━━━━━━━━
Total: {stats['total']}
Completed: {stats['completed']}
Pending: {stats['pending']}
Overdue: {stats['overdue']}

By Priority:
  🔴 High: {stats['by_priority'].get(PRIORITY_HIGH, 0)}
  🟡 Medium: {stats['by_priority'].get(PRIORITY_MEDIUM, 0)}
  🟢 Low: {stats['by_priority'].get(PRIORITY_LOW, 0)}
"""


if __name__ == "__main__":
    # Test task manager
    print("Testing Task Manager...")
    
    tm = get_task_manager()
    
    # Add some test tasks
    add_task("Review project documentation", category=CATEGORY_WORK, priority=PRIORITY_HIGH)
    add_task("Buy groceries", category=CATEGORY_SHOPPING, priority=PRIORITY_MEDIUM)
    add_task("Exercise", category=CATEGORY_HEALTH, priority=PRIORITY_LOW, recurring=True, recurrence_pattern="daily")
    
    print(list_tasks())
    print(show_stats())

