"""
Module: agentic_framework.src.my_mcp.tools
------------------------------------------
This module is responsible for auto-discovering and registering tool functions with
the MCP server. It scans all modules and submodules in the package for functions whose
names end with "_tool". Each discovered function is then converted into a tool configuration
containing the tool's name (derived by removing the "_tool" suffix), description, and function
reference, and is registered with the MCP instance via mcp.add_tool.

Usage:
    The load_tools(mcp) function should be called with a valid MCP instance to automatically
    load and register all available tools in the package.

Mechanism:
    - Utilizes pkgutil.walk_packages to iterate over all submodules.
    - Uses importlib.import_module to dynamically import modules.
    - Inspects each module for functions matching the "_tool" naming pattern.
    - Registers each tool with the MCP using the provided tool configuration.
"""

import pkgutil
import importlib
import inspect
from my_mcp.mcp_server import mcp, ExtendedMCPType
import logging
logger = logging.getLogger(__name__)

def load_tools(mcp: ExtendedMCPType):
    """
    Automatically scan modules within this package, find all functions
    whose names end with '_tool', and add them to the MCP instance via mcp.add_tool.

    Parameters:
        mcp: The MCP instance which maintains the list of available tools.
    """
    # __path__ is available in packages to list submodules
    for finder, module_name, ispkg in pkgutil.walk_packages(__path__, __name__ + "."):
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module):
            for existing_tool in mcp._tool_manager.list_tools(): #type: ignore
                if obj == existing_tool.fn:
                    print(f"Tool {name} already registered, skipping.")
                    break
            if inspect.isfunction(obj) and name.endswith("_tool"):
                tool_config = {
                    "name": name.removesuffix("_tool"),
                    "description": obj.__doc__ or "No description provided.",
                    "fn": obj
                }
                # Register the tool with the MCP instance
                mcp.add_tool(**tool_config)
    print("Logged all tools in the package.") #type: ignore
    print(mcp._tool_manager._tools.keys())

load_tools(mcp)
# This will automatically load all tools defined in this package that end with "_tool"
# and register them with the MCP instance.
