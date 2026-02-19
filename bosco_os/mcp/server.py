"""
Bosco Core - Model Context Protocol (MCP) Server
Standardizes tool interactions for professional developer integrations
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import uuid


class MCPMessageType(Enum):
    """MCP message types"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class MCPTool:
    """Represents a tool that can be called via MCP"""
    
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict,
        handler: Callable
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler


class MCPRequest:
    """Represents an MCP request"""
    
    def __init__(
        self,
        method: str,
        params: Dict = None,
        request_id: str = None
    ):
        self.method = method
        self.params = params or {}
        self.request_id = request_id or str(uuid.uuid4())
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": self.method,
            "params": self.params
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'MCPRequest':
        return MCPRequest(
            method=data.get("method", ""),
            params=data.get("params", {}),
            request_id=data.get("id")
        )


class MCPResponse:
    """Represents an MCP response"""
    
    def __init__(
        self,
        request_id: str,
        result: Any = None,
        error: Dict = None
    ):
        self.request_id = request_id
        self.result = result
        self.error = error
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        response = {
            "jsonrpc": "2.0",
            "id": self.request_id
        }
        
        if self.error:
            response["error"] = self.error
        else:
            response["result"] = self.result
        
        return response


class MCPServer:
    """
    Model Context Protocol Server
    Provides standardized tool interfaces for Bosco Core
    """
    
    def __init__(self, name: str = "bosco-core"):
        self.name = name
        self.version = "1.0.0"
        self.tools: Dict[str, MCPTool] = {}
        self.capabilities: Dict = {}
        
        # Request handlers
        self.request_handlers: Dict[str, Callable] = {}
        
        # Initialize default capabilities
        self._init_capabilities()
        
        # Register default tools
        self._register_default_tools()
        
        print(f"[MCP] Server '{name}' initialized")
    
    def _init_capabilities(self):
        """Initialize server capabilities"""
        self.capabilities = {
            "tools": {
                "supported": True,
                "listChanged": True
            },
            "resources": {
                "supported": True,
                "subscribe": True,
                "listChanged": True
            },
            "prompts": {
                "supported": True
            },
            "logging": {
                "supported": True
            }
        }
    
    def _register_default_tools(self):
        """Register default tools"""
        
        # Register tool for getting server info
        self.register_tool(MCPTool(
            name="server_info",
            description="Get information about the Bosco server",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            handler=self._handle_server_info
        ))
        
        # Register tool for listing tools
        self.register_tool(MCPTool(
            name="list_tools",
            description="List all available tools",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            handler=self._handle_list_tools
        ))
    
    def register_tool(self, tool: MCPTool):
        """Register a new tool"""
        self.tools[tool.name] = tool
        print(f"[MCP] Registered tool: {tool.name}")
    
    def unregister_tool(self, name: str):
        """Unregister a tool"""
        if name in self.tools:
            del self.tools[name]
            print(f"[MCP] Unregistered tool: {name}")
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict]:
        """List all registered tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            }
            for tool in self.tools.values()
        ]
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle an incoming MCP request"""
        
        try:
            method = request.method
            
            # Handle standard methods
            if method == "initialize":
                result = await self._handle_initialize(request.params)
            
            elif method == "tools/list":
                result = {"tools": self.list_tools()}
            
            elif method == "tools/call":
                result = await self._handle_tool_call(request.params)
            
            elif method == "resources/list":
                result = await self._handle_resources_list(request.params)
            
            elif method == "resources/read":
                result = await self._handle_resources_read(request.params)
            
            elif method == "prompts/list":
                result = await self._handle_prompts_list()
            
            elif method == "shutdown":
                result = await self._handle_shutdown()
            
            else:
                # Check custom handlers
                if method in self.request_handlers:
                    result = await self.request_handlers[method](request.params)
                else:
                    # Check if it's a tool call
                    if method in self.tools:
                        result = await self._handle_tool_call({"name": method, "arguments": request.params})
                    else:
                        raise ValueError(f"Unknown method: {method}")
            
            return MCPResponse(
                request_id=request.request_id,
                result=result
            )
        
        except Exception as e:
            return MCPResponse(
                request_id=request.request_id,
                error={
                    "code": -32603,
                    "message": str(e)
                }
            )
    
    async def handle_notification(self, notification: Dict):
        """Handle an incoming notification"""
        method = notification.get("method")
        params = notification.get("params", {})
        
        if method == "initialized":
            print("[MCP] Client initialized")
        
        elif method == "tools/list_changed":
            print("[MCP] Tools list changed")
        
        elif method == "resources/list_changed":
            print("[MCP] Resources list changed")
    
    # ============ Request Handlers ============
    
    async def _handle_initialize(self, params: Dict) -> Dict:
        """Handle initialize request"""
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": self.name,
                "version": self.version
            },
            "capabilities": self.capabilities
        }
    
    async def _handle_list_tools(self, params: Dict) -> Dict:
        """Handle tools/list request"""
        return {"tools": self.list_tools()}
    
    async def _handle_tool_call(self, params: Dict) -> Dict:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        # Call the tool handler
        result = await tool.handler(arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)
                }
            ]
        }
    
    async def _handle_resources_list(self, params: Dict) -> Dict:
        """Handle resources/list request"""
        # Return available resources
        resources = [
            {
                "uri": "bosco://memory",
                "name": "Bosco Memory",
                "description": "Access to Bosco's long-term memory",
                "mimeType": "application/json"
            },
            {
                "uri": "bosco://config",
                "name": "Bosco Configuration",
                "description": "Current Bosco configuration",
                "mimeType": "application/json"
            },
            {
                "uri": "bosco://status",
                "name": "Bosco Status",
                "description": "Current system status",
                "mimeType": "application/json"
            }
        ]
        
        return {"resources": resources}
    
    async def _handle_resources_read(self, params: Dict) -> Dict:
        """Handle resources/read request"""
        uri = params.get("uri", "")
        
        if uri == "bosco://status":
            from bosco_os.agents import get_orchestrator
            orchestrator = get_orchestrator()
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(orchestrator.get_status(), indent=2)
                    }
                ]
            }
        
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "text/plain",
                    "text": "Resource not found"
                }
            ]
        }
    
    async def _handle_prompts_list(self, params: Dict = None) -> Dict:
        """Handle prompts/list request"""
        prompts = [
            {
                "name": "security_scan",
                "description": "Run a security scan on a target",
                "arguments": [
                    {"name": "target", "description": "Target to scan", "required": True}
                ]
            },
            {
                "name": "docker_management",
                "description": "Manage Docker containers",
                "arguments": [
                    {"name": "action", "description": "Action to perform", "required": True},
                    {"name": "container", "description": "Container name/ID", "required": False}
                ]
            },
            {
                "name": "research",
                "description": "Research a topic",
                "arguments": [
                    {"name": "topic", "description": "Topic to research", "required": True}
                ]
            }
        ]
        
        return {"prompts": prompts}
    
    async def _handle_shutdown(self) -> Dict:
        """Handle shutdown request"""
        return {"message": "Server shutting down"}
    
    # ============ Default Tool Handlers ============
    
    async def _handle_server_info(self, params: Dict) -> Dict:
        """Handle server_info tool"""
        return {
            "name": self.name,
            "version": self.version,
            "capabilities": self.capabilities,
            "tools_count": len(self.tools)
        }
    
    async def _handle_list_tools(self, params: Dict) -> Dict:
        """Handle list_tools tool"""
        return {"tools": self.list_tools()}


class MCPClient:
    """
    MCP Client for connecting to external MCP servers
    """
    
    def __init__(self, server_url: str = None):
        self.server_url = server_url
        self.server_info: Dict = {}
        self.tools: List[Dict] = []
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize connection to MCP server"""
        # This is a simplified client implementation
        # In production, would use actual transport (stdio, HTTP, etc.)
        
        self.is_initialized = True
        return True
    
    async def call_tool(self, tool_name: str, arguments: Dict = None) -> Any:
        """Call a tool on the MCP server"""
        if not self.is_initialized:
            await self.initialize()
        
        # This would make actual RPC call in production
        raise NotImplementedError("Client RPC not implemented")
    
    async def list_tools(self) -> List[Dict]:
        """List available tools"""
        if not self.is_initialized:
            await self.initialize()
        
        return self.tools


# ============ MCP Adapters ============

class VSCodeAdapter:
    """Adapter for VS Code integration"""
    
    def __init__(self, mcp_server: MCPServer):
        self.server = mcp_server
    
    def get_extension_config(self) -> Dict:
        """Get VS Code extension configuration"""
        return {
            "name": "bosco-core",
            "version": "1.0.0",
            "engines": {"vscode": "^1.80.0"},
            "contributes": {
                "commands": [
                    {
                        "command": "bosco.scan",
                        "title": "Bosco Security Scan"
                    },
                    {
                        "command": "bosco.research",
                        "title": "Bosco Research"
                    }
                ]
            }
        }


class SlackAdapter:
    """Adapter for Slack integration"""
    
    def __init__(self, mcp_server: MCPServer, webhook_url: str = None):
        self.server = mcp_server
        self.webhook_url = webhook_url
    
    async def send_alert(self, message: str):
        """Send alert to Slack"""
        # Would use requests to post to webhook
        print(f"[SlackAdapter] Would send: {message}")


# Global server instance
_mcp_server: Optional[MCPServer] = None


def get_mcp_server(name: str = "bosco-core") -> MCPServer:
    """Get or create the MCP server"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer(name)
    return _mcp_server


if __name__ == "__main__":
    print("=== Testing MCP Server ===\n")
    
    # Create server
    server = MCPServer("bosco-test")
    
    # Add custom tool
    async def hello_handler(params):
        name = params.get("name", "World")
        return {"message": f"Hello, {name}!"}
    
    server.register_tool(MCPTool(
        name="hello",
        description="Say hello",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name to greet"}
            }
        },
        handler=hello_handler
    ))
    
    # Test request
    async def test():
        # Initialize
        req = MCPRequest("initialize", {"clientInfo": {"name": "test"}})
        resp = await server.handle_request(req)
        print(f"Initialize: {resp.result is not None}")
        
        # List tools
        req = MCPRequest("tools/list")
        resp = await server.handle_request(req)
        print(f"Tools: {len(resp.result['tools'])}")
        
        # Call custom tool
        req = MCPRequest("tools/call", {"name": "hello", "arguments": {"name": "Bosco"}})
        resp = await server.handle_request(req)
        print(f"Hello result: {resp.result}")
    
    asyncio.run(test())

