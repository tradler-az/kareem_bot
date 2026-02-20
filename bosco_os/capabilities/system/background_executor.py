"""
Bosco Core - Background Executor Module
Handles background command execution with sudo password handling
"""

import os
import sys
import subprocess
import threading
import time
import queue
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import signal
import fcntl
import select


class BackgroundExecutor:
    """
    Execute commands in background with sudo password handling
    """

    def __init__(self):
        self.active_tasks = {}
        self.task_id_counter = 0
        self.sudo_password = None
        self.sudo_timestamp = None
        self.sudo_timeout = 300  # 5 minutes cache
        
    def set_sudo_password(self, password: str):
        """Cache sudo password for automatic use"""
        self.sudo_password = password
        self.sudo_timestamp = time.time()
        return "Sudo password cached for this session"
    
    def is_sudo_valid(self) -> bool:
        """Check if cached sudo is still valid"""
        if not self.sudo_password or not self.sudo_timestamp:
            return False
        return (time.time() - self.sudo_timestamp) < self.sudo_timeout
    
    def clear_sudo(self):
        """Clear cached sudo password"""
        self.sudo_password = None
        self.sudo_timestamp = None
    
    def execute_background(
        self, 
        command: str, 
        use_sudo: bool = False,
        callback: Optional[Callable] = None,
        task_name: Optional[str] = None
    ) -> str:
        """
        Execute command in background
        
        Args:
            command: The command to execute
            use_sudo: Whether to use sudo
            callback: Optional callback function when done
            task_name: Optional name for the task
            
        Returns:
            Task ID for tracking
        """
        self.task_id_counter += 1
        task_id = f"task_{self.task_id_counter}"
        
        if not task_name:
            task_name = command[:50]
        
        # Prepare command with sudo if needed
        if use_sudo:
            if self.is_sudo_valid():
                command = f"echo '{self.sudo_password}' | sudo -S {command}"
            else:
                return "Error: No sudo password cached. Say 'cache sudo password' first."
        
        # Create task info
        task_info = {
            'id': task_id,
            'name': task_name,
            'command': command,
            'start_time': datetime.now(),
            'status': 'running',
            'progress': 0,
            'output': '',
            'error': '',
            'callback': callback
        }
        
        self.active_tasks[task_id] = task_info
        
        # Start background thread
        thread = threading.Thread(
            target=self._run_task,
            args=(task_id,),
            daemon=True
        )
        thread.start()
        
        return f"Started task {task_id}: {task_name}"
    
    def _run_task(self, task_id: str):
        """Run task in background thread"""
        task = self.active_tasks.get(task_id)
        if not task:
            return
        
        try:
            # Use Popen for background execution
            process = subprocess.Popen(
                task['command'],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            task['process'] = process
            task['pid'] = process.pid
            
            # Read output in real-time
            output_lines = []
            while True:
                # Check if process is done
                retcode = process.poll()
                
                # Read stdout
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        output_lines.append(line)
                        task['output'] = ''.join(output_lines[-100:])  # Keep last 100 lines
                
                # Check stderr
                if process.stderr:
                    err_line = process.stderr.readline()
                    if err_line:
                        task['error'] += err_line
                
                if retcode is not None:
                    break
                
                time.sleep(0.1)
            
            # Process completed
            task['status'] = 'completed'
            task['returncode'] = retcode
            task['end_time'] = datetime.now()
            
            # Execute callback if provided
            if task['callback']:
                try:
                    task['callback'](task)
                except Exception as e:
                    task['error'] += f"\nCallback error: {str(e)}"
                    
        except Exception as e:
            task['status'] = 'failed'
            task['error'] = str(e)
            task['end_time'] = datetime.now()
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a background task"""
        task = self.active_tasks.get(task_id)
        if not task:
            return {'error': 'Task not found'}
        
        duration = None
        if task.get('start_time'):
            end = task.get('end_time', datetime.now())
            duration = (end - task['start_time']).total_seconds()
        
        return {
            'id': task['id'],
            'name': task['name'],
            'status': task['status'],
            'progress': task.get('progress', 0),
            'output': task.get('output', '')[:500],
            'error': task.get('error', ''),
            'returncode': task.get('returncode'),
            'duration': duration,
            'pid': task.get('pid')
        }
    
    def list_tasks(self) -> str:
        """List all background tasks"""
        if not self.active_tasks:
            return "No background tasks running"
        
        result = "Background Tasks:\n\n"
        for task_id, task in self.active_tasks.items():
            duration = ""
            if task.get('start_time'):
                end = task.get('end_time', datetime.now())
                duration = f"({(end - task['start_time']).total_seconds():.1f}s)"
            
            result += f"{task_id}: {task['name']} - {task['status']} {duration}\n"
        
        return result
    
    def cancel_task(self, task_id: str) -> str:
        """Cancel a running task"""
        task = self.active_tasks.get(task_id)
        if not task:
            return f"Task {task_id} not found"
        
        if task['status'] != 'running':
            return f"Task {task_id} is not running"
        
        try:
            if 'process' in task:
                task['process'].terminate()
                task['status'] = 'cancelled'
                return f"Cancelled task {task_id}"
        except Exception as e:
            return f"Error cancelling: {str(e)}"
        
        return "Could not cancel task"
    
    def run_with_progress(
        self, 
        command: str, 
        progress_callback: Callable[[int, str], None],
        use_sudo: bool = False
    ) -> str:
        """
        Run command with progress updates
        
        Args:
            command: Command to run
            progress_callback: Function called with (progress, message)
            use_sudo: Whether to use sudo
            
        Returns:
            Final output
        """
        if use_sudo:
            if self.is_sudo_valid():
                command = f"echo '{self.sudo_password}' | sudo -S {command}"
            else:
                return "Error: No sudo password cached"
        
        progress_callback(0, "Starting...")
        
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            output = []
            while True:
                line = process.stdout.readline()
                if line:
                    output.append(line)
                    # Update progress based on output patterns
                    progress_callback(50, line.strip()[:100])
                
                if process.poll() is not None:
                    break
                
                time.sleep(0.1)
            
            progress_callback(100, "Completed")
            return ''.join(output)
            
        except Exception as e:
            progress_callback(-1, f"Error: {str(e)}")
            return str(e)


# Global instance
_executor = None

def get_background_executor() -> BackgroundExecutor:
    """Get background executor instance"""
    global _executor
    if _executor is None:
        _executor = BackgroundExecutor()
    return _executor


# Convenience functions
def run_background(
    command: str, 
    use_sudo: bool = False,
    callback: Optional[Callable] = None,
    task_name: Optional[str] = None
) -> str:
    """Run command in background"""
    return get_background_executor().execute_background(
        command, use_sudo, callback, task_name
    )

def cache_sudo_password(password: str) -> str:
    """Cache sudo password"""
    return get_background_executor().set_sudo_password(password)

def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get task status"""
    return get_background_executor().get_task_status(task_id)

def list_background_tasks() -> str:
    """List all tasks"""
    return get_background_executor().list_tasks()

def cancel_task(task_id: str) -> str:
    """Cancel a task"""
    return get_background_executor().cancel_task(task_id)


if __name__ == "__main__":
    print("=== Background Executor Test ===\n")
    
    executor = get_background_executor()
    
    # Test background task
    print("Starting background task...")
    result = executor.execute_background(
        "sleep 3 && echo 'Task completed!'",
        task_name="Test sleep task"
    )
    print(result)
    
    time.sleep(1)
    
    print("\nListing tasks:")
    print(executor.list_tasks())
    
    print("\nChecking status:")
    status = executor.get_task_status("task_1")
    print(f"Status: {status['status']}")
    
    print("\nWaiting for completion...")
    time.sleep(4)
    
    print("\nFinal status:")
    status = executor.get_task_status("task_1")
    print(f"Status: {status['status']}")
    print(f"Output: {status.get('output', 'N/A')}")

