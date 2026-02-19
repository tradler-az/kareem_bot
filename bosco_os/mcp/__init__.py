"""
Bosco Core - MCP Package
Model Context Protocol server and adapters
"""

from bosco_os.mcp.server import (
    MCPServer,
    MCPTool,
    MCPRequest,
    MCPResponse,
    get_mcp_server,
    VSCodeAdapter,
    SlackAdapter
)

__all__ = [
    "MCPServer",
    "MCPTool",
    "MCPRequest", 
    "MCPResponse",
    "get_mcp_server",
    "VSCodeAdapter",
    "SlackAdapter"
]

