"""
Bosco Core - Tool-Use & Self-Correction Loop (ReAct Engine)
Implements reasoning/act logic with automatic error recovery
"""

import asyncio
import re
import subprocess
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    FATAL = "fatal"       # Cannot recover
    CRITICAL = "critical" # Needs major fix
    RECOVERABLE = "recoverable"  # Can auto-recover
    WARNING = "warning"    # Informational only


class CommandError:
    """Represents a command execution error"""
    
    def __init__(
        self,
        command: str,
        stderr: str,
        stdout: str,
        returncode: int,
        severity: ErrorSeverity = ErrorSeverity.RECOVERABLE
    ):
        self.command = command
        self.stderr = stderr
        self.stdout = stdout
        self.returncode = returncode
        self.severity = severity
        self.timestamp = datetime.now()
        self.suggestions: List[str] = []
        
        # Analyze error and generate suggestions
        self._analyze_error()
    
    def _analyze_error(self):
        """Analyze error and generate recovery suggestions"""
        
        # Command not found
        if "command not found" in self.stderr.lower() or "not recognized" in self.stderr.lower():
            self.severity = ErrorSeverity.RECOVERABLE
            # Extract the missing command
            match = re.search(r"(\w+): command not found", self.stderr.lower())
            if match:
                missing_cmd = match.group(1)
                self.suggestions.extend([
                    f"Install {missing_cmd}: sudo apt install {missing_cmd}",
                    f"Check if {missing_cmd} is in your PATH"
                ])
        
        # Permission denied
        elif "permission denied" in self.stderr.lower() or "access denied" in self.stderr.lower():
            self.severity = ErrorSeverity.RECOVERABLE
            self.suggestions.extend([
                "Run with sudo: sudo " + self.command,
                "Check file permissions: ls -la"
            ])
        
        # No such file or directory
        elif "no such file or directory" in self.stderr.lower():
            self.severity = ErrorSeverity.RECOVERABLE
            self.suggestions.extend([
                "Check if the file/path exists",
                "Create the required directory first"
            ])
        
        # Syntax error
        elif "syntax error" in self.stderr.lower() or "parse error" in self.stderr.lower():
            self.severity = ErrorSeverity.CRITICAL
            self.suggestions.extend([
                "Check the command syntax",
                "Verify the command arguments"
            ])
        
        # Network error
        elif "connection" in self.stderr.lower() or "network" in self.stderr.lower():
            self.severity = ErrorSeverity.RECOVERABLE
            self.suggestions.extend([
                "Check network connectivity",
                "Verify the remote host is reachable"
            ])
        
        # Timeout
        elif "timeout" in self.stderr.lower():
            self.severity = ErrorSeverity.RECOVERABLE
            self.suggestions.extend([
                "Increase timeout value",
                "Check if the service is responding"
            ])
        
        # Dependency missing
        elif "dependency" in self.stderr.lower() or "module not found" in self.stderr.lower():
            self.severity = ErrorSeverity.RECOVERABLE
            self.suggestions.extend([
                "Install required dependencies",
                "Check Python package requirements"
            ])
    
    def to_dict(self) -> Dict:
        return {
            "command": self.command,
            "stderr": self.stderr[:500],
            "stdout": self.stdout[:500],
            "returncode": self.returncode,
            "severity": self.severity.value,
            "suggestions": self.suggestions,
            "timestamp": self.timestamp.isoformat()
        }


class ReActEngine:
    """
    Reasoning Engine with Self-Correction (ReAct)
    Implements the Reason/Act loop for robust command execution
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.max_retries = 3
        self.execution_history: List[Dict] = []
        self.auto_fix_enabled = True
        
        # Known fix patterns
        self.fix_patterns = [
            (r"(\w+): command not found", self._fix_missing_command),
            (r"Permission denied", self._fix_permission),
            (r"No such file or directory", self._fix_missing_file),
        ]
    
    async def execute_with_retry(
        self,
        command: str,
        timeout: int = 30,
        context: Dict = None
    ) -> Dict[str, Any]:
        """
        Execute command with automatic retry and self-correction
        
        Args:
            command: The command to execute
            timeout: Command timeout in seconds
            context: Additional context for recovery
            
        Returns:
            Dictionary with execution result and any recovery actions
        """
        
        attempt = 0
        last_error: Optional[CommandError] = None
        recovery_actions: List[str] = []
        
        while attempt < self.max_retries:
            attempt += 1
            
            # Execute command
            result = await self._execute_command(command, timeout)
            
            if result["success"]:
                # Success - record and return
                self._record_execution(command, result, success=True)
                return {
                    "success": True,
                    "result": result,
                    "attempts": attempt,
                    "recovered": len(recovery_actions) > 0,
                    "recovery_actions": recovery_actions
                }
            
            # Command failed - analyze error
            error = CommandError(
                command=command,
                stderr=result.get("stderr", ""),
                stdout=result.get("stdout", ""),
                returncode=result.get("returncode", -1)
            )
            
            last_error = error
            self._record_execution(command, result, success=False, error=error)
            
            # Check if we can recover
            if self.auto_fix_enabled and error.severity != ErrorSeverity.FATAL:
                fix_result = await self._attempt_fix(error, context)
                
                if fix_result["can_fix"]:
                    recovery_actions.append(fix_result["action"])
                    command = fix_result["new_command"]
                    continue
            
            # Cannot recover or max retries reached
            break
        
        return {
            "success": False,
            "result": result if result else {},
            "error": last_error.to_dict() if last_error else None,
            "attempts": attempt,
            "recovery_actions": recovery_actions,
            "final_suggestions": last_error.suggestions if last_error else []
        }
    
    async def _execute_command(
        self,
        command: str,
        timeout: int
    ) -> Dict[str, Any]:
        """Execute a shell command"""
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout
                )
                
                return {
                    "success": proc.returncode == 0,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "returncode": proc.returncode
                }
            except asyncio.TimeoutError:
                proc.kill()
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "Command timed out",
                    "returncode": -1
                }
        
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    async def _attempt_fix(
        self,
        error: CommandError,
        context: Dict = None
    ) -> Dict[str, Any]:
        """
        Attempt to automatically fix the error
        
        Returns:
            Dictionary with fix result
        """
        
        # Try pattern-based fixes first
        for pattern, fix_func in self.fix_patterns:
            if re.search(pattern, error.stderr):
                return await fix_func(self, error, context)
        
        # If LLM client is available, use it for intelligent fix
        if self.llm_client:
            return await self._llm_fix(error, context)
        
        return {
            "can_fix": False,
            "reason": "No automatic fix available"
        }
    
    async def _fix_missing_command(
        self,
        error: CommandError,
        context: Dict = None
    ) -> Dict[str, Any]:
        """Fix missing command error by suggesting installation"""
        
        # Extract command name
        match = re.search(r"(\w+): command not found", error.stderr.lower())
        if not match:
            return {"can_fix": False}
        
        missing_cmd = match.group(1)
        
        # Generate install command
        install_cmd = f"sudo apt install {missing_cmd} -y"
        
        return {
            "can_fix": True,
            "action": f"Install {missing_cmd}",
            "fix_command": install_cmd,
            "new_command": error.command,  # Retry original after fix
            "requires_user_confirmation": True
        }
    
    async def _fix_permission(
        self,
        error: CommandError,
        context: Dict = None
    ) -> Dict[str, Any]:
        """Fix permission error"""
        
        return {
            "can_fix": True,
            "action": "Add sudo prefix",
            "fix_command": f"sudo {error.command}",
            "new_command": f"sudo {error.command}",
            "requires_user_confirmation": True
        }
    
    async def _fix_missing_file(
        self,
        error: CommandError,
        context: Dict = None
    ) -> Dict[str, Any]:
        """Fix missing file error"""
        
        # Extract path
        match = re.search(r"`([^']+)'", error.stderr)
        if not match:
            return {"can_fix": False}
        
        missing_path = match.group(1)
        
        # Check if it's a directory issue
        if "/" in missing_path:
            dir_path = "/".join(missing_path.split("/")[:-1])
            return {
                "can_fix": True,
                "action": f"Create directory {dir_path}",
                "fix_command": f"mkdir -p {dir_path}",
                "new_command": error.command,
                "requires_user_confirmation": True
            }
        
        return {"can_fix": False}
    
    async def _llm_fix(
        self,
        error: CommandError,
        context: Dict = None
    ) -> Dict[str, Any]:
        """Use LLM to intelligently fix the error"""
        
        if not self.llm_client:
            return {"can_fix": False}
        
        # This would call the LLM to analyze and fix the error
        # Implementation depends on LLM client interface
        return {"can_fix": False, "reason": "LLM fix not implemented"}
    
    def _record_execution(
        self,
        command: str,
        result: Dict,
        success: bool,
        error: CommandError = None
    ):
        """Record execution in history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "success": success,
            "returncode": result.get("returncode"),
            "error": error.to_dict() if error else None
        }
        
        self.execution_history.append(entry)
        
        # Keep history manageable
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-500:]
    
    def get_execution_stats(self) -> Dict:
        """Get execution statistics"""
        total = len(self.execution_history)
        successful = sum(1 for e in self.execution_history if e["success"])
        
        return {
            "total_executions": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / max(total, 1)
        }


class ExecutionValidator:
    """
    Validates commands before execution for safety
    """
    
    # Block dangerous commands
    BLOCKED_PATTERNS = [
        r"rm\s+-rf\s+/\s*",  # Delete root
        r"dd\s+if=.*of=/dev/",  # Direct disk write
        r">\s*/dev/sd",  # Direct block device
        r"mkfs\.",  # Format filesystem
        r":\(\)\{",  # Fork bomb
    ]
    
    # Commands requiring confirmation
    CONFIRMATION_REQUIRED = [
        r"sudo\s+rm",
        r"sudo\s+dd",
        r"sudo\s+mkfs",
        r"sudo\s+shutdown",
        r"sudo\s+reboot",
        r"sudo\s+killall",
        r"drop\s+database",
    ]
    
    def __init__(self):
        self.blocked_count = 0
        self.confirmation_count = 0
    
    def validate(self, command: str) -> Dict[str, Any]:
        """
        Validate a command for safety
        
        Returns:
            Dictionary with validation result
        """
        
        # Check blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, command):
                self.blocked_count += 1
                return {
                    "safe": False,
                    "reason": "Command matches blocked pattern (dangerous)",
                    "requires_confirmation": False,
                    "action": "BLOCK"
                }
        
        # Check confirmation required
        for pattern in self.CONFIRMATION_REQUIRED:
            if re.search(pattern, command, re.IGNORECASE):
                self.confirmation_count += 1
                return {
                    "safe": True,
                    "reason": "Command requires user confirmation",
                    "requires_confirmation": True,
                    "action": "CONFIRM"
                }
        
        return {
            "safe": True,
            "reason": "Command appears safe",
            "requires_confirmation": False,
            "action": "EXECUTE"
        }
    
    def get_stats(self) -> Dict:
        return {
            "blocked_count": self.blocked_count,
            "confirmation_count": self.confirmation_count
        }


# Global instances
_react_engine: Optional[ReActEngine] = None
_validator: Optional[ExecutionValidator] = None


def get_react_engine(llm_client=None) -> ReActEngine:
    """Get the ReAct engine instance"""
    global _react_engine
    if _react_engine is None:
        _react_engine = ReActEngine(llm_client)
    return _react_engine


def get_execution_validator() -> ExecutionValidator:
    """Get the execution validator instance"""
    global _validator
    if _validator is None:
        _validator = ExecutionValidator()
    return _validator


if __name__ == "__main__":
    import asyncio
    
    print("=== Testing ReAct Engine ===\n")
    
    async def test():
        engine = get_react_engine()
        
        # Test a valid command
        result = await engine.execute_with_retry("echo 'Hello Bosco'")
        print(f"Valid command result: {result['success']}")
        
        # Test with a failing command
        result = await engine.execute_with_retry("nonexistent_command_xyz")
        print(f"Invalid command result: {result['success']}")
        print(f"Recovery actions: {result.get('recovery_actions', [])}")
        
        # Test validator
        validator = get_execution_validator()
        
        print("\nValidator tests:")
        tests = [
            "echo 'test'",
            "sudo rm -rf /",
            "ls -la"
        ]
        
        for cmd in tests:
            result = validator.validate(cmd)
            print(f"  {cmd}: {result['action']} - {result['reason']}")
    
    asyncio.run(test())

