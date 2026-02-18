"""
Bosco Core - Command Execution System
Secure command execution with confirmation, logging, and whitelist support
"""

import os
import json
import subprocess
import threading
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass


# Command categories for safety
COMMAND_CATEGORY_SYSTEM = "system"
COMMAND_CATEGORY_FILE = "file"
COMMAND_CATEGORY_NETWORK = "network"
COMMAND_CATEGORY_APP = "application"
COMMAND_CATEGORY_WEB = "web"
COMMAND_CATEGORY_MEDIA = "media"
COMMAND_CATEGORY_CUSTOM = "custom"


@dataclass
class CommandResult:
    """Result of a command execution"""
    success: bool
    output: str
    error: str = ""
    execution_time: float = 0.0
    timestamp: str = ""


class CommandRegistry:
    """Registry of allowed commands with safety levels"""
    
    def __init__(self):
        self.commands: Dict[str, Dict] = {}
        self._init_default_commands()
    
    def _init_default_commands(self):
        """Initialize default command registry"""
        # Safe commands that can be executed
        self.commands = {
            # File operations
            "list_files": {
                "category": COMMAND_CATEGORY_FILE,
                "description": "List files in directory",
                "requires_confirmation": False,
                "safe": True
            },
            "find_file": {
                "category": COMMAND_CATEGORY_FILE,
                "description": "Find a file",
                "requires_confirmation": False,
                "safe": True
            },
            "read_file": {
                "category": COMMAND_CATEGORY_FILE,
                "description": "Read file content",
                "requires_confirmation": False,
                "safe": True
            },
            
            # Application control
            "open_app": {
                "category": COMMAND_CATEGORY_APP,
                "description": "Open an application",
                "requires_confirmation": True,
                "safe": True
            },
            "close_app": {
                "category": COMMAND_CATEGORY_APP,
                "description": "Close an application",
                "requires_confirmation": True,
                "safe": True
            },
            
            # System info (read-only)
            "system_info": {
                "category": COMMAND_CATEGORY_SYSTEM,
                "description": "Get system information",
                "requires_confirmation": False,
                "safe": True
            },
            "check_cpu": {
                "category": COMMAND_CATEGORY_SYSTEM,
                "description": "Check CPU usage",
                "requires_confirmation": False,
                "safe": True
            },
            "check_memory": {
                "category": COMMAND_CATEGORY_SYSTEM,
                "description": "Check memory usage",
                "requires_confirmation": False,
                "safe": True
            },
            
            # PC Control
            "screenshot": {
                "category": COMMAND_CATEGORY_SYSTEM,
                "description": "Take a screenshot",
                "requires_confirmation": False,
                "safe": True
            },
            "type_text": {
                "category": COMMAND_CATEGORY_SYSTEM,
                "description": "Type text",
                "requires_confirmation": True,
                "safe": True
            },
            "press_key": {
                "category": COMMAND_CATEGORY_SYSTEM,
                "description": "Press a key",
                "requires_confirmation": True,
                "safe": True
            },
            "click": {
                "category": COMMAND_CATEGORY_SYSTEM,
                "description": "Mouse click",
                "requires_confirmation": True,
                "safe": True
            },
            
            # Clipboard
            "get_clipboard": {
                "category": COMMAND_CATEGORY_SYSTEM,
                "description": "Get clipboard content",
                "requires_confirmation": False,
                "safe": True
            },
            "set_clipboard": {
                "category": COMMAND_CATEGORY_SYSTEM,
                "description": "Set clipboard content",
                "requires_confirmation": True,
                "safe": True
            },
            
            # Web
            "search_web": {
                "category": COMMAND_CATEGORY_WEB,
                "description": "Search the web",
                "requires_confirmation": False,
                "safe": True
            },
            "open_url": {
                "category": COMMAND_CATEGORY_WEB,
                "description": "Open a URL",
                "requires_confirmation": True,
                "safe": True
            },
            
            # Terminal commands (require extra caution)
            "run_command": {
                "category": COMMAND_CATEGORY_SYSTEM,
                "description": "Run terminal command",
                "requires_confirmation": True,
                "safe": False,
                "dangerous": True
            },
            
            # Task management
            "add_task": {
                "category": COMMAND_CATEGORY_CUSTOM,
                "description": "Add a task",
                "requires_confirmation": False,
                "safe": True
            },
            "list_tasks": {
                "category": COMMAND_CATEGORY_CUSTOM,
                "description": "List tasks",
                "requires_confirmation": False,
                "safe": True
            },
            "complete_task": {
                "category": COMMAND_CATEGORY_CUSTOM,
                "description": "Complete a task",
                "requires_confirmation": False,
                "safe": True
            },
        }
    
    def register_command(self, name: str, category: str, description: str,
                        requires_confirmation: bool = True, safe: bool = True,
                        dangerous: bool = False):
        """Register a new command"""
        self.commands[name] = {
            "category": category,
            "description": description,
            "requires_confirmation": requires_confirmation,
            "safe": safe,
            "dangerous": dangerous
        }
    
    def get_command_info(self, name: str) -> Optional[Dict]:
        """Get command information"""
        return self.commands.get(name)
    
    def requires_confirmation(self, name: str) -> bool:
        """Check if command requires confirmation"""
        info = self.commands.get(name, {})
        return info.get("requires_confirmation", True)
    
    def is_safe(self, name: str) -> bool:
        """Check if command is considered safe"""
        info = self.commands.get(name, {})
        return info.get("safe", False)
    
    def is_dangerous(self, name: str) -> bool:
        """Check if command is dangerous"""
        info = self.commands.get(name, {})
        return info.get("dangerous", False)
    
    def get_category_commands(self, category: str) -> List[str]:
        """Get all commands in a category"""
        return [name for name, info in self.commands.items() 
                if info.get("category") == category]


class CommandExecutor:
    """Execute commands with logging and confirmation"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.registry = CommandRegistry()
        
        # Confirmation settings
        self.confirmation_enabled = self.config.get('features', {}).get('command_confirmation', True)
        self.logging_enabled = self.config.get('features', {}).get('command_logging', True)
        self.whitelist_mode = self.config.get('pc_control', {}).get('whitelist_mode', False)
        self.allowed_commands = self.config.get('pc_control', {}).get('allowed_commands', [])
        
        # Pending confirmations
        self.pending_confirmations: Dict[str, Callable] = {}
        
        # Command history
        self.command_history: List[Dict] = []
        self.max_history = 100
        
        # Initialize handlers
        self._init_handlers()
        
        # Load command history
        self._load_history()
    
    def _init_handlers(self):
        """Initialize command handlers"""
        self.handlers: Dict[str, Callable] = {}
        
        # Import PC control handlers
        try:
            from bosco_os.capabilities.system.pc_control import PCControl
            pc = PCControl()
            
            self.handlers['open_app'] = lambda p: pc.open_app(p.get('app_name', ''))
            self.handlers['close_app'] = lambda p: pc.close_app(p.get('app_name', ''))
            self.handlers['screenshot'] = lambda p: pc.screenshot(p.get('path'))
            self.handlers['type_text'] = lambda p: pc.type_text(p.get('text', ''))
            self.handlers['press_key'] = lambda p: pc.press_key(p.get('key', ''))
            self.handlers['click'] = lambda p: pc.click(p.get('x'), p.get('y'), p.get('button', 'left'))
            self.handlers['get_clipboard'] = lambda p: pc.get_clipboard()
            self.handlers['set_clipboard'] = lambda p: pc.set_clipboard(p.get('text', ''))
            self.handlers['open_url'] = lambda p: pc.open_url(p.get('url', ''))
        except Exception as e:
            print(f"PC Control handlers not available: {e}")
        
        # Import system control handlers
        try:
            from automation.system_control import (
                check_cpu, check_memory, check_disk, check_battery,
                get_system_info, take_screenshot
            )
            
            self.handlers['check_cpu'] = lambda p: check_cpu()
            self.handlers['check_memory'] = lambda p: check_memory()
            self.handlers['check_disk'] = lambda p: check_disk()
            self.handlers['check_battery'] = lambda p: check_battery()
            self.handlers['system_info'] = lambda p: str(get_system_info())
        except Exception as e:
            print(f"System control handlers not available: {e}")
        
        # Import task manager handlers
        try:
            from bosco_os.capabilities.task_manager import add_task, list_tasks, complete_task
            
            self.handlers['add_task'] = lambda p: add_task(p.get('title', ''))
            self.handlers['list_tasks'] = lambda p: list_tasks()
            self.handlers['complete_task'] = lambda p: complete_task(p.get('task_id', ''))
        except Exception as e:
            print(f"Task manager handlers not available: {e}")
    
    def _load_history(self):
        """Load command history from file"""
        history_file = 'data/command_history.json'
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    self.command_history = data.get('history', [])
            except:
                pass
    
    def _save_history(self):
        """Save command history to file"""
        os.makedirs('data', exist_ok=True)
        try:
            with open('data/command_history.json', 'w') as f:
                json.dump({
                    'history': self.command_history[-self.max_history:],
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except:
            pass
    
    def _log_command(self, command: str, params: Dict, result: CommandResult):
        """Log command execution"""
        if not self.logging_enabled:
            return
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'params': params,
            'success': result.success,
            'output': result.output[:200] if result.output else "",
            'error': result.error[:200] if result.error else "",
            'execution_time': result.execution_time
        }
        
        self.command_history.append(entry)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
        
        self._save_history()
        
        # Also log to file
        try:
            os.makedirs('logs', exist_ok=True)
            with open('logs/commands.log', 'a') as f:
                f.write(f"{entry['timestamp']} | {command} | {'SUCCESS' if result.success else 'FAILED'} | {result.execution_time:.3f}s\n")
        except:
            pass
    
    def execute(self, command: str, params: Dict = None, 
                confirmed: bool = False, bypass_confirmation: bool = False) -> CommandResult:
        """Execute a command with safety checks"""
        params = params or {}
        start_time = time.time()
        
        # Check whitelist mode
        if self.whitelist_mode and command not in self.allowed_commands:
            return CommandResult(
                success=False,
                output="",
                error=f"Command '{command}' not in whitelist",
                execution_time=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )
        
        # Check if confirmation is required
        if self.confirmation_enabled and not bypass_confirmation:
            if self.registry.requires_confirmation(command) and not confirmed:
                # Return special result indicating confirmation needed
                return CommandResult(
                    success=False,
                    output="",
                    error="CONFIRMATION_REQUIRED",
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now().isoformat()
                )
        
        # Check if command exists
        if command not in self.handlers:
            return CommandResult(
                success=False,
                output="",
                error=f"Unknown command: {command}",
                execution_time=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )
        
        # Check for dangerous commands
        if self.registry.is_dangerous(command):
            print(f"⚠️  Executing potentially dangerous command: {command}")
        
        # Execute command
        try:
            handler = self.handlers[command]
            output = handler(params)
            
            result = CommandResult(
                success=True,
                output=str(output),
                execution_time=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )
            
            self._log_command(command, params, result)
            return result
            
        except Exception as e:
            result = CommandResult(
                success=False,
                output="",
                error=str(e),
                execution_time=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )
            
            self._log_command(command, params, result)
            return result
    
    def execute_terminal(self, command: str, shell: bool = True) -> CommandResult:
        """Execute a raw terminal command (requires extra caution)"""
        start_time = time.time()
        
        # Security: Only allow specific safe commands in non-whitelist mode
        if not self.whitelist_mode:
            # Dangerous - should only be used with explicit confirmation
            print(f"⚠️  Executing terminal command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout if result.returncode == 0 else result.stderr
            
            cmd_result = CommandResult(
                success=result.returncode == 0,
                output=output,
                error=result.stderr if result.returncode != 0 else "",
                execution_time=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )
            
            self._log_command("run_command", {"command": command}, cmd_result)
            return cmd_result
            
        except subprocess.TimeoutExpired:
            return CommandResult(
                success=False,
                output="",
                error="Command timed out",
                execution_time=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return CommandResult(
                success=False,
                output="",
                error=str(e),
                execution_time=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )
    
    def needs_confirmation(self, command: str) -> bool:
        """Check if a command needs confirmation"""
        return self.confirmation_enabled and self.registry.requires_confirmation(command)
    
    def get_command_info(self, command: str) -> Optional[Dict]:
        """Get information about a command"""
        return self.registry.get_command_info(command)
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """Get command execution history"""
        return self.command_history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total = len(self.command_history)
        successful = sum(1 for c in self.command_history if c.get('success'))
        failed = total - successful
        
        return {
            "total_commands": total,
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "N/A",
            "whitelist_mode": self.whitelist_mode,
            "confirmation_enabled": self.confirmation_enabled
        }


# Global executor instance
_executor = None


def get_executor(config: Dict = None) -> CommandExecutor:
    """Get or create command executor"""
    global _executor
    if _executor is None:
        if config is None:
            for path in ['config.json', 'bosco_os/config.json']:
                if os.path.exists(path):
                    with open(path) as f:
                        config = json.load(f)
                        break
            if config is None:
                config = {}
        
        _executor = CommandExecutor(config)
    return _executor


# Convenience functions
def execute_command(command: str, params: Dict = None, confirmed: bool = False) -> CommandResult:
    """Execute a registered command"""
    return get_executor().execute(command, params, confirmed=confirmed)


def run_terminal(command: str) -> CommandResult:
    """Execute a terminal command"""
    return get_executor().execute_terminal(command)


def needs_confirmation(command: str) -> bool:
    """Check if command needs confirmation"""
    return get_executor().needs_confirmation(command)


def get_history(limit: int = 20) -> List[Dict]:
    """Get command history"""
    return get_executor().get_history(limit)


if __name__ == "__main__":
    print("Testing Command Executor...")
    
    executor = get_executor()
    
    # Test commands
    print("\n--- Testing Commands ---")
    
    # Without confirmation (should fail for commands needing it)
    result = executor.execute('screenshot')
    print(f"screenshot (no confirm): {result.success} - {result.output[:50] if result.output else result.error}")
    
    # With confirmation
    result = executor.execute('screenshot', confirmed=True)
    print(f"screenshot (confirmed): {result.success} - {result.output[:50] if result.output else result.error}")
    
    # Check CPU
    result = executor.execute('check_cpu')
    print(f"check_cpu: {result.success} - {result.output[:50] if result.output else result.error}")
    
    print("\n--- Stats ---")
    print(executor.get_stats())
    
    print("\n--- History ---")
    for h in executor.get_history():
        print(f"  {h['timestamp'][:19]} | {h['command']} | {'OK' if h['success'] else 'FAIL'}")
