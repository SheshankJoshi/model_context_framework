from mcp.types import Tool, TextContent
from langchain.tools.base import BaseTool

class LangChainAdapterTool(BaseTool):
    name: str = "mcp_tool"
    description: str
    mcp_tool: Tool

    def __init__(self, mcp_tool: Tool) -> None:
        self.mcp_tool = mcp_tool
        self.name = mcp_tool.name
        self.description = mcp_tool.description or ""

    def _run(self, tool_input: str) -> str:
        # Call the mcp tool function synchronously
        result = self.mcp_tool.fn(tool_input) # type: ignore
        # Convert TextContent (or similar) to plain string
        if isinstance(result, TextContent):
            return result.text
        return str(result)

    async def _arun(self, tool_input: str) -> str:
        # If the tool supports async operation; else call _run
        return self._run(tool_input)


def convert_mcp_tools_to_langchain(mcp_tools: list[Tool]) -> list[LangChainAdapterTool]:
    """Convert a list of mcp.tools to LangChain-adapter tools."""
    return [LangChainAdapterTool(tool) for tool in mcp_tools]
