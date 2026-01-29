"""
Concurrent Workflow Pattern Demo
================================
Multiple agents work on the same task simultaneously and independently.
Results are aggregated from all agents.

Use cases:
- Parallel analysis from multiple perspectives
- Ensemble reasoning and voting systems
- Independent subtasks processing
"""

import asyncio
from typing import Any, cast

from dotenv import load_dotenv
load_dotenv()

from agent_framework import ChatMessage, ConcurrentBuilder, Role, WorkflowOutputEvent
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.github import GitHubCopilotAgent
from azure.identity import DefaultAzureCredential


async def main():
    # Initialize the Azure OpenAI chat client
    chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential())

    # Create three domain-specific agents that will work concurrently
    researcher = chat_client.as_agent(
        instructions=(
            "You're an expert market and product researcher. Given a prompt, provide concise, "
            "factual insights about market opportunities and risks. Keep response under 150 words."
        ),
        name="researcher",
    )

    marketer = chat_client.as_agent(
        instructions=(
            "You're a creative marketing strategist. Craft compelling value propositions and "
            "target messaging aligned to the prompt. Keep response under 150 words."
        ),
        name="marketer",
    )

    # Use GitHub Copilot agent as a technical reviewer
    tech_reviewer = GitHubCopilotAgent(
        default_options={
            "instructions": (
                "You're a technical advisor. Evaluate the technical feasibility and provide "
                "implementation considerations. Keep response under 150 words."
            )
        },
        name="tech_reviewer",
    )

    # Build a concurrent workflow - all agents process the same input simultaneously
    workflow = ConcurrentBuilder().participants([researcher, marketer, tech_reviewer]).build()

    print("=" * 80)
    print("CONCURRENT WORKFLOW: Multi-Perspective Analysis")
    print("=" * 80)
    print("\nTask: Analyze launching a budget-friendly electric bike for urban commuters\n")

    # Run the workflow and collect results
    output_evt: WorkflowOutputEvent | None = None
    async for event in workflow.run_stream(
        "We are launching a new budget-friendly electric bike for urban commuters."
    ):
        if isinstance(event, WorkflowOutputEvent):
            output_evt = event

    if output_evt:
        print("=" * 80)
        print("AGGREGATED RESULTS FROM ALL AGENTS")
        print("=" * 80)
        messages: list[ChatMessage] | Any = output_evt.data
        for i, msg in enumerate(messages, start=1):
            if msg.role == Role.ASSISTANT:
                name = msg.author_name if msg.author_name else "agent"
                print(f"\n--- {name.upper()} ---")
                print(msg.text)


if __name__ == "__main__":
    asyncio.run(main())
