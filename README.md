# Microsoft Agent Framework + GitHub Copilot SDK Demo

This demo showcases the integration of Microsoft Agent Framework with GitHub Copilot SDK to build multi-agent workflows that combine Azure OpenAI and GitHub Copilot agents.

## Overview

The demo creates a sequential workflow where:
1. **Writer Agent** (Azure OpenAI) - Creates marketing copy based on a prompt
2. **Reviewer Agent** (GitHub Copilot) - Reviews and provides feedback on the writer's output

## Prerequisites

- Python 3.11+
- Node.js (for GitHub Copilot CLI)
- Azure subscription with Azure AI Foundry project
- GitHub account with Copilot access
- Azure CLI (`az login` for authentication)

## Setup Instructions

### 1. Clone and Create Virtual Environment

```powershell
cd C:\FY26\AIGuild\Demo\MAF-CopilotSDK
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file with the following variables:

```env
# Azure AI Foundry Configuration
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://<your-resource>.services.ai.azure.com/api/projects/<your-project>

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://<your-resource>.services.ai.azure.com
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4.1-mini

# GitHub Copilot CLI path (update with your actual path)
COPILOT_CLI_PATH=C:\Users\<username>\AppData\Roaming\npm\copilot.cmd
```

### 4. Authenticate Azure CLI

```powershell
az login
```

### 5. Install and Authenticate GitHub Copilot CLI

Install the Copilot CLI (if not already installed):
```powershell
copilot --version
```

If not installed, it will prompt you to install. Once installed, authenticate:

```powershell
copilot
```

In the interactive session, type `/login` and follow the device code flow at https://github.com/login/device

### 6. Run the Demo

```powershell
.\venv\Scripts\Activate.ps1
python .\MAF-CopilotSDK-Demo.py
```

## Expected Output

```
[user]: Write a tagline for a budget-friendly electric bike.

[writer]: Ride Smart, Spend Less—Your Electric Freedom Awaits!

[assistant]: That's a great tagline! It clearly communicates the value proposition...
```

## Project Structure

```
MAF-CopilotSDK/
├── MAF-CopilotSDK-Demo.py   # Sequential workflow demo (original)
├── workflow_concurrent.py    # Concurrent workflow pattern
├── workflow_handoff.py       # Handoff workflow pattern
├── workflow_groupchat.py     # Group chat workflow pattern
├── demo_function_tools.py    # Custom function tools demo
├── demo_streaming.py         # Streaming responses demo
├── demo_multiturn.py         # Multi-turn conversations demo
├── .env                      # Environment variables (not in source control)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── venv/                     # Python virtual environment
```

## Workflow Patterns

### 1. Sequential Workflow (`MAF-CopilotSDK-Demo.py`)
Agents process tasks in a defined order, passing results from one to the next.
```powershell
python MAF-CopilotSDK-Demo.py
```
**Agents:** Writer (Azure OpenAI) → Reviewer (GitHub Copilot)

### 2. Concurrent Workflow (`workflow_concurrent.py`)
Multiple agents work on the same task simultaneously and independently.
```powershell
python workflow_concurrent.py
```
**Agents:** Researcher, Marketer, Tech Reviewer (GitHub Copilot) - all in parallel
**Use cases:** Parallel analysis, ensemble reasoning, multi-perspective insights

### 3. Handoff Workflow (`workflow_handoff.py`)
Agents transfer control to one another based on context and expertise. Includes GitHub Copilot for post-workflow analysis.
```powershell
python workflow_handoff.py
```
**Agents:** Triage → Return Agent → Refund Agent + GitHub Copilot Summarizer
**Use cases:** Customer support, expert systems, dynamic delegation

### 4. Group Chat Workflow (`workflow_groupchat.py`)
Multiple agents collaborate in a conversation coordinated by an orchestrator.
```powershell
python workflow_groupchat.py
```
**Agents:** Writer → Reviewer (GitHub Copilot) → Editor with round-robin orchestration
**Use cases:** Iterative refinement, collaborative problem-solving, content review

## Additional Demos

### Function Tools (`demo_function_tools.py`)
Extend agents with custom function tools for domain-specific capabilities.
```powershell
python demo_function_tools.py
```

### Streaming Responses (`demo_streaming.py`)
Stream responses as they are generated for better UX.
```powershell
python demo_streaming.py
```

### Multi-Turn Conversations (`demo_multiturn.py`)
Maintain conversation context across multiple interactions.
```powershell
python demo_multiturn.py
```

## Key Packages

| Package | Description |
|---------|-------------|
| `agent-framework` | Microsoft Agent Framework core |
| `agent-framework-azure` | Azure OpenAI integration |
| `agent-framework-github-copilot` | GitHub Copilot integration (preview) |
| `azure-identity` | Azure authentication |
| `python-dotenv` | Environment variable loading |

## How It Works

1. **AzureOpenAIChatClient** creates an agent using Azure OpenAI models with `DefaultAzureCredential` for authentication
2. **GitHubCopilotAgent** creates an agent that uses the GitHub Copilot CLI in server mode
3. **Workflow Builders** orchestrate agents:
   - `SequentialBuilder` - pipeline execution (writer → reviewer)
   - `ConcurrentBuilder` - parallel execution
   - `HandoffBuilder` - dynamic delegation between agents
   - `GroupChatBuilder` - collaborative conversations with orchestration
4. The workflows stream events as each agent processes the input

## GitHub Copilot Integration

GitHub Copilot is integrated in multiple demos:
- **Sequential**: Copilot as the reviewer agent
- **Concurrent**: Copilot as the tech reviewer (parallel with other agents)
- **Handoff**: Copilot as post-workflow summarizer/analyzer
- **Group Chat**: Copilot as the reviewer in the collaborative chain

## Troubleshooting

### "No module named 'agent_framework.github'"
Ensure you have the latest preview packages:
```powershell
pip install --upgrade agent-framework agent-framework-github-copilot --pre
```

### "Failed to start GitHub Copilot client"
- Verify `COPILOT_CLI_PATH` in `.env` points to the correct location
- Run `where.exe copilot` to find the CLI path
- Ensure you're authenticated with `/login`

### "No authentication information found"
Run `copilot` interactively and use `/login` to authenticate

### Azure authentication errors
- Run `az login` to refresh credentials
- Verify your Azure subscription has access to the AI Foundry project

## References

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [GitHub Copilot SDK](https://github.com/github/copilot-sdk)
- [Build AI Agents with GitHub Copilot SDK and Microsoft Agent Framework](https://devblogs.microsoft.com/semantic-kernel/build-ai-agents-with-github-copilot-sdk-and-microsoft-agent-framework/)
