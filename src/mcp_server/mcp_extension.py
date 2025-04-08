import json
import os
import time
import re
from typing import Any, Dict, Literal, Optional, Awaitable, Callable
from httpx import request
from lmstudio import BaseModel
from mcp import ClientNotification
from mcp.server.fastmcp import FastMCP, Context
from mcp.shared.context import RequestContext
import uuid
import asyncio
from pydantic import Field
from starlette.routing import Route
from starlette.applications import Starlette
from starlette_context.middleware import ContextMiddleware
from mcp.types import ErrorData, INVALID_REQUEST, ServerResult, EmptyResult, NotificationParams, Notification, ProgressNotification

TOOLS_PERSISTENCE_FILE = "registered_tools.json"

class SessionConfig(BaseModel):
    """Data model for session configuration."""
    session_id: str
    config: Dict[str, Any]

class ToolConfig(BaseModel):
    request_id: str
    tool_name: str
    tool_config: Dict[str, Any]
    
class ConfigNotificationParams(NotificationParams):
    """Custom notification parameters for session configuration."""
    # Add any additional fields you need for your notification
    params: Dict[str, str] = Field(default={})
    method: Literal["client/session_config"] = Field(default="client/session_config")

class ConfigNotification(Notification):
    """Data model for session configuration notification to the server after a handshake is established."""
    params: ConfigNotificationParams


class ExtendedMCP(FastMCP):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tool_registry: Dict[str, Dict[str, Any]] = {}
        # self.load_persisted_tools()
        self.tools_loaded_persist = False
        self._extra_paths = {}
        self.session_config_store: Dict[str, Dict[str, Any]] = {}
        # self._mcp_server.notification_handlers[ProgressNotification] = self.handle_session_config_notification #type: ignore
        # Additional configuration here
        # self._mcp_server.request_handlers[SessionConfig] = self.handle_session_config
        # self._mcp_server.request_handlers[ToolConfig] = self.handle_tool_config

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
        from tool_mapping import mapping_tools
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
        app.add_middleware(ContextMiddleware)
        self.append_extra_routes(app)
        return app
    
    async def create_context(self, request) -> Context:
        # Call the base method to create the default context.
        context = await super().create_context(request)  # type: ignore
        session_context = context.request_context.session

        # Capture incoming headers from the request.
        if request.headers:
            session_context.headers = dict(request.headers)
        
        # If a session id is provided in the headers, use it; otherwise, generate a new one.
        session_id = session_context.headers.get("x-session-id")
        if not session_id:
            session_id = str(uuid.uuid4())
            # Optionally, you may update the headers with the new session id.
            session_context.headers["x-session-id"] = session_id
        
        # Store the session id in the session context.
        session_context.session_id = session_id
        
        # Optionally, you can extract query parameters or any other data from the request.
        if hasattr(request, "query_params"):
            session_context.query_params = dict(request.query_params)
        
        # Here you can set any additional variables that you want available for a particular tool call.
        # For example, you might want to extract a custom header:
        custom_value = session_context.headers.get("x-custom-variable")
        if custom_value:
            session_context.custom_variable = custom_value

        return context

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

    async def handle_session_config(self, context: RequestContext, method: str, params: Any):
        """Handle session configuration messages."""
        async def give_result(end="success"):
            """Return an empty result."""
            if end == "success":
                return EmptyResult()
            else:
                return ErrorData(code=INVALID_REQUEST, message="Invalid config format")
        if method == "client/session_config":
            session_id = context.request_id
            if not isinstance(params, dict):
                return give_result("Invalid config format")

            self.session_config_store[str(session_id)] = params
            context.session.config = params
        return give_result("success")
    
    
    # Currently we are handling on progress notification. We are not handling anything else.
    async def handle_session_config_notification(self, context: Context, notification: ProgressNotification) -> None:
        """
        Notification handler for session configuration.
    
        Expects a ConfigNotification with method "client/session_config" and a dict of parameters.
        If valid, updates (or appends) the session configuration in the underlying session context.
        """
        # Extract method and parameters. If notification.params is a ConfigNotificationParams instance,
        # call .dict() to convert it to a dict.
        method = notification.method
        params = notification.params.dict() if hasattr(notification.params, "dict") else notification.params

        if method != "client/session_config":
            await context.error(f"Unexpected method {method} in session config notification.")
            return

        if not isinstance(params, dict):
            await context.error("Invalid config format in session config notification; expected dict.")
            return

        # Get current session configuration from the context; update or assign anew.
        current_config = getattr(context.session, "config", {}) or {}
        if not isinstance(current_config, dict):
            current_config = {}
        current_config.update(params)
        
        # Optionally, store the configuration in the server's session_config_store.
        self.session_config_store[str(context.request_id)] = current_config
        
        await context.info(f"Session config updated for request {context.request_id}: {current_config}")

    # In __init__ or appropriate setup add the handler to notification_handlers:
    # self.notification_handlers[<NotificationType>] = self.handle_session_config_notification
    # For example, if using the "session/config" method for notifications, you can assign a dummy type:
    # self.notification_handlers["session/config"] = self.handle_session_config_notification


    # async def handle_notification2(self, context: RequestContext, method: str, params: Any):
    #     if method == "session/config":
    #         session_id = context.request_id
    #         if not isinstance(params, dict):
    #             return ErrorData(code=INVALID_REQUEST, message="Invalid config format")

    #         self.session_config_store[session_id] = params
    #         context.session.config = params  # optionally make it available through context
    #         print(f"Stored config for session {session_id}: {params}")
    #         return

        # return await super().handle_notification(context, method, params)



    def append_extra_routes(self, app: Starlette):
        """Append extra routes stored by the route decorator to the Starlette app."""
        for path, info in self._extra_paths.items():
            app.router.routes.append(Route(path, info["fn"], methods=info["methods"]))
            
            
    def wrap_tool_function(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """
        Returns a wrapped version of fn that, when invoked with a context,
        injects environment variables from the client's env_config and restores them afterward.
        """
        if asyncio.iscoroutinefunction(fn):
            async def async_wrapper(*args, **kwargs):
                context: Optional[Context] = kwargs.get("context")
                old_env = {}
                env_config = {}
                if context is not None and hasattr(context.session, "config"):
                    session_config = context.session.config
                    if isinstance(session_config, dict):
                        env_config = session_config.get("env_config", {})
                # Pre-call: set env variables from env_config.
                for key, value in env_config.items():
                    if key in os.environ:
                        old_env[key] = os.environ[key]
                    os.environ[key] = str(value)
                try:
                    result = await fn(*args, **kwargs)
                finally:
                    # Post-call: restore the original environment.
                    for key in env_config.keys():
                        if key in old_env:
                            os.environ[key] = old_env[key]
                        else:
                            os.environ.pop(key, None)
                return result
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                context: Optional[Context] = kwargs.get("context")
                old_env = {}
                env_config = {}
                if context is not None and hasattr(context.session, "config"):
                    session_config = context.session.config
                    if isinstance(session_config, dict):
                        env_config = session_config.get("env_config", {})
                # Pre-call: set environment variables.
                for key, value in env_config.items():
                    if key in os.environ:
                        old_env[key] = os.environ[key]
                    os.environ[key] = str(value)
                try:
                    result = fn(*args, **kwargs)
                finally:
                    # Post-call: restore original environment.
                    for key in env_config.keys():
                        if key in old_env:
                            os.environ[key] = old_env[key]
                        else:
                            os.environ.pop(key, None)
                return result
            return sync_wrapper

    def add_tool(self, fn: Callable[..., Any], name: Optional[str]=None, description: Optional[str] = None):
        """
        Wrap the tool function to inject environment configuration on each call, and then use the
        default add_tool mechanism from the underlying ToolManager.
        """
        # Wrap the function:
        wrapped_fn = self.wrap_tool_function(fn)
        # Call the base (or underlying tool manager) add_tool:
        super().add_tool(wrapped_fn, name=name, description=description)
        # Optionally, update your local tool registry.
        self.tool_registry[name] = {"name": name, "description": description} #type: ignore

