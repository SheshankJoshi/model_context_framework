from autogen_core.tools import FunctionTool
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools # Can create multiple mcp tools also, i.e. tools that follow mcp protocol
import test


# Define a tool using a Python function.
async def dummy_web_search_func(query: str) -> str:
    """Find information on the web"""
    return "AutoGen is a programming framework for building multi-agent applications."

dummy_search_tool = FunctionTool(dummy_web_search_func, description="Find information on the web")
def test_tool(tool: FunctionTool, input: str):
    import asyncio
    ret = asyncio.run(dummy_web_search_func("AutoGen"))
    return ret
if __name__ == "__main__":
    # -- check the schema of the tool
    ret = test_tool(dummy_search_tool, "AutoGen")
    print(ret)
    print(dummy_search_tool.schema)
