from config import mcp_model_client as model_client
from autogen_agentchat.agents import AssistantAgent


simple_assistant_agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    system_message="You are a helpful assistant.",
    model_client_stream=True,  # Enable streaming tokens.
)

