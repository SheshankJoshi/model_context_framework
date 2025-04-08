from typing import Dict
import asyncio
from contextlib import asynccontextmanager
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import StdioConnection
from typing import TypedDict, Union, Literal, Optional, Any
from config import SSEConnection, ClientSessionConfig
import mcp.types as types
from mcp.shared.context import RequestContext
from pydantic import BaseModel, Field
from mcp_client.mcp_client_callbacks import *
from mcp.shared.version import SUPPORTED_PROTOCOL_VERSIONS


# You have to create a connection params object like this
connection_params = SSEConnection(**{"url":"http://localhost:8010/sse",
                                      "headers": {},
                                    "timeout" : 30.0,
                                    "sse_read_timeout": 30.0})


# async def custom_message_handler(message):
#     # Handle incoming messages from the server.
#     print("Custom message received:", message)
#     return "I am letting you know that I have received the message"

async def custom_logging_callback(params: types.LoggingMessageNotificationParams):
    # For logging notifications, you might simply print them.
    print(f"Tool log: {params.data}")
    
async def get_config_callback(context: RequestContext):
    some_condition = True  # Replace with actual condition to check for DB config
    try:
        if not some_condition:
            raise ValueError("No DB config set")
        
        return {"conn_str": "something"}
    except Exception as e:
        return types.ErrorData(code=types.INVALID_REQUEST, message=str(e))


# You have to create a session params object like this
session_params = ClientSessionConfig(
    logging_callback=custom_logging_callback)
    # It can be an empty object for now, but in server deployment, should deploy it properly for troubleshooting

# notification_params = types.NotificationParams()

# class ConfigNotificationParams(types.NotificationParams):
#     """Custom notification parameters for session configuration."""
#     # Add any additional fields you need for your notification
#     params: Dict[str, str] = Field(default={})
#     method: Literal["client/session_config"] = Field(default="client/session_config")

# # NOTE : This has to be properly subclassed from the ClientNotification for it to work
# class ConfigNotification(types.Notification):
#     """Data model for session configuration notification to the server after a handshake is established."""
#     params: Dict[str, str] = Field(default={})
#     method: Literal["client/session_config"] = Field(default="client/session_config")
        
# def create_config_notification_object(config_params: Dict[str,str]) -> ConfigNotification:
#     """Create a notification object for sending to the server."""
#     return ConfigNotification(params=config_params)  # type: ignore
    
class NaviClientSession(ClientSession):
    """A subclass of ClientSession that adds custom functionality."""
    def __init__(self,  *args, config_params: Optional[Dict[str, str]] = None, **kwargs):
        
        super().__init__(*args, **kwargs)
        self.session_config = config_params
        
    async def initialize(self) -> types.InitializeResult:
        # Custom initialization logic here
        print("Custom session initialization with config:", self.session_config)
        # Call the parent class's initialize method
        result = await super().initialize()
        sampling = types.SamplingCapability()
        roots = types.RootsCapability(
            # TODO: Should this be based on whether we
            # _will_ send notifications, or only whether
            # they're supported?
            listChanged=True,
        )
        init_request = types.InitializeRequestParams(
                        protocolVersion=types.LATEST_PROTOCOL_VERSION,
                        capabilities=types.ClientCapabilities(
                            sampling=sampling,
                            experimental=None,
                            roots=roots,
                        ),
                        clientInfo=types.Implementation(name="mcp", version="0.1.0"),
                    )
        init_request.env_config = self.session_config #type: ignore
        result = await self.send_request(
            types.ClientRequest(
                types.InitializeRequest(
                    method="initialize",
                    params= init_request
                )
            ),
            types.InitializeResult,
        )
        if result.protocolVersion not in SUPPORTED_PROTOCOL_VERSIONS:
            raise RuntimeError(
                "Unsupported protocol version from the server: "
                f"{result.protocolVersion}"
            )

        await self.send_notification(
            types.ClientNotification(
                types.InitializedNotification(method="notifications/initialized")
            )
        )

        return result

    # async def send_custom_init(self):
    #     """Configure this method to set everything besides just the configuration on the server side from client"""
    #     await self.set_session_config(self.session_config)

    # async def set_session_config(self, config: Optional[Dict[str, str]] = None):
    #     if not config:
    #         config = self.session_config
    #     if not config:
    #         raise ValueError("No configuration provided to set.")
    #     notification = create_config_notification_object(config_params = config)
    #     await self.send_notification(notification) #type: ignore
    #     """Set the client configuration."""
    #     # Custom logic to set the client configuration
    #     if config != self.session_config:
    #         self.session_config = config
    #     print("Client configuration set:", config)
        
    async def change_context(self, context: Dict[str, str]):
        """Change the context of the session."""
        if not context:
            raise ValueError("No context provided to change.")
        # Custom logic to change the session context
        self.session_config = context
        print("Session context changed:", context)
        #! TODO - Should send a notification to the server that the context has changed and the server should also implement the same on its side
        await self.initialize()
        # Reinitialize the session with the new context
    

    
    # async def send_custom_init_message(self):
    #     # Custom internal session init message
    #     from mcp.types import ClientNotification

    #     notification = ClientNotification(
    #         root={
    #             "method": "session/config",
    #             "params": self.session_config  # e.g., {"conn_str": "...", "db_user": "..."}
    #         }
    #     )
    #     await self.send_notification(notification)


@asynccontextmanager
async def get_an_mcp_session(transport : Literal["sse", "stdio"], connection_params: Union[SSEConnection, StdioServerParameters], session_params: ClientSessionConfig, context: Optional[dict] = None):
    """Async context manager that yields an MCP session.
    The session is created using the asynchronous sse_client.
    """
    if transport == "sse":
        # if context:
        #     connection_params.headers.update(context) #type: ignore
        #     # session_params.context = context #type: ignore
        async with sse_client(**connection_params.model_dump()) as (read, write): #type: ignore
            # session_params.config_params = context
            async with NaviClientSession(read, write, config_params=context,**session_params.model_dump()) as session: #type: ignore
                await session.initialize()
                print("Session is now initialized")
                yield session
    else:
        async with stdio_client(server=connection_params) as (read, write): #type: ignore
            async with ClientSession(read, write, **session_params.model_dump()) as session:
                await session.initialize()
                print("Session is now initialized")
                yield session

async def example_call():
    from pprint import pprint
    # NOTE : This custom context should be completely JSON Serializable, else it won't work.
    custom_context = {
        "custom_key": "custom_value"}
    async with get_an_mcp_session(transport="sse", connection_params=connection_params, session_params=session_params, context=custom_context) as session:
        # Start the event listener task.
        # listener_task = asyncio.create_task(event_listener(session))

        # # Perform tool operations.
        # tools = await session.list_tools()
        # print("Tools:", tools)
        # # Alternatively, you can directly load langchain tools
        langchain_tools = await load_mcp_tools(session)
        print("LangChain Tools:", langchain_tools)

        tools_result = await session.call_tool("echo_tool", arguments={"message": "Hello, World!"})
        print("Echo Tool Result:", tools_result)
        # Change the context in the middle of the session
        # # NOTE : This doesn't work in stdio session. It only works in SSE session
        # if isinstance(session, NaviClientSession):
        #     await session.change_context({"new_key": "new_value"})
        # #
        langchain_tools_result = await langchain_tools[0].arun(tool_input = {"message": "Hello, World!"})
        print("LangChain Tool Result:", langchain_tools_result)



if __name__ == "__main__":
    asyncio.run(example_call())
