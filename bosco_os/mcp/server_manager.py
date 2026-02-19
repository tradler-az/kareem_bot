"""
Bosco Core - MCP Server Manager
Manages connections to external MCP servers (Google Drive, Slack, GitHub, etc.)
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import uuid


class MCPTransportType(Enum):
    """MCP transport types"""
    STDIO = "stdio"
    HTTP = "http"
    WEBSOCKET = "websocket"


class MCPServerConnection:
    """Represents a connection to an external MCP server"""
    
    def __init__(
        self,
        name: str,
        server_path: str,
        transport: MCPTransportType = MCPTransportType.STDIO,
        env: Dict = None
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.server_path = server_path
        self.transport = transport
        self.env = env or {}
        self.is_connected = False
        self.capabilities: Dict = {}
        self.tools: List[Dict] = []
        self.last_error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "server_path": self.server_path,
            "transport": self.transport.value,
            "is_connected": self.is_connected,
            "capabilities": self.capabilities,
            "tools_count": len(self.tools)
        }


class MCPServerManager:
    """
    Manages connections to external MCP servers
    Enables plug-and-play integration with the AI ecosystem
    """
    
    # Predefined server configurations
    DEFAULT_SERVERS = {
        "brave-search": {
            "name": "Brave Search",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {"BRAVE_API_KEY": ""},
            "description": "Web search using Brave Search API"
        },
        "github": {
            "name": "GitHub",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_TOKEN": ""},
            "description": "GitHub integration (issues, PRs, repos)"
        },
        "slack": {
            "name": "Slack",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-slack"],
            "env": {"SLACK_BOT_TOKEN": "", "SLACK_TEAM_ID": ""},
            "description": "Slack messaging integration"
        },
        "postgres": {
            "name": "PostgreSQL",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres"],
            "env": {"DATABASE_URL": ""},
            "description": "PostgreSQL database operations"
        },
        "google-drive": {
            "name": "Google Drive",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-google-drive"],
            "env": {"GOOGLE_application_credentials": ""},
            "description": "Google Drive file operations"
        },
        "filesystem": {
            "name": "Filesystem",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem"],
            "env": {},
            "description": "Local filesystem operations"
        }
    }
    
    def __init__(self):
        self.connections: Dict[str, MCPServerConnection] = {}
        self.tool_cache: Dict[str, List[Dict]] = {}
        self.request_history: List[Dict] = []
        
        print("[MCPServerManager] Initialized")
    
    def register_server(
        self,
        name: str,
        server_path: str,
        transport: MCPTransportType = MCPTransportType.STDIO,
        env: Dict = None
    ) -> MCPServerConnection:
        """Register a new MCP server connection"""
        conn = MCPServerConnection(name, server_path, transport, env)
        self.connections[name] = conn
        print(f"[MCPServerManager] Registered server: {name}")
        return conn
    
    def add_preset_server(self, preset_name: str, env: Dict = None) -> Optional[MCPServerConnection]:
        """Add a preset MCP server"""
        if preset_name not in self.DEFAULT_SERVERS:
            print(f"[MCPServerManager] Unknown preset: {preset_name}")
            return None
        
        preset = self.DEFAULT_SERVERS[preset_name]
        server_env = {**preset.get("env", {}), **(env or {})}
        
        return self.register_server(
            name=preset["name"],
            server_path=" ".join([preset["command"]] + preset["args"]),
            env=server_env
        )
    
    def list_servers(self) -> List[Dict]:
        """List all registered servers"""
        return [conn.to_dict() for conn in self.connections.values()]
    
    def get_tools_from_server(self, server_name: str) -> List[Dict]:
        """Get tools available from a specific server"""
        if server_name not in self.connections:
            return []
        
        conn = self.connections[server_name]
        
        # Check cache first
        if server_name in self.tool_cache:
            return self.tool_cache[server_name]
        
        # In a real implementation, this would actually connect and query
        # For now, return cached tools or empty list
        return conn.tools
    
    def get_all_tools(self) -> List[Dict]:
        """Get all tools from all connected servers"""
        all_tools = []
        
        for server_name, tools in self.tool_cache.items():
            for tool in tools:
                all_tools.append({
                    **tool,
                    "server": server_name
                })
        
        return all_tools
    
    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict = None
    ) -> Any:
        """Call a tool on a specific server"""
        if server_name not in self.connections:
            raise ValueError(f"Server not found: {server_name}")
        
        conn = self.connections[server_name]
        
        # Record the request
        request = {
            "server": server_name,
            "tool": tool_name,
            "args": arguments,
            "timestamp": datetime.now().isoformat()
        }
        self.request_history.append(request)
        
        # In a real implementation, this would:
        # 1. Start the MCP server process
        # 2. Send the JSON-RPC request
        # 3. Receive and parse the response
        
        # Simulate tool call
        print(f"[MCPServerManager] Calling {tool_name} on {server_name}")
        
        return {
            "success": True,
            "server": server_name,
            "tool": tool_name,
            "result": f"Simulated result from {tool_name}"
        }
    
    def get_server_info(self, server_name: str) -> Optional[Dict]:
        """Get information about a specific server"""
        if server_name not in self.connections:
            return None
        
        conn = self.connections[server_name]
        
        return {
            "name": conn.name,
            "id": conn.id,
            "transport": conn.transport.value,
            "capabilities": conn.capabilities,
            "tools": conn.tools,
            "is_connected": conn.is_connected,
            "last_error": conn.last_error
        }
    
    def get_presets(self) -> List[Dict]:
        """Get list of available preset servers"""
        return [
            {
                "id": key,
                "name": val["name"],
                "description": val["description"]
            }
            for key, val in self.DEFAULT_SERVERS.items()
        ]
    
    def get_stats(self) -> Dict:
        """Get manager statistics"""
        return {
            "total_servers": len(self.connections),
            "connected_servers": len([c for c in self.connections.values() if c.is_connected]),
            "total_tools": sum(len(t) for t in self.tool_cache.values()),
            "requests_made": len(self.request_history)
        }


# Global instance
_server_manager: Optional[MCPServerManager] = None


def get_mcp_server_manager() -> MCPServerManager:
    """Get the global MCP server manager"""
    global _server_manager
    if _server_manager is None:
        _server_manager = MCPServerManager()
    return _server_manager


if __name__ == "__main__":
    print("=== Testing MCP Server Manager ===\n")
    
    manager = MCPServerManager()
    
    # List presets
    print("Available presets:")
    for preset in manager.get_presets():
        print(f"  - {preset['id']}: {preset['name']}")
    
    # Add a preset server
    print("\nAdding Brave Search server...")
    manager.add_preset_server("brave-search", {"BRAVE_API_KEY": "test-key"})
    
    # List servers
    print("\nRegistered servers:")
    for server in manager.list_servers():
        print(f"  - {server['name']}: {server['server_path']}")
    
    # Get stats
    print(f"\nStats: {manager.get_stats()}")

