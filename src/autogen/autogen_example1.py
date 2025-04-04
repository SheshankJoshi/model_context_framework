import asyncio
from autogen_agentchat.agents import AssistantAgent
from mcp.config import mcp_model_client as model_client
import os

from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination, HandoffTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from pydantic import BaseModel
from typing import Literal

# os.environ["OPENAI_API_KEY"] = "39gcQzHx4OouFVZxRAb2lKE5akGB1J8OSGAj3BbAmxpcfHQORLcAJQQJ99ALACHrzpqXJ3w3AAABACOGJpy1"



# NOTE : The Below is not supported currently i.e. structuring the output. We need to think about it later
class AgentResponse(BaseModel):
    thoughts: str
    response: str
####

        # response_format=AgentResponse)

async def simple_assistant() -> None:
    agent = AssistantAgent("assistant", model_client=model_client)
    result = await agent.run(task="Say Hello World! and inform me your cutoff date for training")
    await model_client.close()
    
# pip install -U autogen-agentchat autogen-ext[openai,web-surfer]
# playwright install

# async def web_browsing_agent_team() -> None:
#     # The web surfer will open a Chromium browser window to perform web browsing tasks.
#     web_surfer = MultimodalWebSurfer("web_surfer", model_client, headless=False, animate_actions=True)
#     # The user proxy agent is used to get user input after each step of the web surfer.
#     # NOTE: you can skip input by pressing Enter.
#     user_proxy = UserProxyAgent("user_proxy")
#     # The termination condition is set to end the conversation when the user types 'exit'.
#     # termination = TextMentionTermination("exit", sources=["user_proxy"])
#     termination = HandoffTermination(target="user_proxy")
#     # Web surfer and user proxy take turns in a round-robin fashion.
#     team = RoundRobinGroupChat([web_surfer, user_proxy], termination_condition=termination)
#     try:
#         # Start the team and wait for it to terminate.
#         await Console(team.run_stream(task="Find information about latest earthquakes in Indonesia and write a short summary."))
#     finally:
#         await web_surfer.close()
#         await model_client.close()


# async def web_browsing_agent_team() -> None:
#     # The web surfer will open a Chromium browser window to perform web browsing tasks.
#     web_surfer = MultimodalWebSurfer("web_surfer", model_client, headless=False, animate_actions=True)

#     # Define a custom extraction function
#     def extract_info(page):
#         # Extract specific information from the web page
#         title = page.title
#         text = page.text_content
#         return {"title": title, "text": text}

#     # Use the extract method to apply the custom extraction function to the web pages
#     web_surfer.extract(extract_info)

#     # The termination condition is set to end the conversation when the user types 'exit'.
#     termination = HandoffTermination(target="web_surfer")

#     # Web surfer takes turns in a round-robin fashion.
#     team = RoundRobinGroupChat([web_surfer], termination_condition=termination)
#     try:
#         # Start the team and wait for it to terminate.
#         await Console(team.run_stream(task="Find information about latest earthquakes in Indonesia and write a short summary."))
#     finally:
#         await web_surfer.close()
#         await model_client.close()

async def web_browsing_agent_team() -> None:
    # The web surfer will open a Chromium browser window to perform web browsing tasks.
    web_surfer = MultimodalWebSurfer("web_surfer", 
                                     model_client, 
                                     headless=False,
                                     start_page="https://www.google.com",
                                     animate_actions=True,
                                     to_save_screenshots=False)

    # Define a custom observation function
    # def observe_page(page):
    #     # Extract specific information from the web page
    #     title = page.title
    #     text = page.text_content
    #     print(f"Visited page: {title}")
    #     print(f"Text content: {text}")

    # # Use the observe method to apply the custom observation function to the web pages
    # web_surfer.observe(observe_page)

    # The termination condition is set to end the conversation when the user types 'exit'.
    termination = HandoffTermination(target="web_surfer")

    # Web surfer takes turns in a round-robin fashion.
    team = RoundRobinGroupChat([web_surfer], termination_condition=termination)
    try:
        # Start the team and wait for it to terminate.
        await Console(team.run_stream(task="Find information about latest earthquakes in Indonesia and write a short summary."))
    finally:
        await web_surfer.close()
        await model_client.close()
if __name__ == "__main__":
    asyncio.run(web_browsing_agent_team())