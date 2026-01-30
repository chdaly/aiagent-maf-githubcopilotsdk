# GitHub Copilot Instructions for MAF-CopilotSDK Demo

## Project Overview

This is a demonstration project showcasing the integration of **Microsoft Agent Framework (MAF)** with **GitHub Copilot SDK**. The project demonstrates building multi-agent workflows that combine Azure OpenAI agents and GitHub Copilot agents.

### Key Technologies
- **Python 3.11+**
- **Microsoft Agent Framework** (`agent-framework`, `agent-framework-azure`, `agent-framework-github-copilot`)
- **Azure OpenAI Service** (via Azure AI Foundry)
- **GitHub Copilot SDK** (via Copilot CLI)
- **Azure Identity** (DefaultAzureCredential for authentication)

### Project Structure
This is a demo-focused codebase with flat file structure. Each Python file demonstrates a specific workflow pattern or feature:
- `MAF-CopilotSDK-Demo.py` - Sequential workflow (Writer → Reviewer)
- `workflow_concurrent.py` - Concurrent/parallel workflow pattern
- `workflow_handoff.py` - Dynamic delegation between specialized agents
- `workflow_groupchat.py` - Collaborative multi-agent conversations
- `demo_function_tools.py` - Custom function tools integration
- `demo_streaming.py` - Streaming response patterns
- `demo_multiturn.py` - Multi-turn conversation context

## Naming Conventions

### Variables and Parameters
- **Style**: `snake_case`
- **Examples**: `chat_client`, `location_lower`, `bill_amount`, `round_robin_selector`
- **Pattern**: Descriptive names that clearly indicate purpose

### Functions
- **Style**: `snake_case`
- **Examples**: `get_weather()`, `process_refund()`, `check_order_status()`, `calculate_tip()`
- **Pattern**: Verb-based names that describe action

### Agent Names
- **Style**: `snake_case` or descriptive strings
- **Examples**: `"writer"`, `"reviewer"`, `"order_agent"`, `"triage_agent"`, `"memory_assistant"`
- **Pattern**: Role-based names that describe the agent's purpose

### Constants and Data Structures
- **Style**: `snake_case`
- **Examples**: `weather_data`, `stock_data`, `default_options`
- **Pattern**: Use dictionaries for simulated/demo data

## Import Organization

Imports are organized in the following order:

1. **Standard library imports**
   ```python
   import asyncio
   from typing import Annotated, cast
   ```

2. **Third-party configuration** (always at the top of application imports)
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

3. **Agent Framework core imports**
   ```python
   from agent_framework import ChatMessage, Role, SequentialBuilder, WorkflowOutputEvent
   ```

4. **Azure and GitHub integration imports**
   ```python
   from agent_framework.azure import AzureOpenAIChatClient
   from agent_framework.github import GitHubCopilotAgent
   from azure.identity import DefaultAzureCredential
   ```

5. **Pydantic imports** (when needed for tools)
   ```python
   from pydantic import Field
   ```

**Key Rule**: `load_dotenv()` is always called immediately after importing it, typically on lines 4-5.

## Agent Framework Patterns

### Creating Azure OpenAI Agents

```python
chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential())

agent = chat_client.as_agent(
    instructions="Clear, specific instructions about the agent's role and behavior.",
    name="agent_name",
    tools=[tool1, tool2],  # Optional: list of tool functions
)
```

**Key Points**:
- Use `DefaultAzureCredential()` for Azure authentication (no explicit credentials in code)
- `instructions` parameter defines agent behavior
- `name` parameter is used for logging and identification
- `tools` parameter is optional and accepts a list of callable functions

### Creating GitHub Copilot Agents

```python
agent = GitHubCopilotAgent(
    default_options={"instructions": "Instructions for the agent."},
    name="agent_name",
    tools=[tool1, tool2],  # Optional: list of tool functions
)
```

**Key Points**:
- Instructions are passed via `default_options` dictionary with `"instructions"` key
- GitHub Copilot agents use the Copilot CLI in server mode
- Tool support is available but may have limitations compared to Azure OpenAI agents

### Agent Lifecycle Management

Always use async context managers for agent lifecycle:

```python
async with agent:
    result = await agent.run(query)
    # or for streaming:
    async for chunk in agent.run_stream(query):
        # process chunk
```

## Workflow Builder Patterns

### Sequential Workflow
Agents process tasks in a defined order, passing results from one to the next.

```python
from agent_framework import SequentialBuilder

workflow = SequentialBuilder().participants([agent1, agent2, agent3]).build()

async for event in workflow.run_stream(user_query):
    if isinstance(event, WorkflowOutputEvent):
        messages = cast(list[ChatMessage], event.data)
        # process messages
```

**Use cases**: Pipeline processing, multi-step refinement, writer → reviewer patterns

### Concurrent Workflow
Multiple agents work on the same task simultaneously and independently.

```python
from agent_framework import ConcurrentBuilder

workflow = ConcurrentBuilder().participants([agent1, agent2, agent3]).build()

async for event in workflow.run_stream(user_query):
    if isinstance(event, WorkflowOutputEvent):
        messages = cast(list[ChatMessage], event.data)
        # process messages
```

**Use cases**: Parallel analysis, ensemble reasoning, multi-perspective insights

### Handoff Workflow
Agents transfer control to one another based on context and expertise.

```python
from agent_framework import HandoffBuilder

workflow = (
    HandoffBuilder(
        name="customer_service",
        participants=[triage_agent, order_agent, refund_agent, return_agent]
    )
    .with_start_agent("triage_agent")
    .with_termination_condition(lambda msg: "DONE" in msg.text)
    .with_autonomous_mode(True)
    .build()
)
```

**Key Points**:
- Requires agents with handoff tool capabilities (typically Azure OpenAI agents)
- Use `with_start_agent()` to specify initial agent
- Use `with_termination_condition()` to define when workflow completes
- `with_autonomous_mode(True)` allows agents to handoff without user intervention

**Use cases**: Customer support routing, expert systems, dynamic delegation

### Group Chat Workflow
Multiple agents collaborate in a conversation coordinated by an orchestrator.

```python
from agent_framework import GroupChatBuilder

workflow = (
    GroupChatBuilder()
    .with_orchestrator(selection_func=round_robin_selector)
    .participants([writer, reviewer, editor])
    .with_termination_condition(lambda msg: "FINAL" in msg.text)
    .build()
)
```

**Use cases**: Iterative refinement, collaborative problem-solving, content review cycles

## Tool Definition Patterns

### Using @tool Decorator

```python
from agent_framework import tool

@tool
def function_name(
    param1: Annotated[str, "Description of param1"],
    param2: Annotated[int, "Description of param2"]
) -> str:
    """Function docstring describing what the tool does."""
    # implementation
    return result
```

### Using Pydantic Field Annotations

```python
from typing import Annotated
from pydantic import Field

def get_weather(
    location: Annotated[str, Field(description="The city name to get weather for")],
) -> str:
    """Get the current weather for a given location."""
    # implementation
    return result
```

**Key Points**:
- Always use `Annotated` for parameter type hints with descriptions
- Use either `@tool` decorator with string descriptions OR Pydantic `Field` for richer metadata
- Always include a docstring describing the tool's purpose
- Return type should be specified (typically `str` for LLM consumption)
- Tools should be deterministic and return string representations

### Tool Registration

```python
# Pass tools as a list to agent creation
agent = GitHubCopilotAgent(
    default_options={"instructions": "..."},
    tools=[get_weather, get_stock_price, calculate_tip],
    name="assistant",
)
```

## Type Hints and Annotations

### Required Type Annotations
- **Function parameters**: Always use type hints
- **Return types**: Always specify return types
- **Annotated types**: Use for tool parameters and complex types

### Common Patterns

```python
from typing import Annotated, cast

# Tool parameters with descriptions
param: Annotated[str, Field(description="...")]
param: Annotated[str, "Description string"]

# Return types
def function() -> str: ...
async def async_function() -> list[ChatMessage]: ...

# Type casting for framework events
messages = cast(list[ChatMessage], event.data)

# Type unions for event handling
event: WorkflowOutputEvent | None
```

## Async/Await Usage

### Consistent Async Patterns
All agent operations and workflows are asynchronous.

```python
async def main():
    # Agent execution
    result = await agent.run(query)
    
    # Streaming responses
    async for event in workflow.run_stream(query):
        # process event
    
    # Context managers
    async with agent:
        # agent operations

# Entry point
if __name__ == "__main__":
    asyncio.run(main())
```

**Rules**:
- All main functions are `async def main()`
- Use `await` for agent.run() calls
- Use `async for` for streaming operations
- Use `async with` for agent lifecycle management
- Entry point is always `asyncio.run(main())`

## Configuration Management

### Environment Variables
Use `python-dotenv` for loading environment variables:

```python
from dotenv import load_dotenv
load_dotenv()
```

**Required Environment Variables**:
- `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT` - Azure AI Foundry project endpoint
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI service endpoint
- `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` - Deployment name (e.g., "gpt-4o-mini")
- `COPILOT_CLI_PATH` - Path to GitHub Copilot CLI executable

### Authentication
Use Azure DefaultAzureCredential for all Azure services:

```python
from azure.identity import DefaultAzureCredential

chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential())
```

**No explicit credentials in code** - rely on Azure CLI authentication (`az login`)

## Error Handling

### Minimal Error Handling Philosophy
This demo codebase relies on the framework's built-in error handling and does not implement extensive try-except blocks.

### Safe Dictionary Access
Use `.get()` method for safe dictionary lookups with fallback values:

```python
weather_data.get(location_lower, f"Weather data not available for {location}")
```

### Framework Error Handling
Trust the agent framework to handle:
- API errors
- Network failures
- Authentication issues
- Tool execution errors

## Documentation Standards

### Module Docstrings
Every demo file should start with a module-level docstring:

```python
"""
Module Title
============
Brief description of what this module demonstrates.

Additional context or explanation.

Use cases:
- Use case 1
- Use case 2
"""
```

### Function Docstrings
All functions (especially tools) should have docstrings:

```python
def get_weather(location: Annotated[str, Field(description="...")]) -> str:
    """Get the current weather for a given location."""
    # implementation
```

**Pattern**: Simple, one-line docstrings describing the function's purpose in plain English.

### Comments
- Use sparingly - rely on readable code
- Section headers use `#` for logical grouping
- No inline comments - prefer self-documenting code

## Code Organization

### File Structure Pattern
Each demo file follows this structure:

1. **Imports** (organized as described above)
2. **Tool definitions** (if any)
3. **Main function** (`async def main()`)
4. **Entry point** (`if __name__ == "__main__": asyncio.run(main())`)

### Main Function Structure
```python
async def main():
    # 1. Initialize clients
    chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential())
    
    # 2. Create agents
    agent1 = chat_client.as_agent(...)
    agent2 = GitHubCopilotAgent(...)
    
    # 3. Build workflow
    workflow = SomeBuilder().participants([...]).build()
    
    # 4. Execute workflow
    async for event in workflow.run_stream(query):
        # 5. Process events
        if isinstance(event, WorkflowOutputEvent):
            # handle output
```

## Message Handling

### Processing Workflow Events

```python
async for event in workflow.run_stream(user_query):
    if isinstance(event, WorkflowOutputEvent):
        messages = cast(list[ChatMessage], event.data)
        for msg in messages:
            name = msg.author_name or ("assistant" if msg.role == Role.ASSISTANT else "user")
            print(f"[{name}]: {msg.text}\n")
```

**Pattern**:
- Filter events by type using `isinstance()`
- Cast event data to expected type using `cast()`
- Extract author name with fallback logic
- Format output with clear role identification

## Best Practices

### Agent Instructions
- Be clear and specific about agent role and behavior
- Use imperative mood ("You are...", "Do...", "Don't...")
- For triage/routing agents, emphasize immediate handoff over solving problems
- For specialized agents, define boundaries and handoff conditions

### Workflow Design
- Choose the right pattern for the use case:
  - **Sequential**: Linear, dependent steps
  - **Concurrent**: Independent, parallel analysis
  - **Handoff**: Dynamic routing based on expertise
  - **Group Chat**: Collaborative, iterative refinement

### Demo Data
- Use dictionaries for simulated data (weather, stocks, etc.)
- Provide realistic but clearly fake data
- Include variety in test cases

### Output Formatting
- Use separator lines for readability (`"=" * 80`, `"─" * 60`)
- Prefix messages with role/agent name in brackets
- Add blank lines between logical sections

## Common Patterns to Follow

1. **Always load environment variables first** (after imports)
2. **Use builder pattern for workflow construction** (method chaining)
3. **Prefer streaming over blocking calls** (`run_stream()` vs `run()`)
4. **Use async context managers for agents** (`async with agent:`)
5. **Type cast framework event data** for type safety
6. **Keep demo files focused on single pattern** (one concept per file)
7. **Follow the flat file structure** (no complex module hierarchies)

## Anti-Patterns to Avoid

1. ❌ Don't hardcode credentials or API keys
2. ❌ Don't use blocking I/O in async functions
3. ❌ Don't mix workflow patterns in a single demo
4. ❌ Don't create custom classes when framework classes exist
5. ❌ Don't add complex error handling in demos (keep it simple)
6. ❌ Don't forget to use `load_dotenv()` before framework imports
7. ❌ Don't use wildcard imports (`from module import *`)

## Testing and Running

### Run Individual Demos
```bash
python MAF-CopilotSDK-Demo.py
python workflow_concurrent.py
python demo_function_tools.py
```

### Prerequisites Checklist
- ✅ Python 3.11+ installed
- ✅ Virtual environment activated
- ✅ Dependencies installed (`pip install -r requirements.txt`)
- ✅ `.env` file configured with required variables
- ✅ Azure CLI authenticated (`az login`)
- ✅ GitHub Copilot CLI authenticated (`copilot` then `/login`)

## Framework-Specific Notes

### Microsoft Agent Framework
- Uses **builder pattern** for workflow construction
- Provides **streaming and non-streaming execution**
- Supports **tool calling** through function definitions
- Handles **authentication** via Azure credentials
- Manages **agent lifecycle** through context managers

### GitHub Copilot Integration
- Runs Copilot CLI in **server mode** (background process)
- Requires **CLI authentication** separate from GitHub account
- Instructions passed via `default_options` dictionary
- Limited handoff support (use Azure OpenAI for handoff workflows)

### Azure OpenAI Integration
- Uses **DefaultAzureCredential** for authentication
- Supports **all workflow patterns** (sequential, concurrent, handoff, group chat)
- Provides **rich tool calling** capabilities
- Integrates with **Azure AI Foundry** projects

## Version Information

This codebase uses preview/pre-release versions of the Agent Framework packages:
- `agent-framework`
- `agent-framework-azure`
- `agent-framework-github-copilot --pre`

**Note**: API patterns may change as the framework evolves from preview to stable releases.
