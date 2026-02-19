"""
Bosco Core - Execution Sandbox
Safely runs and tests generated code before applying to the main system
"""

import asyncio
import subprocess
import tempfile
import os
import uuid
import re
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import hashlib


class SandboxResult:
    """Result of sandbox execution"""
    
    def __init__(
        self,
        success: bool,
        stdout: str,
        stderr: str,
        returncode: int,
        execution_time: float,
        warnings: List[str] = None,
        errors: List[str] = None
    ):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.execution_time = execution_time
        self.warnings = warnings or []
        self.errors = errors or []
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "stdout": self.stdout[:1000],  # Limit output
            "stderr": self.stderr[:1000],
            "returncode": self.returncode,
            "execution_time": self.execution_time,
            "warnings": self.warnings,
            "errors": self.errors
        }


class ExecutionSandbox:
    """
    Secure execution sandbox for testing generated code
    Provides isolation and safety checks before running code
    """
    
    # Dangerous patterns that should be blocked
    DANGEROUS_PATTERNS = [
        (r"rm\s+-rf\s+/", "Recursive deletion of root"),
        (r">\s*/dev/sd[a-z]", "Direct disk write"),
        (r"dd\s+if=.*of=/dev/", "Direct block device write"),
        (r"mkfs\.", "Filesystem format"),
        (r":\(\)\s*\{.*:\|\:", "Fork bomb"),
        (r"import\s+os\s*;.*os\.system\s*\(", "Shell injection via os.system"),
        (r"__import__\s*\(\s*['\"]os['\"]\)\.system", "Dynamic shell execution"),
        (r"subprocess\s*\.run\s*\(\s*\[.*shell\s*=\s*True", "Shell=True subprocess"),
        (r"eval\s*\(", "Dangerous eval usage"),
        (r"exec\s*\(", "Dangerous exec usage"),
        (r"open\s*\(\s*['\"]/etc/passwd", "System file access"),
        (r"open\s*\(\s*['\"]/etc/shadow", "Shadow file access"),
    ]
    
    # Allowed file paths for file operations
    ALLOWED_PATHS = [
        "/tmp",
        "/home",
        "/var/tmp",
        "/opt",
    ]
    
    def __init__(
        self,
        timeout: int = 30,
        max_memory_mb: int = 512,
        network_enabled: bool = False
    ):
        self.timeout = timeout
        self.max_memory_mb = max_memory_mb
        self.network_enabled = network_enabled
        
        # Execution history
        self.execution_history: List[Dict] = []
        
        print(f"[Sandbox] Initialized (timeout={timeout}s, network={network_enabled})")
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze code for safety issues
        
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        
        # Check for dangerous patterns
        for pattern, description in self.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append({
                    "type": "dangerous",
                    "pattern": pattern,
                    "description": description
                })
        
        # Check for file operations
        if "open(" in code or "write" in code:
            # Check if paths are in allowed locations
            for match in re.finditer(r"open\s*\(\s*['\"]([^'\"]+)['\"]", code):
                path = match.group(1)
                if not any(path.startswith(allowed) for allowed in self.ALLOWED_PATHS):
                    warnings.append(f"File operation on non-standard path: {path}")
        
        # Check for imports
        if "import" in code:
            # Check for dangerous imports
            dangerous_imports = ["socket", "subprocess", "pty", "tty", "termios"]
            for imp in dangerous_imports:
                if f"import {imp}" in code or f"from {imp} import" in code:
                    if imp in ["socket", "pty", "tty", "termios"]:
                        warnings.append(f"Potentially dangerous import: {imp}")
        
        # Check for network operations
        if not self.network_enabled:
            if "requests" in code or "urllib" in code or "http" in code:
                issues.append({
                    "type": "network_blocked",
                    "description": "Network operations disabled in sandbox"
                })
        
        return {
            "safe": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "can_execute": len(issues) == 0
        }
    
    async def execute_python(
        self,
        code: str,
        input_data: str = "",
        env: Dict = None
    ) -> SandboxResult:
        """
        Execute Python code in sandbox
        
        Args:
            code: Python code to execute
            input_data: Optional stdin input
            env: Optional environment variables
            
        Returns:
            SandboxResult
        """
        
        start_time = datetime.now()
        
        # Analyze first
        analysis = self.analyze_code(code)
        
        if not analysis["can_execute"]:
            return SandboxResult(
                success=False,
                stdout="",
                stderr=f"Code blocked: {analysis['issues']}",
                returncode=-1,
                execution_time=0,
                errors=[i["description"] for i in analysis["issues"]],
                warnings=analysis["warnings"]
            )
        
        # Write code to temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Prepare environment
            exec_env = os.environ.copy()
            if env:
                exec_env.update(env)
            
            # Run with restricted globals
            result = await asyncio.create_subprocess_exec(
                "python3",
                temp_file,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=exec_env,
                cwd="/tmp"  # Restrict working directory
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    result.communicate(input_data.encode() if input_data else None),
                    timeout=self.timeout
                )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return SandboxResult(
                    success=result.returncode == 0,
                    stdout=stdout.decode(),
                    stderr=stderr.decode(),
                    returncode=result.returncode,
                    execution_time=execution_time,
                    warnings=analysis["warnings"]
                )
            
            except asyncio.TimeoutError:
                result.kill()
                return SandboxResult(
                    success=False,
                    stdout="",
                    stderr=f"Execution timed out after {self.timeout} seconds",
                    returncode=-1,
                    execution_time=self.timeout,
                    errors=["Timeout"]
                )
        
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
    
    async def execute_shell(
        self,
        command: str,
        shell: bool = True
    ) -> SandboxResult:
        """
        Execute shell command in sandbox
        
        Args:
            command: Shell command to execute
            shell: Whether to use shell
            
        Returns:
            SandboxResult
        """
        
        start_time = datetime.now()
        
        # Validate command
        if shell:
            analysis = self.analyze_code(command)
            if not analysis["can_execute"]:
                return SandboxResult(
                    success=False,
                    stdout="",
                    stderr=f"Command blocked: {analysis['issues']}",
                    returncode=-1,
                    execution_time=0,
                    errors=[i["description"] for i in analysis["issues"]]
                )
        
        try:
            result = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/tmp"
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    result.communicate(),
                    timeout=self.timeout
                )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return SandboxResult(
                    success=result.returncode == 0,
                    stdout=stdout.decode(),
                    stderr=stderr.decode(),
                    returncode=result.returncode,
                    execution_time=execution_time
                )
            
            except asyncio.TimeoutError:
                result.kill()
                return SandboxResult(
                    success=False,
                    stdout="",
                    stderr=f"Command timed out after {self.timeout}s",
                    returncode=-1,
                    execution_time=self.timeout,
                    errors=["Timeout"]
                )
        
        except Exception as e:
            return SandboxResult(
                success=False,
                stdout="",
                stderr=str(e),
                returncode=-1,
                execution_time=0,
                errors=[str(e)]
            )
    
    async def test_script(
        self,
        code: str,
        test_cases: List[Dict],
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Test generated script with test cases
        
        Args:
            code: The generated code
            test_cases: List of test cases with input/expected
            language: Language of code (python, shell)
            
        Returns:
            Test results
        """
        
        results = []
        all_passed = True
        
        for i, test in enumerate(test_cases):
            # Execute
            if language == "python":
                result = await self.execute_python(
                    code,
                    input_data=test.get("input", "")
                )
            else:
                result = await self.execute_shell(code)
            
            # Check result
            passed = result.success
            if "expected_returncode" in test:
                passed = passed and result.returncode == test["expected_returncode"]
            
            if "expected_output" in test:
                expected = test["expected_output"]
                passed = passed and expected in result.stdout
            
            if not passed:
                all_passed = False
            
            results.append({
                "test_case": i + 1,
                "passed": passed,
                "result": result.to_dict()
            })
        
        # Record in history
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "language": language,
            "test_cases": len(test_cases),
            "all_passed": all_passed,
            "results": results
        })
        
        return {
            "all_passed": all_passed,
            "test_results": results,
            "summary": {
                "total": len(test_cases),
                "passed": sum(1 for r in results if r["passed"]),
                "failed": sum(1 for r in results if not r["passed"])
            }
        }
    
    def validate_output(self, output: str, constraints: Dict) -> Dict[str, Any]:
        """
        Validate output against constraints
        
        Args:
            output: Command output
            constraints: Validation constraints
            
        Returns:
            Validation result
        """
        
        violations = []
        
        # Check max length
        if "max_length" in constraints:
            if len(output) > constraints["max_length"]:
                violations.append(f"Output exceeds max length: {len(output)} > {constraints['max_length']}")
        
        # Check for patterns to avoid
        if "forbidden_patterns" in constraints:
            for pattern in constraints["forbidden_patterns"]:
                if re.search(pattern, output):
                    violations.append(f"Output contains forbidden pattern: {pattern}")
        
        # Check required patterns
        if "required_patterns" in constraints:
            for pattern in constraints["required_patterns"]:
                if not re.search(pattern, output):
                    violations.append(f"Output missing required pattern: {pattern}")
        
        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
    
    def get_stats(self) -> Dict:
        """Get sandbox statistics"""
        return {
            "total_executions": len(self.execution_history),
            "timeout": self.timeout,
            "max_memory_mb": self.max_memory_mb,
            "network_enabled": self.network_enabled
        }


# Global instance
_sandbox: Optional[ExecutionSandbox] = None


def get_execution_sandbox(
    timeout: int = 30,
    max_memory_mb: int = 512,
    network_enabled: bool = False
) -> ExecutionSandbox:
    """Get the execution sandbox instance"""
    global _sandbox
    if _sandbox is None:
        _sandbox = ExecutionSandbox(timeout, max_memory_mb, network_enabled)
    return _sandbox


if __name__ == "__main__":
    import asyncio
    
    print("=== Testing Execution Sandbox ===\n")
    
    async def test():
        sandbox = get_execution_sandbox(timeout=10)
        
        # Test safe code
        print("Testing safe code...")
        code = """
import sys
print("Hello from sandbox!")
print("Arguments:", sys.argv)
"""
        
        result = await sandbox.execute_python(code)
        print(f"  Success: {result.success}")
        print(f"  Output: {result.stdout.strip()}")
        
        # Test dangerous code
        print("\nTesting dangerous code...")
        dangerous_code = """
import os
os.system("rm -rf /")
"""
        
        result = await sandbox.execute_python(dangerous_code)
        print(f"  Blocked: {not result.success}")
        print(f"  Reason: {result.stderr[:100]}")
        
        # Test validation
        print("\nTesting output validation...")
        validation = sandbox.validate_output(
            "Some output",
            {"max_length": 10, "required_patterns": ["xyz"]}
        )
        print(f"  Valid: {validation['valid']}")
        print(f"  Violations: {validation['violations']}")
    
    asyncio.run(test())

