from mcp.client.sse import sse_client
from mcp import ClientSession

async def incoming_message_handler(message):
    print(message)
async def connect_client():
    async with sse_client("http://localhost:8000/sse") as (read,write):
        async with ClientSession(
            read, write, sampling_callback=incoming_message_handler,
        ) as session:
            # Initialize the connection
            await session.initialize()

            # List available prompts
            prompts = await session.list_prompts()
            print("prompts :", prompts)

            # Get a prompt
            prompt = await session.get_prompt(
                "agent_prompt", arguments={"message": "Hello, world!"}
            )
            print("prompt :", prompt)

            # List available resources
            resources = await session.list_resources()
            print("resources :",resources)

            # List available tools
            tools = await session.list_tools()
            print("tools :", tools)

            # Read a resource
            # content, mime_type = await session.read_resource("echo://some_path") # can list resources or databases with sqlite://my_database.db
            # print("content:", content, "mime_type:",mime_type)

            # Call a tool
            result = await session.call_tool("echo_tool", arguments={"message": "Tool Echo here"})
            print("result of tool call", result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(connect_client())
