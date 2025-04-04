from my_mcp.mcp_server import mcp
import tools
if __name__ == "__main__":
    print(mcp.settings.port)
    print(mcp.settings.host)
    mcp.run(transport="sse")
