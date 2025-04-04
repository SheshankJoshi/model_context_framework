import json
import os
import time
import re
from typing import Any, Dict, Optional
from mcp.server.fastmcp import FastMCP, Context
import starlette
from starlette.routing import Route
from starlette.applications import Starlette

TOOLS_PERSISTENCE_FILE = "registered_tools.json"

class ExtendedMCP(FastMCP):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tool_registry: Dict[str, Dict[str, Any]] = {}
        # self.load_persisted_tools()
        self.tools_loaded_persist = False
        self._extra_paths = {}

    def load_persisted_tools(self):
        """Load persisted tools from a JSON file and register them."""
        if os.path.exists(TOOLS_PERSISTENCE_FILE):
            with open(TOOLS_PERSISTENCE_FILE, "r") as f:
                data = json.load(f)
                for tool_name, tool_info in data.items():
                    # Decide if we are using an imported function or the provided code.
                    if "code" in tool_info and tool_info["code"]:
                        func = self._load_tool_from_code(tool_info["code"], tool_name)
                    else:
                        func = self.lookup_tool_function(tool_info["func_name"])
                    if func is None:
                        raise ValueError(
                            f"Function {tool_info['func_name']} not found. Either send the code inline, or place the module on the server and update the mapping"
                        )
                    # Register the tool with its function.
                    self._register_tool(
                        tool_name,
                        func,
                        tool_info.get("description", ""),
                        tool_info.get("config", {}),
                    )
                    # Save metadata if available.
                    tool_info.setdefault("metadata", {})
                    self.tool_registry[tool_name] = tool_info
            self.tools_loaded_persist = True

    def lookup_tool_function(self, func_name: str):
        """Lookup a tool function by name from known modules.
           Extend this to dynamically import modules if needed.
        """
        from my_mcp.tool_mapping import mapping_tools
        return mapping_tools.get(func_name)

    def _load_tool_from_code(self, code: str, tool_name: str):
        """Dynamically compile and load a tool function from source code.
           The code should define a function called 'dynamic_tool' (or similar).
        """
        local_scope = {}
        try:
            exec(code, {}, local_scope)
            # Expect that the tool function is named f"{tool_name}_tool" or simply "dynamic_tool"
            ret_value = local_scope.get(f"{tool_name}")
            return ret_value
        except Exception as e:
            print(f"Error loading tool {tool_name} from code: {e}")
            return None

    def _register_tool(self, name: str, func, description: str, config: Dict[str, Any]):
        """Internal helper to register a tool with custom configuration."""
        @self.tool(name=name, description=description)
        def wrapped_tool(*args, context: Context, **kwargs):
            # Inject custom configuration if provided.
            if config:
                for k, v in config.items():
                    os.environ[k] = str(v)
            return func(*args, **kwargs)
        return wrapped_tool

    def add_tool_dynamically(
        self,
        name: str,
        func_name: str,
        description: str,
        config: Optional[Dict[str, Any]] = None,
        persist: bool = False,
        code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Dynamically add a new tool.
           If 'code' is provided, compile it to get the function.
           If persist is True, the tool definition (including code and metadata if any)
           is saved to a JSON file and the function code is appended to a persist_tools sub-package.
        """
        if not self.tools_loaded_persist:
            self.load_persisted_tools()

        config = config or {}
        if code:
            func = self._load_tool_from_code(code, name)
            if func is None:
                raise ValueError("Unable to load tool from provided code.")
        else:
            func = self.lookup_tool_function(func_name)
            if func is None:
                raise ValueError(f"Function {func_name} not found.")
        # Register the tool
        self._register_tool(name, func, description, config)
        # Build the tool entry.
        tool_entry = {
            "func_name": func_name,
            "description": description,
            "config": config,
            "code": code or "",
            "metadata": metadata or {},
        }
        self.tool_registry[name] = tool_entry
        # Persist only if requested.
        if persist:
            # Write to persistence JSON file.
            with open(TOOLS_PERSISTENCE_FILE, "w") as f:
                json.dump(self.tool_registry, f, indent=2)
            # Instead of appending the tool code to __init__.py, create a unique module for the tool.
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_dir = os.path.join(base_dir, "tools", "persist_tools")
            if not os.path.exists(persist_dir):
                os.makedirs(persist_dir)
            # Generate a unique module name using timestamp.
            timestamp = int(time.time())
            unique_module_name = f"{name}_{timestamp}.py"
            persist_file = os.path.join(persist_dir, unique_module_name)
            # Write the given code into the unique module file as is.
            try:
                with open(persist_file, "w") as f:
                    f.write(f"# Auto-generated on {time.ctime(timestamp)}\n")
                    f.write(code if code else f"# No code provided for tool {name}.\n")
            except Exception as e:
                print(f"Error writing tool code to {persist_file}: {e}")

    def sse_app(self):
        """This is going to add some extra paths to the Starlette app, with underlying mechanism"""
        app = super().sse_app()
        self.append_extra_routes(app)
        return app

    def route(self, path: str, methods=["GET"]):
        """
        Decorator that adds a new HTTP route to the given MCP instance.

        Parameters:
        path: The URL path for the new route.
        methods: List of HTTP methods allowed (default is ["GET"]).

        The decorated function will be used as the route handler.
        """
        def decorator(fn):
            self._extra_paths[path] = {"fn": fn, "methods": methods}
            return fn
        return decorator

    def append_extra_routes(self, app: Starlette):
        """Append extra routes stored by the route decorator to the Starlette app."""
        for path, info in self._extra_paths.items():
            app.router.routes.append(Route(path, info["fn"], methods=info["methods"]))

