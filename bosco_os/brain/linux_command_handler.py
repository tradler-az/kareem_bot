"""
Bosco Core - Linux Command Handler
Processes Linux-specific commands and integrates with Kali control
"""

import re
from typing import Dict, Any, Optional, Tuple

# Import Kali control
try:
    from bosco_os.capabilities.system.kali_control import get_kali_control
    KALI_CONTROL_AVAILABLE = True
except ImportError:
    KALI_CONTROL_AVAILABLE = False


class LinuxCommandHandler:
    """
    Handles Linux-specific commands
    Maps natural language to system operations
    """
    
    def __init__(self):
        self.kali = get_kali_control() if KALI_CONTROL_AVAILABLE else None
        self.last_result = ""
        
        # Command patterns mapping
        self.command_patterns = {
            # System Info
            r'(?:check|show|get|display) (?:my |the )?system (?:info|information|status)': self.handle_system_info,
            r'(?:check|show|get|display) (?:my |the )?cpu': self.handle_cpu,
            r'(?:check|show|get|display) (?:my |the )?(?:ram|memory|ram usage)': self.handle_memory,
            r'(?:check|show|get|display) (?:my |the )?disk': self.handle_disk,
            r'(?:check|show|get|display) (?:my |the )?(?:disk )?usage': self.handle_disk_usage,
            
            # Process Management
            r'(?:list|show|display) (?:the )?processes': self.handle_list_processes,
            r'(?:list|show|display) top processes': self.handle_list_processes,
            r'find process\s+(.+)': self.handle_find_process,
            r'kill process\s+(\d+)': self.handle_kill_process,
            
            # Network
            r'(?:check|show|get|display) (?:my |the )?network': self.handle_network_info,
            r'(?:check|show|display) (?:listening |open )?ports': self.handle_listening_ports,
            r'(?:check|show|display) connections': self.handle_connections,
            r'nmap scan\s+(.+)': self.handle_nmap_scan,
            
            # Services
            r'(?:list|show|display) (?:the )?services': self.handle_list_services,
            r'(?:start|stop|restart|enable|disable) service\s+(.+)': self.handle_service_control,
            r'service\s+status\s+(.+)': self.handle_service_status,
            
            # Packages
            r'check package\s+(.+)': self.handle_check_package,
            r'(?:list|show|display) (?:installed )?packages': self.handle_list_packages,
            r'apt update': self.handle_apt_update,
            r'apt upgrade': self.handle_apt_upgrade,
            
            # Users & Groups
            r'(?:list|show|display) (?:the )?users': self.handle_list_users,
            r'(?:list|show|display) (?:the )?groups': self.handle_list_groups,
            
            # Firewall
            r'(?:check|show|display) (?:the )?iptables': self.handle_iptables,
            r'(?:check|show|display) (?:the )?ufw': self.handle_ufw,
            
            # Logs
            r'(?:check|show|display) (?:the )?(?:system )?logs': self.handle_system_logs,
            r'(?:check|show|display) (?:the )?(?:kernel )?dmesg': self.handle_dmesg,
            r'(?:check|show|display) (?:the )?auth(?:entication)? logs': self.handle_auth_logs,
            
            # Kali specific
            r'(?:check|show|display) (?:my |the )?(?:root|root access|privileges)': self.handle_check_root,
            r'(?:list|show|display) (?:the )?kali tools': self.handle_kali_tools,
            
            # File operations
            r'find large files': self.handle_large_files,
            r'file (?:info|permissions)\s+(.+)': self.handle_file_info,
            r'(?:check|show|display) mount(?:s|points)': self.handle_mount_points,
            
            # Quick commands
            r'run\s+(.+)': self.handle_run_command,
            r'execute\s+(.+)': self.handle_run_command,
            r'sudo\s+(.+)': self.handle_run_command,
            
            # Disk
            r'(?:check|show|display) (?:the )?mounts': self.handle_mount_points,
            
            # I/O
            r'(?:check|show|display) (?:the )?io': self.handle_io_stats,
        }
    
    def process(self, user_input: str) -> Tuple[Optional[str], float]:
        """
        Process user input and return (response, confidence)
        """
        user_input = user_input.lower().strip()
        
        # Try to match patterns
        for pattern, handler in self.command_patterns.items():
            match = re.search(pattern, user_input)
            if match:
                try:
                    # Extract capture groups
                    groups = match.groups()
                    if groups:
                        result = handler(*groups)
                    else:
                        result = handler()
                    
                    if result:
                        self.last_result = result
                        return result, 0.9
                except Exception as e:
                    return f"Error executing command: {str(e)}", 0.8
        
        # Check for simple keyword matches
        return self.handle_keyword_match(user_input)
    
    def handle_keyword_match(self, text: str) -> Tuple[Optional[str], float]:
        """Handle simple keyword matches"""
        
        keywords = {
            'system info': (self.handle_system_info, 0.7),
            'cpu': (self.handle_cpu, 0.6),
            'memory': (self.handle_memory, 0.6),
            'disk': (self.handle_disk, 0.6),
            'processes': (self.handle_list_processes, 0.7),
            'network': (self.handle_network_info, 0.7),
            'ports': (self.handle_listening_ports, 0.7),
            'services': (self.handle_list_services, 0.7),
            'packages': (self.handle_list_packages, 0.7),
            'users': (self.handle_list_users, 0.7),
            'groups': (self.handle_list_groups, 0.7),
            'iptables': (self.handle_iptables, 0.7),
            'ufw': (self.handle_ufw, 0.7),
            'logs': (self.handle_system_logs, 0.7),
            'dmesg': (self.handle_dmesg, 0.7),
            'root': (self.handle_check_root, 0.7),
            'kali tools': (self.handle_kali_tools, 0.8),
            'mounts': (self.handle_mount_points, 0.7),
        }
        
        for keyword, (handler, confidence) in keywords.items():
            if keyword in text:
                try:
                    result = handler()
                    if result:
                        return result, confidence
                except:
                    pass
        
        return None, 0.0
    
    # ============ Handlers ============
    
    def handle_system_info(self) -> str:
        """Get comprehensive system info"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.get_system_info()
    
    def handle_cpu(self) -> str:
        """Get CPU info"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.cpu_info()
    
    def handle_memory(self) -> str:
        """Get memory info"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.memory_info()
    
    def handle_disk(self) -> str:
        """Get disk info"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.disk_usage()
    
    def handle_disk_usage(self) -> str:
        """Get disk usage"""
        return self.handle_disk()
    
    def handle_list_processes(self) -> str:
        """List processes"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.list_processes(top=15)
    
    def handle_find_process(self, name: str) -> str:
        """Find process by name"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.find_process(name)
    
    def handle_kill_process(self, pid: str) -> str:
        """Kill process by PID"""
        if not self.kali:
            return "Kali control module not available"
        try:
            return self.kali.kill_process(int(pid))
        except ValueError:
            return f"Invalid PID: {pid}"
    
    def handle_network_info(self) -> str:
        """Get network info"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.get_network_info()
    
    def handle_listening_ports(self) -> str:
        """Get listening ports"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.check_listening_ports()
    
    def handle_connections(self) -> str:
        """Get network connections"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.get_connections()
    
    def handle_nmap_scan(self, target: str) -> str:
        """Run nmap scan"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.run_nmap_scan(target)
    
    def handle_list_services(self) -> str:
        """List services"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.list_services()
    
    def handle_service_control(self, name: str) -> str:
        """Control a service"""
        if not self.kali:
            return "Kali control module not available"
        # Extract action from the name
        parts = name.split()
        if len(parts) >= 2:
            action = parts[0]
            service = ' '.join(parts[1:])
            return self.kali.service_control(action, service)
        return "Please specify service name: start service <name>"
    
    def handle_service_status(self, name: str) -> str:
        """Get service status"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.service_control('status', name)
    
    def handle_check_package(self, name: str) -> str:
        """Check if package is installed"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.check_package(name)
    
    def handle_list_packages(self) -> str:
        """List installed packages"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.list_installed_packages()
    
    def handle_apt_update(self) -> str:
        """Run apt update"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.apt_update()
    
    def handle_apt_upgrade(self) -> str:
        """Run apt upgrade"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.apt_upgrade()
    
    def handle_list_users(self) -> str:
        """List system users"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.list_users()
    
    def handle_list_groups(self) -> str:
        """List system groups"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.list_groups()
    
    def handle_iptables(self) -> str:
        """Check iptables"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.iptables_status()
    
    def handle_ufw(self) -> str:
        """Check UFW status"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.ufw_status()
    
    def handle_system_logs(self) -> str:
        """Get system logs"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.system_logs()
    
    def handle_dmesg(self) -> str:
        """Get kernel logs"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.dmesg_logs()
    
    def handle_auth_logs(self) -> str:
        """Get auth logs"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.auth_logs()
    
    def handle_check_root(self) -> str:
        """Check if running as root"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.check_root()
    
    def handle_kali_tools(self) -> str:
        """Get Kali tools status"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.get_kali_tools()
    
    def handle_large_files(self) -> str:
        """Find large files"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.find_large_files()
    
    def handle_file_info(self, path: str) -> str:
        """Get file info"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.file_permissions(path)
    
    def handle_mount_points(self) -> str:
        """Get mount points"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.mount_points()
    
    def handle_io_stats(self) -> str:
        """Get I/O stats"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.io_stats()
    
    def handle_run_command(self, command: str) -> str:
        """Run custom command"""
        if not self.kali:
            return "Kali control module not available"
        return self.kali.execute_command(command)


# Global handler
_linux_handler = None

def get_linux_handler() -> LinuxCommandHandler:
    """Get Linux command handler"""
    global _linux_handler
    if _linux_handler is None:
        _linux_handler = LinuxCommandHandler()
    return _linux_handler


def process_linux_command(user_input: str) -> Tuple[Optional[str], float]:
    """Process a Linux command"""
    return get_linux_handler().process(user_input)


if __name__ == "__main__":
    # Test the handler
    handler = LinuxCommandHandler()
    
    test_inputs = [
        "check system info",
        "list processes",
        "check memory",
        "show network",
        "listening ports",
        "list services",
        "check root",
        "list kali tools",
        "disk usage",
    ]
    
    print("=== Linux Command Handler Test ===\n")
    for inp in test_inputs:
        result, conf = handler.process(inp)
        print(f"Input: {inp}")
        print(f"  Confidence: {conf:.2f}")
        if result:
            print(f"  Result: {result[:100]}...")
        print()

