"""
Handoff Workflow Pattern Demo
=============================
Agents can transfer control to one another based on context.
Each agent can "handoff" the conversation to another agent with appropriate expertise.

Use cases:
- Customer support with specialized agents
- Expert systems with dynamic delegation
- Multi-domain problem solving
"""

import asyncio
from typing import Annotated, cast

from dotenv import load_dotenv
load_dotenv()

from agent_framework import (
    ChatMessage,
    HandoffBuilder,
    HandoffAgentUserRequest,
    HandoffSentEvent,
    RequestInfoEvent,
    Role,
    WorkflowOutputEvent,
    tool,
)
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.github import GitHubCopilotAgent
from azure.identity import DefaultAzureCredential


# Define tools for demonstration
@tool
def process_refund(order_number: Annotated[str, "Order number to process refund for"]) -> str:
    """Simulated function to process a refund for a given order number."""
    return f"✓ Refund processed successfully for order {order_number}. Amount will be credited in 3-5 business days."


@tool
def check_order_status(order_number: Annotated[str, "Order number to check status for"]) -> str:
    """Simulated function to check the status of a given order number."""
    return f"Order {order_number} status: Shipped on Jan 28, 2026. Expected delivery: Jan 31, 2026."


@tool
def process_return(order_number: Annotated[str, "Order number to process return for"]) -> str:
    """Simulated function to process a return for a given order number."""
    return f"✓ Return initiated for order {order_number}. Return label sent to your email."


async def main():
    # Initialize the Azure OpenAI chat client
    chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential())

    # Note: Handoff pattern requires ChatAgent with local tool execution support.
    # GitHubCopilotAgent doesn't support handoff directly, so we use Azure OpenAI agents
    # for the handoff workflow, and demonstrate GitHub Copilot in a final summary step.

    # Create specialized agents (all Azure OpenAI for handoff compatibility)
    triage_agent = chat_client.as_agent(
        instructions=(
            "You are frontline support triage. Your ONLY job is to understand the customer's issue "
            "and immediately handoff to the appropriate specialist. Do NOT try to solve the problem yourself. "
            "If the issue is about order status or shipping, handoff to order_agent. "
            "If the issue is about returns, handoff to return_agent. "
            "If the issue is about refunds, handoff to refund_agent. "
            "Always handoff - never respond directly to customer queries."
        ),
        description="Triage agent that routes customers to specialists.",
        name="triage_agent",
    )

    order_agent = chat_client.as_agent(
        instructions=(
            "You handle order and shipping inquiries. Use the check_order_status tool to look up orders. "
            "Be helpful and provide clear information about order status. "
            "If customer wants a return, handoff to return_agent. "
            "If customer wants a refund, handoff to refund_agent."
        ),
        description="Agent that handles order tracking and shipping issues.",
        name="order_agent",
        tools=[check_order_status],
    )

    return_agent = chat_client.as_agent(
        instructions=(
            "You manage product return requests. Use the process_return tool to initiate returns. "
            "Be empathetic and guide customers through the return process. "
            "After processing the return, if customer also wants a refund, handoff to refund_agent."
        ),
        description="Agent that handles return processing.",
        name="return_agent",
        tools=[process_return],
    )

    refund_agent = chat_client.as_agent(
        instructions=(
            "You process refund requests. Use the process_refund tool to process refunds. "
            "After processing the refund, thank the customer with 'Thank you for contacting us!' and end."
        ),
        description="Agent that handles refund requests.",
        name="refund_agent",
        tools=[process_refund],
    )

    # Build the handoff workflow with autonomous mode for demo
    workflow = (
        HandoffBuilder(
            name="customer_support_handoff",
            participants=[triage_agent, order_agent, return_agent, refund_agent],
        )
        .with_start_agent(triage_agent)  # Triage receives initial user input
        .with_termination_condition(
            # Terminate when conversation has enough messages or contains closing phrase
            lambda conversation: (
                len(conversation) >= 6 or
                (len(conversation) > 0 and "thank you for contacting" in conversation[-1].text.lower())
            )
        )
        .with_autonomous_mode(
            prompts={
                "triage_agent": "Route this to the appropriate specialist now.",
                "return_agent": "Process the return and then handoff to refund_agent.",
                "refund_agent": "Process the refund and complete the transaction.",
            },
            turn_limits={
                "triage_agent": 1,
                "return_agent": 2,
                "refund_agent": 2,
            }
        )
        .build()
    )

    # GitHub Copilot agent for post-workflow summary
    copilot_summarizer = GitHubCopilotAgent(
        default_options={
            "instructions": (
                "You are a customer service analyst. Given a support conversation transcript, "
                "provide a brief 2-3 sentence summary of what happened and the resolution. "
                "Be concise and professional."
            )
        },
        name="copilot_summarizer",
    )

    print("=" * 80)
    print("HANDOFF WORKFLOW: Customer Support with Specialized Agents")
    print("=" * 80)
    print("Agents: triage → return_agent → refund_agent")
    print("Post-analysis: GitHub Copilot Agent")
    print("=" * 80)
    print("\nCustomer Request: 'I need to return my order #12345 and get a refund'\n")

    # Collect conversation for Copilot analysis
    conversation_transcript = []

    # Collect all events and print in real-time
    async for event in workflow.run_stream("I need to return my order #12345 and get a refund"):
        # Print handoff events
        if isinstance(event, HandoffSentEvent):
            print(f"\n→ HANDOFF occurred")
        # Print agent responses as they happen
        elif isinstance(event, RequestInfoEvent) and isinstance(event.data, HandoffAgentUserRequest):
            print(f"\n[{event.source_executor_id}]:")
            for msg in event.data.agent_response.messages:
                if msg.text and msg.role == Role.ASSISTANT:
                    print(f"  {msg.text}")
        elif isinstance(event, WorkflowOutputEvent):
            # Print final conversation
            print("\n" + "=" * 80)
            print("WORKFLOW COMPLETE - TRANSCRIPT")
            print("=" * 80)
            messages = cast(list[ChatMessage], event.data)
            for msg in messages:
                # Skip autonomous mode prompts
                if msg.role == Role.USER:
                    text_lower = msg.text.lower()
                    if "autonomously" not in text_lower and "process the" not in text_lower and "route this" not in text_lower:
                        print(f"\n[Customer]: {msg.text}")
                        conversation_transcript.append(f"Customer: {msg.text}")
                elif msg.role == Role.ASSISTANT:
                    author = msg.author_name or "Agent"
                    print(f"\n[{author}]: {msg.text}")
                    conversation_transcript.append(f"{author}: {msg.text}")

    # Use GitHub Copilot to analyze the conversation
    print("\n" + "=" * 80)
    print("GITHUB COPILOT ANALYSIS")
    print("=" * 80)

    async with copilot_summarizer:
        transcript_text = "\n".join(conversation_transcript)
        analysis = await copilot_summarizer.run(
            f"Analyze this customer support conversation and provide a brief summary:\n\n{transcript_text}"
        )
        print(f"\n[GitHub Copilot]: {analysis}")


if __name__ == "__main__":
    asyncio.run(main())
