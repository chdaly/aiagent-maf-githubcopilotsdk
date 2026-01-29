"""
Group Chat Workflow Pattern Demo
================================
Multiple agents collaborate in a conversation coordinated by an orchestrator.
The orchestrator determines which agent speaks next using various strategies.

Use cases:
- Iterative content refinement (writer + reviewer)
- Collaborative problem-solving
- Multi-perspective analysis with discussion
- Quality assurance workflows
"""

import asyncio
from typing import cast

from dotenv import load_dotenv
load_dotenv()

from agent_framework import (
    AgentRunUpdateEvent,
    ChatMessage,
    GroupChatBuilder,
    GroupChatState,
    Role,
    WorkflowOutputEvent,
)
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.github import GitHubCopilotAgent
from azure.identity import DefaultAzureCredential


async def main():
    # Initialize the Azure OpenAI chat client
    chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential())

    # Create a writer agent (Azure OpenAI)
    writer = chat_client.as_agent(
        instructions=(
            "You are a creative copywriter. Generate catchy marketing slogans and taglines. "
            "Be concise and impactful. When you receive feedback, incorporate it into an improved version. "
            "Keep responses under 100 words."
        ),
        name="Writer",
    )

    # Create a reviewer agent (GitHub Copilot)
    reviewer = GitHubCopilotAgent(
        default_options={
            "instructions": (
                "You are a marketing reviewer. Evaluate slogans for clarity, impact, and brand alignment. "
                "Provide constructive feedback or approval. Be specific about what works and what could improve. "
                "If the slogan is excellent, say 'APPROVED' and explain why. Keep responses under 100 words."
            )
        },
        name="Reviewer",
    )

    # Create an editor agent (Azure OpenAI)
    editor = chat_client.as_agent(
        instructions=(
            "You are an editor who polishes final copy. You take approved slogans and create "
            "the final polished version with a brief explanation of why it works. "
            "Keep responses under 100 words."
        ),
        name="Editor",
    )

    # Define a round-robin selector for speaker selection
    def round_robin_selector(state: GroupChatState) -> str:
        """Select speakers in order: Writer -> Reviewer -> Writer -> Reviewer -> Editor"""
        participant_names = ["Writer", "Reviewer", "Writer", "Reviewer", "Editor"]
        round_idx = state.current_round % len(participant_names)
        return participant_names[round_idx]

    # Build the group chat workflow
    workflow = (
        GroupChatBuilder()
        .with_orchestrator(selection_func=round_robin_selector)
        .participants([writer, reviewer, editor])
        # Terminate after 5 rounds or when editor has spoken
        .with_termination_condition(
            lambda conversation: (
                len([m for m in conversation if m.role == Role.ASSISTANT]) >= 5 or
                any(m.author_name == "Editor" for m in conversation if m.role == Role.ASSISTANT)
            )
        )
        .build()
    )

    print("=" * 80)
    print("GROUP CHAT WORKFLOW: Iterative Content Creation")
    print("=" * 80)
    print("\nTask: Create a slogan for an eco-friendly electric vehicle\n")
    print("-" * 80)

    last_author = None

    # Run the workflow and stream responses
    async for event in workflow.run_stream("Create a slogan for an eco-friendly electric vehicle"):
        if isinstance(event, AgentRunUpdateEvent):
            # Print agent name when it changes
            if event.executor_id != last_author:
                if last_author is not None:
                    print("\n")
                print(f"\n[{event.executor_id}]: ", end="", flush=True)
                last_author = event.executor_id
            # Stream the response text
            if event.data:
                print(event.data, end="", flush=True)
        elif isinstance(event, WorkflowOutputEvent):
            final_conversation = cast(list[ChatMessage], event.data)
            print("\n\n" + "=" * 80)
            print("FINAL CONVERSATION SUMMARY")
            print("=" * 80)
            for msg in final_conversation:
                if msg.role == Role.ASSISTANT:
                    print(f"\n[{msg.author_name}]:")
                    print(f"  {msg.text[:200]}..." if len(msg.text) > 200 else f"  {msg.text}")


if __name__ == "__main__":
    asyncio.run(main())
