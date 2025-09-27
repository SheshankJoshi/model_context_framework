import asyncio
import os
import shutil


# from agents import Agent, Runner, set_trace_processors
# from agents.mcp import MCPServer, MCPServerStdio
# from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor
# import weave


# # Initialize Weave project
# weave.init("mcp_stuff")
# set_trace_processors([WeaveTracingProcessor()])  # Enable Weave tracing


# async def run(mcp_server: MCPServer):
#     agent = Agent(
#         name="Assistant",
#         instructions="Use the tools to read the filesystem and answer questions based on those files.",
#         mcp_servers=[mcp_server],
#     )


#     message = "Read the files and list them."
#     print(f"Running: {message}")
#     result = await Runner.run(starting_agent=agent, input=message)
#     print(result.final_output)


#     message = "What is my #1 favorite book?"
#     print(f"\n\nRunning: {message}")
#     result = await Runner.run(starting_agent=agent, input=message)
#     print(result.final_output)


#     message = "Look at my favorite songs. Suggest one new song that I might like."
#     print(f"\n\nRunning: {message}")
#     result = await Runner.run(starting_agent=agent, input=message)
#     print(result.final_output)


# async def main():
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     samples_dir = os.path.join(current_dir, "sample_files")


#     async with MCPServerStdio(
#         name="Filesystem Server, via npx",
#         params={
#             "command": "npx",
#             "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
#         },
#     ) as server:
#         await run(server)


# if __name__ == "__main__":
#     if not shutil.which("npx"):
#         raise RuntimeError("npx is not installed. Please install it with `npm install -g npx`.")
#     asyncio.run(main())
