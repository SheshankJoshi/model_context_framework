from starlette.applications import Starlette
from starlette.routing import Mount, Host
from mcp.server.fastmcp import FastMCP, Context


mcp_settings = {
    "host": "0.0.0.0",
    "port": 8000,
    "sse_path": "/sse",
    "message_path": "/messages/",}

mcp = FastMCP("My SSE Server App", settings=mcp_settings)

# Mount the SSE server to the existing ASGI server
app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app()),
    ]
)

# or dynamically mount as host
# app.router.routes.append(Host('mcp.acme.corp', app=mcp.sse_app()))

# mcp = FastMCP("Echo")


@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"


@mcp.tool()
def echo_tool(message: str, context: Context ) -> str:
    """Echo a message as a tool"""
    return f"Tool echo: {message}"


@mcp.prompt()
def echo_prompt(message: str) -> str:
    """Create an echo prompt"""
    return f"Please process this message: {message}"

if __name__ == "__main__":
    mcp.run(transport="sse")


