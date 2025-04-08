from attr import has
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from mcp.server.fastmcp import Context as MCPContext
from mcp_server.mcp_extension import ExtendedMCP
from starlette_context.middleware import ContextMiddleware
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
async def echo_tool(message: str, context: MCPContext) -> str:
    """A simple echo tool that returns the message prefixed with 'Echo:'."""
    logging.debug(f"echo_tool invoked with message: {message}")
    # nonlocal context
    print("The context here is :", context)
    await context.info("Info from echo tool")	
    await context.warning("Warning from echo tool")
    print("=======1==========")
    # headers =  context.request_context.session.headers
    client_parameters = context.session.client_params
    if hasattr(client_parameters, "model_extra"):
        # If the client_params has model_extra, we can access it
        session_env = client_parameters.model_extra["env_config"]
    print("session meta is :", session_env)
    print("========3=========")
    return f"Echo: {message}"

@mcp.tool()
def langchain_search(query: str) -> str:
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
