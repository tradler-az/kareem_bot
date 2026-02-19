"""
Bosco Core - Self-Update & Auto-Upgrade System
Enables Bosco to update itself, install dependencies, and improve during operation
"""

import os
import sys
import subprocess
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import threading


class UpdateSource:
    """Defines a source for updates"""
    def __init__(self, name: str, path: str, update_type: str = "git"):
        self.name = name
        self.path = path
        self.update_type = update_type  # git, pip, file


class SelfUpdateManager:
    """
    Manages self-update and auto-upgrade capabilities
    Allows Bosco to update itself during operation
    """
    
    # Default update sources
    DEFAULT_SOURCES = [
        UpdateSource("PyPI", "bosco-core", "pip"),
        UpdateSource("GitHub", "https://github.com/tradler-az/kareem-bot", "git"),
    ]
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.update_sources = self.DEFAULT_SOURCES.copy()
        
        # Track versions
        self.current_version = self._get_current_version()
        self.last_check = None
        self.update_history: List[Dict] = []
        
        # Auto-update settings
        self.auto_update_enabled = False
        self.auto_install_missing = True
        self.backup_before_update = True
        
        print(f"[SelfUpdate] Current version: {self.current_version}")
    
    def _get_current_version(self) -> str:
        """Get current Bosco version"""
        version_file = self.project_root / "VERSION"
        
        if version_file.exists():
            try:
                return version_file.read_text().strip()
            except:
                pass
        
        # Check setup.py or pyproject.toml
        setup_file = self.project_root / "setup.py"
        if setup_file.exists():
            content = setup_file.read_text()
            version_match = __import__('re').search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if version_match:
                return version_match.group(1)
        
        return "0.0.0"
    
    def check_for_updates(self, source_name: str = "PyPI") -> Dict[str, Any]:
        """Check if updates are available"""
        self.last_check = datetime.now()
        
        if source_name == "PyPI":
            return self._check_pypi_updates()
        elif source_name == "GitHub":
            return self._check_github_updates()
        else:
            return {"available": False, "error": "Unknown source"}
    
    def _check_pypi_updates(self) -> Dict[str, Any]:
        """Check PyPI for updates"""
        try:
            # Get latest version from PyPI
            result = subprocess.run(
                [sys.executable, "-m", "pip", "index", "versions", "bosco-core"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout
                # Parse version from output
                version_match = __import__('re').search(r'versions?:\s*([^)]+)', output)
                if version_match:
                    latest = version_match.group(1).strip().split()[-1]
                    return {
                        "available": latest != self.current_version,
                        "current": self.current_version,
                        "latest": latest,
                        "source": "PyPI"
                    }
            
            return {"available": False, "error": "Could not check PyPI"}
        
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def _check_github_updates(self) -> Dict[str, Any]:
        """Check GitHub for updates"""
        # This would require GitHub API access
        return {"available": False, "error": "GitHub API not configured"}
    
    def install_missing_dependencies(self, requirements_file: str = "requirements.txt") -> Dict[str, Any]:
        """Auto-install missing dependencies"""
        req_path = self.project_root / requirements_file
        
        if not req_path.exists():
            return {"success": False, "error": "requirements.txt not found"}
        
        try:
            # Parse requirements
            requirements = []
            for line in req_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name
                    pkg = line.split('>=')[0].split('==')[0].split('<')[0].strip()
                    requirements.append(pkg)
            
            # Check which are missing
            missing = []
            for pkg in requirements:
                result = subprocess.run(
                    [sys.executable, "-c", f"import {pkg.replace('-', '_')}"],
                    capture_output=True,
                    timeout=10
                )
                if result.returncode != 0:
                    missing.append(pkg)
            
            if not missing:
                return {
                    "success": True,
                    "message": "All dependencies satisfied",
                    "installed": []
                }
            
            # Install missing
            if self.auto_install_missing:
                print(f"[SelfUpdate] Installing missing packages: {missing}")
                
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install"] + missing,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                return {
                    "success": result.returncode == 0,
                    "installed": missing,
                    "output": result.stdout[-500:] if result.stdout else result.stderr[-500:]
                }
            else:
                return {
                    "success": True,
                    "message": "Missing packages found but auto-install disabled",
                    "missing": missing
                }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_from_git(self, branch: str = "main") -> Dict[str, Any]:
        """Update from Git repository"""
        git_dir = self.project_root / ".git"
        
        if not git_dir.exists():
            return {"success": False, "error": "Not a git repository"}
        
        try:
            # Check for changes
            result = subprocess.run(
                ["git", "fetch", "--dry-run"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                # Pull updates
                if self.backup_before_update:
                    self._create_backup()
                
                result = subprocess.run(
                    ["git", "pull", "origin", branch],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                success = result.returncode == 0
                
                if success:
                    self._record_update("git", branch)
                
                return {
                    "success": success,
                    "output": result.stdout,
                    "type": "git"
                }
            else:
                return {
                    "success": True,
                    "message": "Already up to date",
                    "type": "git"
                }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def upgrade_pip_packages(self, packages: List[str] = None) -> Dict[str, Any]:
        """Upgrade pip packages"""
        try:
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
            
            if packages:
                cmd.extend(packages)
            else:
                cmd.extend(["--upgrade", "-r", "requirements.txt"])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            
            if success:
                self._record_update("pip_upgrade", str(packages) if packages else "all")
            
            return {
                "success": success,
                "output": result.stdout[-1000:] if result.stdout else "",
                "error": result.stderr[-500:] if result.stderr else ""
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def apply_code_fixes(self, fixes: Dict[str, str]) -> Dict[str, Any]:
        """
        Apply automatic code fixes
        fixes: {filename: "patch content" or "instruction"}
        """
        results = []
        
        for filepath, fix_content in fixes.items():
            try:
                full_path = self.project_root / filepath
                
                if not full_path.exists():
                    results.append({
                        "file": filepath,
                        "success": False,
                        "error": "File not found"
                    })
                    continue
                
                # Create backup
                if self.backup_before_update:
                    backup_path = full_path.with_suffix(full_path.suffix + '.bak')
                    backup_path.write_bytes(full_path.read_bytes())
                
                # Apply fix
                if fix_content.startswith("PATCH:"):
                    # Apply patch
                    patch_content = fix_content[6:].strip()
                    original = full_path.read_text()
                    # Simple replace (in production, use proper diff)
                    full_path.write_text(original + "\n" + patch_content)
                else:
                    # Execute as Python code
                    exec(fix_content)
                
                results.append({
                    "file": filepath,
                    "success": True
                })
                
            except Exception as e:
                results.append({
                    "file": filepath,
                    "success": False,
                    "error": str(e)
                })
        
        all_success = all(r["success"] for r in results)
        
        if all_success:
            self._record_update("code_fixes", str(fixes.keys()))
        
        return {
            "success": all_success,
            "results": results
        }
    
    def learn_and_improve(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Learn from feedback and improve
        feedback: {type, description, suggestion, code_change}
        """
        improvement_log = self.project_root / "improvements.log"
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            **feedback
        }
        
        # Log the improvement
        with open(improvement_log, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        # Apply code change if provided
        if "code_change" in feedback:
            return self.apply_code_fixes(feedback["code_change"])
        
        return {
            "success": True,
            "message": "Improvement logged for future reference"
        }
    
    def _create_backup(self) -> str:
        """Create backup before update"""
        backup_dir = self.project_root / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = backup_dir / backup_name
        
        # Create tar archive
        result = subprocess.run(
            ["tar", "-czf", str(backup_path), "-C", str(self.project_root.parent), 
             self.project_root.name, "--exclude=.git", "--exclude=__pycache__"],
            capture_output=True
        )
        
        return str(backup_path) if result.returncode == 0 else ""
    
    def _record_update(self, update_type: str, details: str):
        """Record update in history"""
        self.update_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": update_type,
            "details": details,
            "version": self.current_version
        })
    
    def get_status(self) -> Dict[str, Any]:
        """Get current update status"""
        return {
            "current_version": self.current_version,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "auto_update_enabled": self.auto_update_enabled,
            "update_history": self.update_history[-10:],
            "backup_enabled": self.backup_before_update
        }
    
    def enable_auto_update(self, enabled: bool = True):
        """Enable or disable auto-update"""
        self.auto_update_enabled = enabled
        print(f"[SelfUpdate] Auto-update: {'enabled' if enabled else 'disabled'}")
    
    def restore_backup(self, backup_path: str) -> Dict[str, Any]:
        """Restore from backup"""
        try:
            if self.backup_before_update:
                # Extract backup
                result = subprocess.run(
                    ["tar", "-xzf", backup_path, "-C", str(self.project_root.parent)],
                    capture_output=True,
                    text=True
                )
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout
                }
            else:
                return {"success": False, "error": "Backup restore disabled"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}


class ContinuousLearningEngine:
    """
    Continuously learns and improves from interactions
    """
    
    def __init__(self, update_manager: SelfUpdateManager):
        self.update_manager = update_manager
        self.learning_data: List[Dict] = []
        self.improvement_threshold = 10  # Apply improvements after this many learnings
    
    def record_interaction(
        self,
        user_input: str,
        response: str,
        success: bool,
        feedback: str = None
    ):
        """Record interaction for learning"""
        self.learning_data.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "response": response,
            "success": success,
            "feedback": feedback
        })
        
        # Periodically analyze and improve
        if len(self.learning_data) >= self.improvement_threshold:
            self._analyze_and_improve()
    
    def _analyze_and_improve(self):
        """Analyze interactions and suggest improvements"""
        # Find patterns in failed interactions
        failed = [d for d in self.learning_data if not d["success"]]
        
        if failed:
            # Log pattern for analysis
            pattern_file = self.project_root / "failure_patterns.json"
            existing = []
            if pattern_file.exists():
                existing = json.loads(pattern_file.read_text())
            
            existing.extend(failed)
            pattern_file.write_text(json.dumps(existing[-100:], indent=2))
            
            print(f"[Learning] Logged {len(failed)} failure patterns")
        
        # Clear old data
        self.learning_data = self.learning_data[-self.improvement_threshold:]
    
    def get_learning_stats(self) -> Dict:
        """Get learning statistics"""
        return {
            "total_interactions": len(self.learning_data),
            "success_rate": sum(1 for d in self.learning_data if d["success"]) / max(len(self.learning_data), 1),
            "pending_analysis": len(self.learning_data)
        }


# Global instances
_update_manager: Optional[SelfUpdateManager] = None
_learning_engine: Optional[ContinuousLearningEngine] = None


def get_update_manager(project_root: str = None) -> SelfUpdateManager:
    """Get the update manager instance"""
    global _update_manager
    if _update_manager is None:
        _update_manager = SelfUpdateManager(project_root)
    return _update_manager


def get_learning_engine() -> ContinuousLearningEngine:
    """Get the learning engine instance"""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = ContinuousLearningEngine(get_update_manager())
    return _learning_engine


if __name__ == "__main__":
    print("=== Testing Self-Update System ===\n")
    
    # Get manager
    manager = get_update_manager()
    
    # Check status
    print("Status:")
    print(json.dumps(manager.get_status(), indent=2))
    
    # Check for updates
    print("\nChecking for updates...")
    update_info = manager.check_for_updates()
    print(f"Update available: {update_info.get('available', False)}")
    
    # Check dependencies
    print("\nChecking dependencies...")
    dep_result = manager.install_missing_dependencies()
    print(f"Dependency check: {dep_result.get('message', dep_result.get('error'))}")

