"""
Bosco Core - Multi-Device Support Module
Execute commands on different devices with device discovery and command forwarding
"""

import socket
import threading
import json
import os
import time
import uuid
import base64
import pickle
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict


@dataclass
class Device:
    """Device information"""
    device_id: str
    device_name: str
    ip_address: str
    port: int
    last_seen: str
    status: str = "online"
    capabilities: List[str] = None
    platform: str = "unknown"
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


class MultiDeviceManager:
    """Manage multiple devices for command execution"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.device_id = self.config.get('device_id', str(uuid.uuid4())[:8])
        self.device_name = self.config.get('device_name', 'main_pc')
        self.server_port = self.config.get('server_port', 8765)
        self.is_server = False
        self.server_socket = None
        self.known_devices: Dict[str, Device] = {}
        self.command_callbacks: Dict[str, Callable] = {}
        self._running = False
        
        # Load known devices
        self._load_devices()
    
    def _load_devices(self):
        """Load known devices from config"""
        known = self.config.get('known_devices', [])
        for d in known:
            device = Device(**d)
            self.known_devices[device.device_id] = device
    
    def _save_devices(self):
        """Save known devices to config"""
        # This would update config.json in practice
        pass
    
    def register_device(self, device: Device):
        """Register a new device"""
        self.known_devices[device.device_id] = device
        print(f"Registered device: {device.device_name} ({device.device_id})")
    
    def start_server(self):
        """Start the device server to receive commands"""
        if self.is_server:
            return
        
        self._running = True
        self.is_server = True
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.server_port))
        self.server_socket.listen(5)
        
        print(f"Device server started on port {self.server_port}")
        
        # Start accept loop in background
        threading.Thread(target=self._accept_connections, daemon=True).start()
    
    def _accept_connections(self):
        """Accept incoming connections"""
        while self._running:
            try:
                client_socket, address = self.server_socket.accept()
                threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                ).start()
            except:
                break
    
    def _handle_client(self, client_socket, address):
        """Handle incoming client connection"""
        try:
            data = client_socket.recv(4096)
            if data:
                message = json.loads(data.decode('utf-8'))
                
                if message.get('type') == 'command':
                    # Execute command locally
                    result = self._execute_command(message.get('command'), message.get('params', {}))
                    
                    # Send response
                    response = {
                        'type': 'response',
                        'status': 'success' if result else 'failed',
                        'result': result
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))
                
                elif message.get('type') == 'register':
                    # Device registration
                    device_data = message.get('device', {})
                    device = Device(
                        device_id=device_data.get('device_id', ''),
                        device_name=device_data.get('device_name', 'Unknown'),
                        ip_address=address[0],
                        port=device_data.get('port', 8765),
                        last_seen=datetime.now().isoformat(),
                        capabilities=device_data.get('capabilities', [])
                    )
                    self.register_device(device)
        
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def _execute_command(self, command: str, params: Dict) -> Any:
        """Execute a command locally"""
        # Import PC control for local execution
        try:
            from bosco_os.capabilities.system.pc_control import PCControl
            pc = PCControl()
            
            commands = {
                'open_app': lambda: pc.open_app(params.get('app_name', '')),
                'screenshot': lambda: pc.screenshot(params.get('path')),
                'type_text': lambda: pc.type_text(params.get('text', '')),
                'press_key': lambda: pc.press_key(params.get('key', '')),
                'click': lambda: pc.click(params.get('x'), params.get('y'), params.get('button', 'left')),
                'get_clipboard': lambda: pc.get_clipboard(),
                'set_clipboard': lambda: pc.set_clipboard(params.get('text', '')),
                'get_screen_size': lambda: pc.get_screen_size(),
            }
            
            if command in commands:
                return commands[command]()
            return f"Unknown command: {command}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def stop_server(self):
        """Stop the device server"""
        self._running = False
        if self.server_socket:
            self.server_socket.close()
        self.is_server = False
    
    def send_command(self, device_id: str, command: str, params: Dict = None) -> Optional[Any]:
        """Send command to a specific device"""
        if device_id not in self.known_devices:
            print(f"Unknown device: {device_id}")
            return None
        
        device = self.known_devices[device_id]
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((device.ip_address, device.port))
            
            message = {
                'type': 'command',
                'command': command,
                'params': params or {}
            }
            
            sock.send(json.dumps(message).encode('utf-8'))
            
            # Wait for response
            data = sock.recv(4096)
            response = json.loads(data.decode('utf-8'))
            
            sock.close()
            
            return response.get('result')
        
        except Exception as e:
            print(f"Error sending command: {e}")
            return None
    
    def broadcast_command(self, command: str, params: Dict = None) -> Dict[str, Any]:
        """Broadcast command to all known devices"""
        results = {}
        
        for device_id in self.known_devices:
            result = self.send_command(device_id, command, params)
            results[device_id] = result
        
        return results
    
    def discover_devices(self, timeout: float = 3.0) -> List[Device]:
        """Discover devices on local network (UDP broadcast)"""
        discovered = []
        
        # Create UDP socket for discovery
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)
        
        discovery_message = json.dumps({
            'type': 'discovery',
            'device_id': self.device_id,
            'device_name': self.device_name,
            'port': self.server_port
        })
        
        try:
            sock.sendto(discovery_message.encode('utf-8'), ('<broadcast>', 8766))
            
            while True:
                try:
                    data, address = sock.recvfrom(4096)
                    message = json.loads(data.decode('utf-8'))
                    
                    if message.get('type') == 'discovery_response':
                        device = Device(
                            device_id=message.get('device_id', ''),
                            device_name=message.get('device_name', 'Unknown'),
                            ip_address=address[0],
                            port=message.get('port', 8765),
                            last_seen=datetime.now().isoformat()
                        )
                        discovered.append(device)
                except socket.timeout:
                    break
        except Exception as e:
            print(f"Discovery error: {e}")
        finally:
            sock.close()
        
        return discovered
    
    def get_online_devices(self) -> List[Device]:
        """Get list of online devices"""
        return [d for d in self.known_devices.values() if d.status == "online"]
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        return self.known_devices.get(device_id)
    
    def remove_device(self, device_id: str) -> bool:
        """Remove a device"""
        if device_id in self.known_devices:
            del self.known_devices[device_id]
            return True
        return False
    
    def execute_on_all(self, command: str, params: Dict = None) -> str:
        """Execute command on all devices and format results"""
        results = self.broadcast_command(command, params)
        
        lines = [f"Command '{command}' executed on {len(results)} devices:"]
        for device_id, result in results.items():
            device = self.known_devices.get(device_id)
            name = device.device_name if device else device_id
            lines.append(f"  - {name}: {result}")
        
        return "\n".join(lines)
    
    def format_device_list(self) -> str:
        """Format device list as readable text"""
        if not self.known_devices:
            return "No devices registered."
        
        lines = ["🖥️ Registered Devices:", "=" * 40]
        
        for device in self.known_devices.values():
            status_icon = "🟢" if device.status == "online" else "🔴"
            lines.append(f"{status_icon} {device.device_name}")
            lines.append(f"   ID: {device.device_id}")
            lines.append(f"   IP: {device.ip_address}:{device.port}")
            if device.capabilities:
                lines.append(f"   Features: {', '.join(device.capabilities)}")
            lines.append("")
        
        return "\n".join(lines)


# Global instance
_device_manager = None


def get_device_manager(config: Dict = None) -> MultiDeviceManager:
    """Get or create the global device manager"""
    global _device_manager
    if _device_manager is None:
        # Load config
        if config is None:
            import json
            for path in ['config.json', 'bosco_os/config.json']:
                if os.path.exists(path):
                    with open(path) as f:
                        config = json.load(f)
                        config = config.get('multi_device', {})
                        break
            if config is None:
                config = {}
        
        _device_manager = MultiDeviceManager(config)
    return _device_manager


# Quick functions
def list_devices() -> str:
    """List all registered devices"""
    manager = get_device_manager()
    return manager.format_device_list()


def send_to_device(device_id: str, command: str, params: Dict = None) -> str:
    """Send command to a specific device"""
    manager = get_device_manager()
    result = manager.send_command(device_id, command, params)
    return str(result) if result is not None else "Device not found"


def discover_devices() -> str:
    """Discover devices on network"""
    manager = get_device_manager()
    devices = manager.discover_devices()
    
    if not devices:
        return "No devices discovered on the network."
    
    lines = ["🔍 Discovered Devices:", "=" * 40]
    for d in devices:
        lines.append(f"🖥️ {d.device_name} ({d.ip_address})")
        manager.register_device(d)
    
    return "\n".join(lines)


if __name__ == "__main__":
    print("Testing Multi-Device Support...")
    
    dm = get_device_manager()
    print(dm.format_device_list())
    
    # Test starting server
    dm.start_server()
    print("Server started")
    
    time.sleep(1)
    dm.stop_server()
    print("Server stopped")

