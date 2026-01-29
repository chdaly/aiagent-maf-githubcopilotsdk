"""
Streaming Responses Demo
========================
Stream responses as they are generated for a better user experience.
"""

import asyncio

from dotenv import load_dotenv
load_dotenv()

from agent_framework.github import GitHubCopilotAgent


async def main():
    print("=" * 80)
    print("STREAMING RESPONSES DEMO")
    print("=" * 80)

    agent = GitHubCopilotAgent(
        default_options={
            "instructions": "You are a helpful storyteller. Tell engaging, creative short stories."
        },
        name="storyteller",
    )

    async with agent:
        print("\nPrompt: Tell me a very short story about a robot learning to paint.\n")
        print("-" * 60)
        print("Agent: ", end="", flush=True)
        
        async for chunk in agent.run_stream("Tell me a very short story about a robot learning to paint."):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        
        print("\n" + "-" * 60)
        print("\nStreaming complete!")


if __name__ == "__main__":
    asyncio.run(main())
