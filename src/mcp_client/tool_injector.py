import inspect
import ast
from multiprocessing import Value
import re
import json
import asyncio
import aiohttp
from langchain_core.tools import Tool  # Ensure this is the correct import for your Tool

def extract_tool_source(func) -> str:
    """Extract the source code of the tool function."""
    try:
        source = inspect.getsource(func)
        return source
    except Exception as e:
        print(f"Error extracting source: {e}")
        return ""

def extract_imports(source: str) -> list:
    """Extract all import statements from the source code as metadata."""
    imports = []
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({"module": alias.name, "as": alias.asname})
            elif isinstance(node, ast.ImportFrom):
                imported = [alias.name for alias in node.names]
                imports.append({"module": node.module, "names": imported})
    except Exception as e:
        print(f"Error extracting imports: {e}")
    return imports

def extract_env_dependencies(source: str) -> list:
    """Extract environment variable keys from os.environ usage."""
    pattern = r'os\.environ\[(?:\'|\")([^\'"]+)(?:\'|\")\]'
    matches = re.findall(pattern, source)
    return list(set(matches))

def extract_bound_variables(func) -> dict:
    """
    Extract bound variables from the function.
    Returns a dictionary with nonlocals, globals, and builtins using string representations
    so that everything is JSON serializable.
    """
    closure_vars = inspect.getclosurevars(func)
    nonlocals = {k: repr(v) for k, v in closure_vars.nonlocals.items()}
    globals_used = {name: repr(func.__globals__.get(name))
                    for name in func.__code__.co_names if name in func.__globals__}
    builtins = {k: repr(v) for k, v in closure_vars.builtins.items()}
    return {"nonlocals": nonlocals, "globals": globals_used, "builtins": builtins}

def profile_tool_metadata(func) -> dict:
    """Return metadata for the tool containing its source, imports, env dependencies and bound variables."""
    source = extract_tool_source(func)
    imports = extract_imports(source)
    env_vars = extract_env_dependencies(source)
    bound_vars = extract_bound_variables(func)
    metadata = {
        "imports": imports,
        "env_vars": env_vars,
        "bound_variables": bound_vars,
        "source_length": len(source),
    }
    return metadata

async def add_tool_to_server(server_url: str, tool_name: str, func, description: str, config: dict, persist: bool):
    """Send a POST request to add the tool dynamically with full metadata including bound variables.
       This version expects explicit tool properties.
    """
    code = extract_tool_source(func)
    metadata = profile_tool_metadata(func)
    payload = {
        "name": tool_name,
        "func_name": func.__name__,
        "description": description,
        "config": config,
        "persist": persist,
        "code": code,
        "metadata": metadata,
    }
    async with aiohttp.ClientSession() as session:
        url = f"{server_url}/dynamic/add_tool"
        async with session.post(url, json=payload) as resp:
            async for line in resp.content:
                if line:
                    print(line.decode('utf-8').strip())


async def add_langchain_tool_to_server(server_url: str, tool_obj: Tool, config: dict, persist: bool):
    """Overloaded version that accepts a LangChain Tool instance.
       It automatically extracts name, description and the underlying function.
    """
    tool_name = tool_obj.name
    description = tool_obj.description
    func = tool_obj.func
    if not callable(func):
        raise ValueError("Tool function is not defined.")
    code = extract_tool_source(func)
    metadata = profile_tool_metadata(func)
    payload = {
        "name": tool_name,
        "func_name": func.__name__,
        "description": description,
        "config": config,
        "persist": persist,
        "code": code,
        "metadata": metadata,
    }
    async with aiohttp.ClientSession() as session:
        url = f"{server_url}/dynamic/add_tool"
        async with session.post(url, json=payload) as resp:
            async for line in resp.content:
                if line:
                    print(line.decode('utf-8').strip())


# Example tool to be injected.
def dynamic_example_tool(arg1: str) -> str:
    """
    Example dynamically injected tool.
    It returns a message with the provided argument and checks for an environment key.
    Also demonstrates usage of a bound variable.
    """
    import os
    def helper():
        return "helper value"
    bound_value = helper()
    required_key = os.environ.get("EXAMPLE_CONFIG", "default")
    return f"Dynamic tool received: {arg1} with config {required_key} and bound value {bound_value}"


# For testing the injector with a LangChain Tool instance.
if __name__ == "__main__":
    from langchain_core.tools import Tool
    server_url = "http://localhost:8010"
    # Assume web_search_google is defined as a Tool in basic_tools.py.
    # For demonstration, we create a dummy tool instance.
    dummy_tool = Tool(
        name="dynamic_example_tool",
        description="A dummy search tool for testing.",
        func=dynamic_example_tool
    )
    asyncio.run(add_langchain_tool_to_server(
        server_url=server_url,
        tool_obj=dummy_tool,
        config={"EXAMPLE_CONFIG": "value123"},
        persist=True
    ))
