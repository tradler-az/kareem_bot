"""
Bosco Core - Root Manager
Full root/sudo permissions handling with password caching
"""

import os
import subprocess
import time
import getpass
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta


class RootManager:
    """
    Manages root permissions and sudo operations
    """

    def __init__(self):
        self.sudo_password = None
        self.sudo_timestamp = None
        self.sudo_timeout = 600  # 10 minutes cache
        self.is_root = os.geteuid() == 0
        self.session_start = datetime.now()
        self.command_history = []
        
    def set_sudo_password(self, password: str) -> str:
        """Cache sudo password for session"""
        # Test password first
        test_cmd = f"echo '{password}' | sudo -S -k true"
        try:
            result = subprocess.run(
                test_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.sudo_password = password
                self.sudo_timestamp = time.time()
                return "✅ Sudo password cached successfully for this session"
            else:
                return "❌ Invalid sudo password"
        except Exception as e:
            return f"❌ Error verifying password: {str(e)}"
    
    def is_sudo_valid(self) -> bool:
        """Check if cached sudo is still valid"""
        if not self.sudo_password or not self.sudo_timestamp:
            return False
        return (time.time() - self.sudo_timestamp) < self.sudo_timeout
    
    def clear_sudo(self):
        """Clear cached sudo password"""
        self.sudo_password = None
        self.sudo_timestamp = None
    
    def _build_sudo_command(self, command: str) -> str:
        """Build sudo command with cached password"""
        if not self.is_sudo_valid():
            raise PermissionError("No valid sudo password cached")
        return f"echo '{self.sudo_password}' | sudo -S -k {command}"
    
    def run_sudo(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Run command with sudo privileges
        
        Args:
            command: Command to run as sudo
            timeout: Command timeout in seconds
            
        Returns:
            Dict with success, output, error
        """
        if not self.is_sudo_valid():
            return {
                'success': False,
                'error': 'No sudo password cached. Say "cache sudo password" first.',
                'output': ''
            }
        
        # Add command to history
        self.command_history.append({
            'command': command,
            'timestamp': datetime.now(),
            'mode': 'sudo'
        })
        
        try:
            sudo_cmd = self._build_sudo_command(command)
            result = subprocess.run(
                sudo_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Command timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
    
    def run_as_root(self, command: str, timeout: int = 60) -> str:
        """Run command as root and return output"""
        result = self.run_sudo(command, timeout)
        if result['success']:
            return result['output'] or "Command executed successfully"
        return f"Error: {result.get('error', 'Unknown error')}"

    # === SYSTEM OPERATIONS WITH SUDO ===
    
    def apt_update(self) -> str:
        """Update package lists"""
        return self.run_as_root("apt update")
    
    def apt_upgrade(self) -> str:
        """Upgrade all packages"""
        return self.run_as_root("DEBIAN_FRONTEND=noninteractive apt upgrade -y")
    
    def apt_install(self, package: str) -> str:
        """Install a package"""
        return self.run_as_root(f"DEBIAN_FRONTEND=noninteractive apt install -y {package}")
    
    def apt_remove(self, package: str) -> str:
        """Remove a package"""
        return self.run_as_root(f"apt remove -y {package}")
    
    def system_reboot(self) -> str:
        """Reboot the system"""
        result = self.run_as_root("reboot")
        return "System rebooting..." if result else result
    
    def system_shutdown(self) -> str:
        """Shutdown the system"""
        result = self.run_as_root("shutdown now")
        return "System shutting down..." if result else result
    
    def restart_service(self, service: str) -> str:
        """Restart a system service"""
        return self.run_as_root(f"systemctl restart {service}")
    
    def stop_service(self, service: str) -> str:
        """Stop a system service"""
        return self.run_as_root(f"systemctl stop {service}")
    
    def start_service(self, service: str) -> str:
        """Start a system service"""
        return self.run_as_root(f"systemctl start {service}")
    
    def enable_service(self, service: str) -> str:
        """Enable a service to start on boot"""
        return self.run_as_root(f"systemctl enable {service}")
    
    def disable_service(self, service: str) -> str:
        """Disable a service"""
        return self.run_as_root(f"systemctl disable {service}")
    
    def check_service_status(self, service: str) -> str:
        """Check service status"""
        return self.run_as_root(f"systemctl status {service}")
    
    def get_system_logs(self, lines: int = 50) -> str:
        """Get system logs"""
        return self.run_as_root(f"journalctl -n {lines}")
    
    def kill_process(self, pid: int) -> str:
        """Kill a process"""
        return self.run_as_root(f"kill -9 {pid}")
    
    def killall(self, process_name: str) -> str:
        """Kill all processes by name"""
        return self.run_as_root(f"killall -9 {process_name}")
    
    def chmod(self, permissions: str, path: str) -> str:
        """Change file permissions"""
        return self.run_as_root(f"chmod {permissions} {path}")
    
    def chown(self, owner: str, path: str) -> str:
        """Change file owner"""
        return self.run_as_root(f"chown {owner} {path}")
    
    def mount_device(self, device: str, mount_point: str) -> str:
        """Mount a device"""
        return self.run_as_root(f"mount {device} {mount_point}")
    
    def unmount_device(self, mount_point: str) -> str:
        """Unmount a device"""
        return self.run_as_root(f"umount {mount_point}")
    
    # === FIREWALL COMMANDS ===
    
    def ufw_status(self) -> str:
        """Get UFW firewall status"""
        return self.run_as_root("ufw status")
    
    def ufw_enable(self) -> str:
        """Enable UFW firewall"""
        return self.run_as_root("ufw enable")
    
    def ufw_disable(self) -> str:
        """Disable UFW firewall"""
        return self.run_as_root("ufw disable")
    
    def ufw_allow(self, port: str) -> str:
        """Allow a port"""
        return self.run_as_root(f"ufw allow {port}")
    
    def ufw_deny(self, port: str) -> str:
        """Deny a port"""
        return self.run_as_root(f"ufw deny {port}")
    
    # === USER MANAGEMENT ===
    
    def add_user(self, username: str) -> str:
        """Add a new user"""
        return self.run_as_root(f"useradd -m {username}")
    
    def delete_user(self, username: str) -> str:
        """Delete a user"""
        return self.run_as_root(f"userdel -r {username}")
    
    def add_group(self, groupname: str) -> str:
        """Add a new group"""
        return self.run_as_root(f"groupadd {groupname}")
    
    def list_users(self) -> str:
        """List all users"""
        return self.run_as_root("cat /etc/passwd | cut -d: -1")
    
    def list_groups(self) -> str:
        """List all groups"""
        return self.run_as_root("cat /etc/group | cut -d: -1")
    
    # === DISK OPERATIONS ===
    
    def format_disk(self, device: str, fs_type: str = 'ext4') -> str:
        """Format a disk"""
        return self.run_as_root(f"mkfs.{fs_type} {device}")
    
    def create_partition(self, device: str) -> str:
        """Create partition table"""
        return self.run_as_root(f"parted -s {device} mklabel msdos")
    
    # === NETWORK OPERATIONS ===
    
    def restart_network(self) -> str:
        """Restart network service"""
        return self.run_as_root("systemctl restart NetworkManager")
    
    def flush_dns(self) -> str:
        """Flush DNS cache"""
        return self.run_as_root("systemd-resolve --flush-caches")
    
    # === STATUS METHODS ===
    
    def get_status(self) -> Dict[str, Any]:
        """Get root manager status"""
        return {
            'is_root': self.is_root,
            'sudo_valid': self.is_sudo_valid(),
            'session_duration': str(datetime.now() - self.session_start),
            'commands_executed': len(self.command_history),
            'sudo_timeout': self.sudo_timeout
        }
    
    def get_history(self) -> str:
        """Get command history"""
        if not self.command_history:
            return "No commands executed in this session"
        
        result = "Sudo Command History:\n\n"
        for i, entry in enumerate(self.command_history[-20:], 1):
            result += f"{i}. {entry['command']} ({entry['timestamp'].strftime('%H:%M:%S')})\n"
        
        return result


# Global instance
_root_manager = None

def get_root_manager() -> RootManager:
    """Get root manager instance"""
    global _root_manager
    if _root_manager is None:
        _root_manager = RootManager()
    return _root_manager


# Convenience functions
def sudo_run(command: str, timeout: int = 60) -> Dict[str, Any]:
    """Run command with sudo"""
    return get_root_manager().run_sudo(command, timeout)

def sudo_exec(command: str) -> str:
    """Run command as root"""
    return get_root_manager().run_as_root(command)

def cache_sudo(password: str) -> str:
    """Cache sudo password"""
    return get_root_manager().set_sudo_password(password)

def clear_sudo():
    """Clear sudo cache"""
    get_root_manager().clear_sudo()

def get_root_status() -> Dict[str, Any]:
    """Get root status"""
    return get_root_manager().get_status()


if __name__ == "__main__":
    print("=== Root Manager Test ===\n")
    
    rm = get_root_manager()
    print(f"Running as root: {rm.is_root}")
    print(f"Sudo valid: {rm.is_sudo_valid()}")
    print(f"Status: {rm.get_status()}")

