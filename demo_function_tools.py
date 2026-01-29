"""
Function Tools Demo
====================
Extend agents with custom function tools to give them domain-specific capabilities.
This demo shows how to add tools to both Azure OpenAI and GitHub Copilot agents.
"""

import asyncio
from typing import Annotated

from dotenv import load_dotenv
load_dotenv()

from pydantic import Field
from agent_framework.github import GitHubCopilotAgent


# Define custom tools
def get_weather(
    location: Annotated[str, Field(description="The city name to get weather for")],
) -> str:
    """Get the current weather for a given location."""
    # Simulated weather data
    weather_data = {
        "seattle": "Rainy, 52°F (11°C)",
        "new york": "Partly cloudy, 45°F (7°C)",
        "san francisco": "Foggy, 58°F (14°C)",
        "los angeles": "Sunny, 72°F (22°C)",
        "chicago": "Windy, 38°F (3°C)",
    }
    location_lower = location.lower()
    return weather_data.get(location_lower, f"Weather data not available for {location}")


def get_stock_price(
    symbol: Annotated[str, Field(description="The stock ticker symbol (e.g., AAPL, MSFT)")],
) -> str:
    """Get the current stock price for a given ticker symbol."""
    # Simulated stock data
    stock_data = {
        "AAPL": "$185.42 (+1.2%)",
        "MSFT": "$378.91 (+0.8%)",
        "GOOGL": "$141.23 (-0.3%)",
        "AMZN": "$178.56 (+2.1%)",
        "TSLA": "$248.90 (-1.5%)",
    }
    return stock_data.get(symbol.upper(), f"Stock data not available for {symbol}")


def calculate_tip(
    bill_amount: Annotated[float, Field(description="The total bill amount in dollars")],
    tip_percentage: Annotated[float, Field(description="The tip percentage (e.g., 15, 18, 20)")],
) -> str:
    """Calculate the tip amount and total for a restaurant bill."""
    tip = bill_amount * (tip_percentage / 100)
    total = bill_amount + tip
    return f"Bill: ${bill_amount:.2f}, Tip ({tip_percentage}%): ${tip:.2f}, Total: ${total:.2f}"


async def main():
    print("=" * 80)
    print("FUNCTION TOOLS DEMO: GitHub Copilot Agent with Custom Tools")
    print("=" * 80)

    # Create a GitHub Copilot agent with custom tools
    agent = GitHubCopilotAgent(
        default_options={
            "instructions": (
                "You are a helpful assistant with access to weather, stock, and tip calculation tools. "
                "Use the appropriate tool when the user asks about weather, stocks, or calculating tips. "
                "Be concise and friendly in your responses."
            )
        },
        tools=[get_weather, get_stock_price, calculate_tip],
        name="assistant",
    )

    # Test queries
    queries = [
        "What's the weather like in Seattle?",
        "What's the current price of Microsoft stock?",
        "I have a $85.50 dinner bill. What's a 20% tip?",
    ]

    async with agent:
        for query in queries:
            print(f"\n{'─' * 60}")
            print(f"User: {query}")
            print(f"{'─' * 60}")
            
            result = await agent.run(query)
            print(f"Agent: {result}")


if __name__ == "__main__":
    asyncio.run(main())
