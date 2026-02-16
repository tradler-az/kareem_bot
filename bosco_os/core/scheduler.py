"""
Bosco OS - Scheduler Module
Task scheduling and automation
"""

import threading
import time
from typing import Callable, Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import queue


@dataclass
class ScheduledTask:
    """Task scheduled for execution"""
    id: str
    name: str
    callback: Callable
    interval: Optional[int] = None
    schedule_time: Optional[datetime] = None
    repeat: bool = False
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class Scheduler:
    """Task scheduler for Bosco OS"""
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self._running = False
        self._thread = None
        self._stop_event = threading.Event()
    
    def start(self):
        """Start the scheduler"""
        if self._running:
            return
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._thread.start()
        print("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self._running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while not self._stop_event.is_set():
            self._check_tasks()
            time.sleep(1)
    
    def _check_tasks(self):
        """Check and execute scheduled tasks"""
        now = datetime.now()
        for task_id, task in self.tasks.items():
            if not task.enabled or not task.next_run:
                continue
            if now >= task.next_run:
                self._execute_task(task)
    
    def _execute_task(self, task: ScheduledTask):
        """Execute a scheduled task"""
        try:
            task.callback()
            task.last_run = datetime.now()
            if task.repeat and task.interval:
                task.next_run = datetime.now() + timedelta(seconds=task.interval)
            else:
                task.enabled = False
        except Exception as e:
            print(f"Task {task.id} error: {e}")
    
    def schedule_once(self, task_id: str, name: str, callback: Callable, schedule_time: datetime):
        """Schedule a one-time task"""
        task = ScheduledTask(task_id, name, callback, schedule_time=schedule_time, next_run=schedule_time)
        self.tasks[task_id] = task
    
    def schedule_interval(self, task_id: str, name: str, callback: Callable, interval: int, repeat: bool = True):
        """Schedule a recurring task"""
        task = ScheduledTask(task_id, name, callback, interval=interval, repeat=repeat, next_run=datetime.now() + timedelta(seconds=interval))
        self.tasks[task_id] = task
    
    def cancel(self, task_id: str):
        """Cancel a task"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False


_scheduler = Scheduler()

def get_scheduler():
    return _scheduler
