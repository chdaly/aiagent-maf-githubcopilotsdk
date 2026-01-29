import asyncio
from typing import cast

from dotenv import load_dotenv
load_dotenv()

from agent_framework import ChatMessage, Role, SequentialBuilder, WorkflowOutputEvent
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.github import GitHubCopilotAgent
from azure.identity import DefaultAzureCredential

async def main():
    # Create an Azure OpenAI agent as a copywriter
    chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential())

    writer = chat_client.as_agent(
        instructions="You are a concise copywriter. Provide a single, punchy marketing sentence based on the prompt.",
        name="writer",
    )

    # Create a GitHub Copilot agent as a reviewer
    reviewer = GitHubCopilotAgent(
        default_options={"instructions": "You are a thoughtful reviewer. Give brief feedback on the previous assistant message."},
        name="reviewer",
    )

    # Build a sequential workflow: writer -> reviewer
    workflow = SequentialBuilder().participants([writer, reviewer]).build()

    # Run the workflow
    async for event in workflow.run_stream("Write a tagline for a budget-friendly electric bike."):
        if isinstance(event, WorkflowOutputEvent):
            messages = cast(list[ChatMessage], event.data)
            for msg in messages:
                name = msg.author_name or ("assistant" if msg.role == Role.ASSISTANT else "user")
                print(f"[{name}]: {msg.text}\n")

asyncio.run(main())