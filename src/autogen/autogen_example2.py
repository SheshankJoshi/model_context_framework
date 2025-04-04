


from autogen_agentchat.messages import TextMessage, ModelClientStreamingChunkEvent,  MultiModalMessage
from autogen_agentchat.base import Response
from autogen_core import CancellationToken
from autogen_agentchat.ui import Console
from autogen_agentchat.agents import AssistantAgent
from io import BytesIO
from PIL import Image as PILImage
import requests
from autogen_core import Image



async def simple_assistant(agent: AssistantAgent) -> None:
    # Use an async function and asyncio.run() in a script.
    async for message in agent.on_messages_stream(  # type: ignore
        [TextMessage(content="Name two cities in South America", source="user")],
        cancellation_token=CancellationToken(),

    ):
        try:
            if isinstance(message, ModelClientStreamingChunkEvent):
                print(message.content, end = "", flush=True)
            else:
                print(message.chat_message.content)
        except Exception as e:
            print(e)

async def assistant_run(agent: AssistantAgent) -> None:
    # response = await simple_assistant_agent.on_messages(
    #     [TextMessage(content="Find information on AutoGen", source="user")],
    #     cancellation_token=CancellationToken(),
    # )
    response = await agent.run(
        task=[TextMessage(content="Find information on AutoGen", source="user")],
        cancellation_token=CancellationToken(),
    )
    print(response.messages)
    print(response.stop_reason)

async def multi_modal_check(agent: AssistantAgent) -> None:
    pil_image = PILImage.open(BytesIO(requests.get("https://picsum.photos/300/200").content))
    img = Image(pil_image)
    multi_modal_message = MultiModalMessage(content=["Can you describe the content of this image?", img], source="user")
    print(multi_modal_message)
    pil_image.show()
    response = await agent.on_messages([multi_modal_message], CancellationToken())
    print(response.chat_message.content)
    # response = await agent.run(task = [multi_modal_message], cancellation_token=CancellationToken())
    # print(response.messages)

async def assistant_run_stream(agent) -> None:
        await Console(
            agent.on_messages_stream(
                [TextMessage(content="Find information on latest earthquakes", source="user")],
                cancellation_token=CancellationToken(),
            ),
            output_stats=True,  # Enable stats printing.
        )


if __name__ == "__main__":
    import asyncio
    from agentic_framework.src.my_mcp.autogen.agents import simple_assistant_agent # type: ignore
    # -- simple assistant --
    # asyncio.run(simple_assistant())
    #
    # -- assistant run --
    # asyncio.run(assistant_run(simple_assistant_agent))
    #
    # -- multi modal check --
    # asyncio.run(multi_modal_check(simple_assistant_agent))
    #
    # -- agent streaming with stats check --
    asyncio.run(assistant_run_stream(simple_assistant_agent))
