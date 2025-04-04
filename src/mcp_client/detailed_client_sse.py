import asyncio
from contextlib import asynccontextmanager
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import StdioConnection
from typing import TypedDict, Union, Literal
from openai import timeout
from config import SSEConnection, ClientSessionConfig


# You have to create a connection params object like this
connection_params = SSEConnection(**{"url":"http://localhost:8001/sse",
                                      "headers": {},
                                    "timeout" : 30.0,
                                    "sse_read_timeout": 30.0})

# You have to create a session params object like this
session_params = ClientSessionConfig() # It can be an empty object for now, but in server deployment, should deploy it properly for troubleshooting

async def handle_sampling_message(message):
    print("Sampling message:", message)

@asynccontextmanager
async def get_an_mcp_session(transport : Literal["sse", "stdio"], connection_params: Union[SSEConnection, StdioServerParameters], session_params: ClientSessionConfig):
    """Async context manager that yields an MCP session.
    The session is created using the asynchronous sse_client.
    """
    if transport == "sse":
        async with sse_client(**connection_params.model_dump()) as (read, write): #type: ignore
            async with ClientSession(read, write, **session_params.model_dump()) as session: #type: ignore
                await session.initialize()
                print("Session is now initialized")
                yield session
    else:
        async with stdio_client(server=connection_params) as (read, write): #type: ignore
            async with ClientSession(read, write, **session_params.model_dump()) as session:
                await session.initialize()
                print("Session is now initialized")
                yield session

async def event_listener(session):
    try:
        # Using an async iterator to process events.
        async for event in session.read_events():
            print("Received event:", event)
    except asyncio.CancelledError:
        print("Event listener cancelled.")


async def example_call():
    from pprint import pprint
    async with get_an_mcp_session(transport="sse", connection_params=connection_params, session_params=session_params) as session:
        # Start the event listener task.
        # listener_task = asyncio.create_task(event_listener(session))

        # Perform tool operations.
        tools = await session.list_tools()
        print("Tools:", tools)
        # Alternatively, you can directly load langchain tools
        langchain_tools = await load_mcp_tools(session)
        print("LangChain Tools:", langchain_tools)

        # tools_result = await session.call_tool("echo_tool", arguments={"message": "Hello, World!"})
        # print("Echo Tool Result:", tools_result)
        #
        langchain_tools_result = await langchain_tools[0].arun(tool_input = {"message": "Hello, World!"})
        print("LangChain Tool Result:", langchain_tools_result)



if __name__ == "__main__":
    asyncio.run(example_call())
