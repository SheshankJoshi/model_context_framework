from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My MCP Plain App")

@mcp.tool()
def store_tool(message: str):
    ...

if __name__ == "__main__":
    mcp.run(transport="stdio")
