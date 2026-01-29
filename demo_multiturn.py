"""
Multi-Turn Conversations Demo
=============================
Maintain conversation context across multiple interactions using threads.
"""

import asyncio

from dotenv import load_dotenv
load_dotenv()

from agent_framework.github import GitHubCopilotAgent


async def main():
    print("=" * 80)
    print("MULTI-TURN CONVERSATIONS DEMO")
    print("=" * 80)

    agent = GitHubCopilotAgent(
        default_options={
            "instructions": (
                "You are a helpful assistant with a good memory. "
                "Remember details from our conversation and refer back to them when relevant. "
                "Keep responses concise."
            )
        },
        name="memory_assistant",
    )

    async with agent:
        # Create a new conversation thread
        thread = agent.get_new_thread()

        # First interaction
        print("\n[Turn 1]")
        print("User: My name is Alice and I'm learning Python.")
        result1 = await agent.run("My name is Alice and I'm learning Python.", thread=thread)
        print(f"Agent: {result1}")

        # Second interaction - agent should remember the context
        print("\n[Turn 2]")
        print("User: What programming language am I learning?")
        result2 = await agent.run("What programming language am I learning?", thread=thread)
        print(f"Agent: {result2}")

        # Third interaction - agent should still remember
        print("\n[Turn 3]")
        print("User: What's my name?")
        result3 = await agent.run("What's my name?", thread=thread)
        print(f"Agent: {result3}")

        # Fourth interaction - building on context
        print("\n[Turn 4]")
        print("User: Can you suggest a simple Python project for me?")
        result4 = await agent.run("Can you suggest a simple Python project for me?", thread=thread)
        print(f"Agent: {result4}")

    print("\n" + "=" * 80)
    print("Demo complete! The agent maintained context across all turns.")


if __name__ == "__main__":
    asyncio.run(main())
