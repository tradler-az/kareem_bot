"""
Bosco Core - Kali Linux Control Module
Advanced Linux system control with Kali-specific capabilities
"""

import os
import sys
import subprocess
import platform
import socket
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class KaliLinuxControl:
    """Advanced Linux control with Kali-specific features"""
    
    def __init__(self):
        self.platform = platform.system()
        self.is_linux = self.platform == "Linux"
        self.is_kali = self._detect_kali()
        self.hostname = socket.gethostname()
        
    def _detect_kali(self) -> bool:
        """Detect if running on Kali Linux"""
        try:
            # Check os-release
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release') as f:
                    content = f.read()
                    if 'Kali' in content or 'kali' in content:
                        return True
            
            # Check for Kali-specific files
            if os.path.exists('/usr/bin/kali'):
                return True
                
            # Check kernel version for Kali indicators
            with open('/proc/version', 'r') as f:
                if 'kali' in f.read().lower():
                    return True
                    
        except:
            pass
        return False
    
    def _run_command(self, cmd: str, shell: bool = True, timeout: int = 30) -> Dict[str, Any]:
        """Run a shell command and return result"""
        try:
            result = subprocess.run(
                cmd if shell else cmd.split(),
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                'success': result.returncode == 0,
                'output': result.stdout.strip(),
                'error': result.stderr.strip(),
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'output': '', 'error': 'Command timed out', 'returncode': -1}
        except Exception as e:
            return {'success': False, 'output': '', 'error': str(e), 'returncode': -1}
    
    # ============ System Information ============
    
    def get_linux_info(self) -> Dict[str, Any]:
        """Get comprehensive Linux system information"""
        info = {
            'hostname': self.hostname,
            'kernel': os.uname().release,
            'architecture': os.uname().machine,
            'is_kali': self.is_kali,
            'distro': 'Kali Linux' if self.is_kali else 'Linux'
        }
        
        # Uptime
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                info['uptime'] = f"{days}d {hours}h {minutes}m"
        except:
            info['uptime'] = 'Unknown'
        
        # Current user
        info['current_user'] = os.environ.get('USER', 'Unknown')
        
        # Load average (Linux only)
        if self.is_linux:
            try:
                with open('/proc/loadavg', 'r') as f:
                    load = f.read().split()[:3]
                    info['load_average'] = f"{load[0]} (1m), {load[1]} (5m), {load[2]} (15m)"
            except:
                pass
        
        return info
    
    def get_system_info(self) -> str:
        """Get formatted system info"""
        info = self.get_linux_info()
        return (
            f"Host: {info['hostname']}\n"
            f"User: {info['current_user']}\n"
            f"Kernel: {info['kernel']}\n"
            f"Architecture: {info['architecture']}\n"
            f"Distribution: {info['distro']}\n"
            f"Uptime: {info.get('uptime', 'Unknown')}\n"
            f"Load Average: {info.get('load_average', 'N/A')}"
        )
    
    # ============ Process Management ============
    
    def list_processes(self, top: int = 10, sort_by: str = 'cpu') -> str:
        """List top processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username']):
            try:
                pinfo = proc.info
                processes.append(pinfo)
            except:
                pass
        
        # Sort
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        else:
            processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        
        # Format output
        result = f"Top {top} Processes (by {sort_by}):\n"
        result += f"{'PID':<8} {'USER':<15} {'CPU%':<8} {'MEM%':<8} {'NAME':<30}\n"
        result += "-" * 70 + "\n"
        
        for p in processes[:top]:
            result += f"{p['pid']:<8} {p['username'][:15]:<15} {p.get('cpu_percent', 0):<8.1f} {p.get('memory_percent', 0):<8.1f} {p['name'][:30]:<30}\n"
        
        return result
    
    def kill_process(self, pid: int, signal: int = 15) -> str:
        """Kill a process"""
        try:
            proc = psutil.Process(pid)
            proc.send_signal(signal)
            return f"Sent signal {signal} to process {pid} ({proc.name()})"
        except psutil.NoSuchProcess:
            return f"Process {pid} not found"
        except psutil.AccessDenied:
            return f"Access denied to process {pid}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def find_process(self, name: str) -> str:
        """Find processes by name"""
        result = self._run_command(f"pgrep -la {name}")
        if result['success'] and result['output']:
            return f"Processes matching '{name}':\n{result['output']}"
        return f"No processes found matching '{name}'"
    
    # ============ Network Management ============
    
    def get_network_info(self) -> str:
        """Get network configuration"""
        result = self._run_command("ip addr show")
        if not result['success']:
            result = self._run_command("ifconfig")
        
        if result['success']:
            return f"Network Interfaces:\n{result['output']}"
        return f"Could not get network info: {result['error']}"
    
    def get_connections(self) -> str:
        """Get active network connections"""
        result = self._run_command("ss -tunap", timeout=10)
        if not result['success']:
            result = self._run_command("netstat -tunap", timeout=10)
        
        if result['success']:
            # Show first 30 lines
            lines = result['output'].split('\n')[:30]
            return "Active Network Connections:\n" + '\n'.join(lines)
        return f"Could not get connections: {result['error']}"
    
    def check_listening_ports(self) -> str:
        """Check listening ports"""
        result = self._run_command("ss -tulnp")
        if result['success']:
            lines = result['output'].split('\n')
            return "Listening Ports:\n" + '\n'.join(lines[:20])
        return f"Could not get ports: {result['error']}"
    
    # ============ Service Management ============
    
    def list_services(self) -> str:
        """List system services"""
        result = self._run_command("systemctl list-units --type=service --state=running")
        if result['success']:
            return f"Active Services:\n{result['output']}"
        return f"Could not list services: {result['error']}"
    
    def service_control(self, action: str, service: str) -> str:
        """Control a service (start, stop, restart, status)"""
        if action not in ['start', 'stop', 'restart', 'status', 'enable', 'disable']:
            return f"Invalid action: {action}"
        
        result = self._run_command(f"sudo systemctl {action} {service}")
        if result['success']:
            return f"Service {service} {action}ed successfully"
        return f"Failed to {action} {service}: {result['error']}"
    
    # ============ Package Management ============
    
    def check_package(self, package: str) -> str:
        """Check if a package is installed"""
        result = self._run_command(f"dpkg -l {package}")
        if result['success'] and result['output']:
            lines = result['output'].split('\n')
            if len(lines) > 2 and 'ii' in lines[2]:
                return f"Package '{package}' is installed"
        return f"Package '{package}' is NOT installed"
    
    def list_installed_packages(self, search: str = "") -> str:
        """List installed packages"""
        if search:
            result = self._run_command(f"dpkg -l | grep -i {search}")
        else:
            result = self._run_command("dpkg -l | head -50")
        
        if result['success']:
            return f"Installed Packages:\n{result['output']}"
        return f"Could not list packages: {result['error']}"
    
    def apt_update(self) -> str:
        """Run apt update"""
        result = self._run_command("sudo apt update", timeout=120)
        if result['success']:
            return "APT package lists updated successfully"
        return f"Failed to update: {result['error']}"
    
    def apt_upgrade(self) -> str:
        """Run apt upgrade"""
        result = self._run_command("sudo apt upgrade -y", timeout=300)
        if result['success']:
            return "System upgraded successfully"
        return f"Failed to upgrade: {result['error']}"
    
    # ============ User Management ============
    
    def list_users(self) -> str:
        """List system users"""
        result = self._run_command("cat /etc/passwd | grep -v nologin | grep -v false | cut -d: -f1,3,5")
        if result['success']:
            return f"System Users:\n{result['output']}"
        return f"Could not list users: {result['error']}"
    
    def list_groups(self) -> str:
        """List system groups"""
        result = self._run_command("getent group | cut -d: -f1")
        if result['success']:
            return f"System Groups:\n{result['output']}"
        return f"Could not list groups: {result['error']}"
    
    # ============ Firewall ============
    
    def iptables_status(self) -> str:
        """Check iptables status"""
        result = self._run_command("sudo iptables -L -n -v")
        if result['success']:
            return f"IPTables Rules:\n{result['output']}"
        return f"Could not get iptables: {result['error']}"
    
    def ufw_status(self) -> str:
        """Check UFW status"""
        result = self._run_command("sudo ufw status verbose")
        if result['success']:
            return f"UFW Status:\n{result['output']}"
        return f"UFW not installed or not configured"
    
    # ============ Logs ============
    
    def system_logs(self, lines: int = 50, service: str = "") -> str:
        """Get system logs"""
        if service:
            result = self._run_command(f"journalctl -u {service} -n {lines}")
        else:
            result = self._run_command(f"journalctl -n {lines}")
        
        if result['success']:
            return f"System Logs (last {lines} lines):\n{result['output']}"
        return f"Could not get logs: {result['error']}"
    
    def dmesg_logs(self, lines: int = 30) -> str:
        """Get kernel messages"""
        result = self._run_command(f"dmesg | tail -{lines}")
        if result['success']:
            return f"Kernel Messages:\n{result['output']}"
        return f"Could not get dmesg: {result['error']}"
    
    def auth_logs(self, lines: int = 30) -> str:
        """Get authentication logs"""
        result = self._run_command(f"sudo tail -{lines} /var/log/auth.log")
        if not result['success']:
            result = self._run_command(f"journalctl -u ssh -n {lines}")
        if result['success']:
            return f"Auth Logs:\n{result['output']}"
        return f"Could not get auth logs: {result['error']}"
    
    # ============ Disk & Filesystem ============
    
    def disk_usage(self) -> str:
        """Get disk usage"""
        result = self._run_command("df -h")
        if result['success']:
            return f"Disk Usage:\n{result['output']}"
        return f"Could not get disk usage: {result['error']}"
    
    def mount_points(self) -> str:
        """Get mount points"""
        result = self._run_command("mount | column -t")
        if result['success']:
            return f"Mount Points:\n{result['output']}"
        return f"Could not get mounts: {result['error']}"
    
    # ============ Kali Linux Specific ============
    
    def get_kali_tools(self) -> str:
        """Get list of common Kali Linux tools"""
        tools = {
            'Information Gathering': ['nmap', 'netdiscover', 'arp-scan', 'dnsenum', 'fierce'],
            'Vulnerability Analysis': ['nikto', 'openvas', 'sqlmap', 'commix'],
            'Exploitation Tools': ['msfconsole', 'searchsploit', 'empire', 'metasploit'],
            'Wireless Attacks': ['aircrack-ng', 'wifite', 'reaver', ' bully'],
            'Forensics': ['foremost', 'binwalk', 'volatility', 'autopsy'],
            'Password Attacks': ['hydra', 'john', 'hashcat', 'cupp'],
            'Reverse Engineering': ['radare2', 'ghidra', 'ida', 'objdump'],
            'Sniffing & Spoofing': ['ettercap', 'wireshark', 'tcpdump', 'dsniff'],
            'Web Applications': ['burpsuite', 'zap', 'dirb', 'gobuster'],
            'Post Exploitation': ['mimikatz', 'privilege-escalation', 'persistence']
        }
        
        result = "Kali Linux Tools Status:\n\n"
        for category, tool_list in tools.items():
            result += f"\n{category}:\n"
            for tool in tool_list:
                check = self._run_command(f"which {tool}")
                status = "✓ Installed" if check['success'] else "✗ Not found"
                result += f"  {tool}: {status}\n"
        
        return result
    
    def check_root(self) -> str:
        """Check if running as root"""
        import os
        if os.geteuid() == 0:
            return "⚠️ Running as ROOT user"
        return "Running as regular user (not root)"
    
    def run_nmap_scan(self, target: str, scan_type: str = 'basic') -> str:
        """Run nmap scan"""
        if scan_type == 'basic':
            cmd = f"nmap -sV {target}"
        elif scan_type == 'quick':
            cmd = f"nmap -F {target}"
        elif scan_type == 'stealth':
            cmd = f"nmap -sS -T stealth {target}"
        elif scan_type == 'full':
            cmd = f"nmap -A -p- {target}"
        else:
            cmd = f"nmap {target}"
        
        result = self._run_command(cmd, timeout=120)
        if result['success']:
            return f"Nmap scan results:\n{result['output']}"
        return f"Scan failed: {result['error']}"
    
    # ============ System Resources ============
    
    def memory_info(self) -> str:
        """Get detailed memory info"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return (
            f"Memory Usage:\n"
            f"  Total: {mem.total / (1024**3):.2f} GB\n"
            f"  Used: {mem.used / (1024**3):.2f} GB ({mem.percent}%)\n"
            f"  Free: {mem.available / (1024**3):.2f} GB\n"
            f"\nSwap Usage:\n"
            f"  Total: {swap.total / (1024**3):.2f} GB\n"
            f"  Used: {swap.used / (1024**3):.2f} GB ({swap.percent}%)\n"
            f"  Free: {swap.free / (1024**3):.2f} GB"
        )
    
    def cpu_info(self) -> str:
        """Get CPU information"""
        cpu = psutil.cpu_percent(interval=1, percpu=True)
        cpu_freq = psutil.cpu_freq()
        
        result = f"CPU Usage: {psutil.cpu_percent(interval=1)}%\n"
        result += f"Per-core usage: {', '.join([f'{c:.1f}%' for c in cpu])}\n"
        
        if cpu_freq:
            result += f"Frequency: {cpu_freq.current:.0f} MHz\n"
        
        result += f"CPU Count: {psutil.cpu_count()} cores\n"
        
        # CPU times
        times = psutil.cpu_times()
        result += f"User: {times.user:.1f}s, System: {times.system:.1f}s"
        
        return result
    
    def io_stats(self) -> str:
        """Get I/O statistics"""
        io = psutil.disk_io_counters()
        
        if io:
            return (
                f"I/O Statistics:\n"
                f"  Read: {io.read_bytes / (1024**2):.2f} MB\n"
                f"  Write: {io.write_bytes / (1024**2):.2f} MB\n"
                f"  Read Count: {io.read_count}\n"
                f"  Write Count: {io.write_count}"
            )
        return "Could not get I/O stats"
    
    # ============ File Operations ============
    
    def find_large_files(self, path: str = '/', size_mb: int = 100) -> str:
        """Find large files"""
        result = self._run_command(f"sudo find {path} -type f -size +{size_mb}M -exec ls -lh {{}} \\; 2>/dev/null | head -20")
        if result['success']:
            return f"Large files (>={size_mb}MB):\n{result['output']}"
        return f"Could not find files: {result['error']}"
    
    def file_permissions(self, path: str) -> str:
        """Get file permissions"""
        try:
            import stat
            st = os.stat(path)
            perms = stat.filemode(st.st_mode)
            return f"Path: {path}\nPermissions: {perms}\nOwner UID: {st.st_uid}\nGroup GID: {st.st_gid}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    # ============ Execute Custom Command ============
    
    def execute_command(self, command: str) -> str:
        """Execute a custom shell command"""
        result = self._run_command(command, timeout=60)
        if result['success']:
            return result['output'] if result['output'] else "Command executed successfully (no output)"
        return f"Error: {result['error']}"


# Global instance
_kali_control = None

def get_kali_control() -> KaliLinuxControl:
    """Get Kali Linux control instance"""
    global _kali_control
    if _kali_control is None:
        _kali_control = KaliLinuxControl()
    return _kali_control


if __name__ == "__main__":
    # Test the module
    kali = KaliLinuxControl()
    
    print("=== Kali Linux Control Test ===\n")
    print(f"Platform: {kali.platform}")
    print(f"Is Kali: {kali.is_kali}")
    print(f"Hostname: {kali.hostname}")
    print()
    
    print("--- System Info ---")
    print(kali.get_system_info())
    print()
    
    print("--- CPU Info ---")
    print(kali.cpu_info())
    print()
    
    print("--- Root Check ---")
    print(kali.check_root())
    
    if kali.is_kali:
        print("\n--- Kali Tools ---")
        print(kali.get_kali_tools())

