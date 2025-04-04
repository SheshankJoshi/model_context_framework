from starlette.applications import Starlette
from starlette.routing import Mount, Route
from mcp.server.fastmcp import Context
from my_mcp.mcp_server.mcp_extension import ExtendedMCP
from typing import TYPE_CHECKING, TypeVar
import logging

ExtendedMCPType = TypeVar("ExtendedMCPType", bound="ExtendedMCP")

logging.basicConfig(level=logging.DEBUG)

mcp_settings = {
    "host": "127.0.0.1",
    "port": 8010,
    "sse_path": "/sse",
    "message_path": "/messages/",
    "log_level": "DEBUG"
}

# Instantiate our extended MCP server.
mcp = ExtendedMCP(name = "Detailed MCP Server", instructions=None,  **mcp_settings)

# Register static tools.
@mcp.tool()
def echo_tool(message: str, context: Context) -> str:
    """A simple echo tool that returns the message prefixed with 'Echo:'."""
    logging.debug(f"echo_tool invoked with message: {message}")
    return f"Echo: {message}"

@mcp.tool()
def langchain_search(query: str, context: Context) -> str:
    """A simulated search tool that returns dummy search results."""
    return f"Simulated search results for query: {query}"

@mcp.prompt()
def agent_prompt(message: str) -> str:
    """A prompt used by agents to process a message."""
    return f"Agent, please process the following message:\n{message}"

@mcp.resource("resource://echo/{message}")
def echo_resource(message: str) -> str:
    """A resource that echoes a message."""
    return f"Resource echo: {message}"

@mcp.route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint."""
    return {"status": "healthy"}

@mcp.route("/dynamic/add_tool", methods=["POST"])
async def add_tool_endpoint(request):
    data = await request.json()
    # Expected keys: name, func_name, description, config (optional), persist (bool),
    # code (optional), and metadata (optional)
    tool_name = data.get("name")
    func_name = data.get("func_name", "")
    description = data.get("description", "")
    config = data.get("config", {})
    persist = data.get("persist", False)
    code = data.get("code", "")
    metadata = data.get("metadata", {})
    try:
        mcp.add_tool_dynamically(tool_name, func_name, description, config, persist, code, metadata)
        logging.info(f"Tool {tool_name} added dynamically")
        return {"status": "success", "message": f"Tool {tool_name} added."}
    except Exception as e:
        logging.error(f"Error adding tool {tool_name}: {e}")
        return {"status": "error", "message": str(e)}

# Build the SSE app using mcp.sse_app()

#TODO - mcp serving extra routes only over SSE. It doesn't allow the serving on local for extra paths. This needs fixing

if __name__ == "__main__":
    logging.info("Starting MCP server")
    mcp.run(transport="sse")
