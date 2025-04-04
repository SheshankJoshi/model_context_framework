import asyncio
import json
import logging
from mcp.server import Server
from mcp.server import InitializationOptions, NotificationOptions
from mcp.server.stdio import stdio_server
# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define available tools
def math_solver(params):
    """Executes mathematical expressions."""
    try:
        expression = params.get("expression", "")
        result = eval(expression)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def file_reader(params):
    """Reads a file's content."""
    try:
        file_path = params.get("path", "")
        with open(file_path, "r") as file:
            content = file.read()
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool registry
TOOLS = {
    "math_solver": math_solver,
    "file_reader": file_reader,
}

async def handle_request(request):
    """Processes incoming MCP requests."""
    try:
        data = json.loads(request)
        tool_name = data.get("tool")
        params = data.get("params", {})

        if tool_name in TOOLS:
            response = TOOLS[tool_name](params)
        else:
            response = {"status": "error", "message": f"Unknown tool: {tool_name}"}
        
        return json.dumps(response)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# Actual server setup
# Initialization options

async def start_server():
    server = Server("sample_testing")
    initialize_options = InitializationOptions(
                server_name="navi_server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(notification_options=NotificationOptions(),experimental_capabilities={})
            )
    async with stdio_server() as (read_stream, write_stream):
        print("server setup is done. Now server is running")
        await server.run(
            read_stream,
            write_stream,
            initialization_options=initialize_options,
        )

if __name__ == "__main__":
    asyncio.run(start_server())
