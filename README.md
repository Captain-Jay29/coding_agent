<p align="center">
  <img src="media/agentCode_testRun.gif" alt="AgentCode Demo" width="800" />
</p>

<pre align="center" style="font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.2; color: #1e3a8a; background: transparent;">
 █████╗  ██████╗ ███████╗███╗   ██╗████████╗ ██████╗ ██████╗ ██████╗ ███████╗
██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝██╔═══██╗██╔══██╗██╔════╝
███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ██║     ██║   ██║██║  ██║█████╗  
██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██║     ██║   ██║██║  ██║██╔══╝  
██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ╚██████╗╚██████╔╝██████╔╝███████╗
╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
</pre>

<p align="center" style="color: #2563eb; font-size: 1.2em; font-weight: 600; margin-top: 10px;">
  The AI coding agent that understands your workspace!
</p>

<p align="center" style="color: #1e40af; font-size: 1.0em; font-weight: 500;">
  Real-time streaming, contextual awareness, and intelligent workspace management.
</p>

<p align="center" style="color: #374151; font-size: 0.95em;">
  <strong>AgentCode brings powerful AI coding assistance with LangChain, featuring real-time streaming, multi-file project support, and seamless Git integration.</strong>
</p>
<br>
<br>

[![Python Versions](https://img.shields.io/pypi/pyversions/langchain.svg)](https://pypi.org/project/langchain/) [![License](https://img.shields.io/github/license/openai/openai-python.svg)](https://github.com/openai/openai-python/blob/main/LICENSE) [![LangChain](https://img.shields.io/badge/LangChain-0.1.0-blue.svg)](https://github.com/langchain-ai/langchain) [![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green.svg)](https://openai.com/) [![Streaming](https://img.shields.io/badge/Streaming-Real--time-orange.svg)](https://github.com/langchain-ai/langchain) [![Git Integration](https://img.shields.io/badge/Git-Integration-purple.svg)](https://git-scm.com/) [![Web UI](https://img.shields.io/badge/Web%20UI-Next.js%20%2B%20FastAPI-red.svg)](https://nextjs.org/) [![Evaluation](https://img.shields.io/badge/Evaluation-LangSmith-yellow.svg)](https://smith.langchain.com/)

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Run the agent:**
   ```bash
   python main.py
   ```

That's it! The agent runs with sensible defaults. See [Configuration](#configuration) for customization options.

## Features

- **🎯 Smart Code Operations**: Read, write, edit files with full workspace awareness and contextual understanding
- **⚡ Real-time Streaming**: Token-by-token responses with live tool execution feedback
- **🧠 Contextual Memory**: Remembers conversation history, file context, and references across sessions
- **🛠️ Multi-file Projects**: Create complete packages, run tests, and execute shell commands safely
- **🌐 Web UI**: Modern Next.js interface with live metrics, file tree, and SSE streaming
- **🔄 Git Integration**: Natural language branch creation, commits, and push workflows
- **📊 LangSmith Evaluation**: Full tracing with 20+ test cases and 7 custom evaluators
- **♻️ Auto-Retry Logic**: Automatically recovers from errors (configurable, up to 3 retries)

## CLI Reference

**Commands:**
`help` • `sessions` • `session <id>` • `info` • `config` • `multiline` • `clear` • `quit`

**Options:**
`--stream` / `--no-stream` • `--model <name>` • `--session-id <id>`

## Configuration

Configure via `.env` file or environment variables:

**Core Settings:**
- `OPENAI_API_KEY` - OpenAI API Key (required)
- `WORKSPACE_PATH` - Working directory (default: `./agent_runs`)
- `DEFAULT_MODEL` - Model to use (default: `gpt-4o-mini`)
- `MODEL_TEMPERATURE` - Randomness 0-1 (default: `0.0`)
- `MAX_HISTORY_MESSAGES` - Context limit (default: `20`)

**Git Integration:**
- `GIT_ENABLED` - Enable Git ops (default: `true`)
- `GIT_AUTO_PUSH` - Auto-push without confirmation (default: `false`)
- `GIT_MAIN_BRANCH` - Protected branch (default: `main`)

**LangSmith Tracing:**
- `LANGSMITH_TRACING` - Enable tracing (default: `false`)
- `LANGSMITH_API_KEY` - API key
- `LANGSMITH_PROJECT` - Project name

## Web UI

Modern web interface with real-time streaming, visual workspace management, and live metrics.

### Quick Start

```bash
# Start Backend (Terminal 1)
cd web_ui/backend && python server.py

# Start Frontend (Terminal 2)
cd web_ui/frontend && npm install && npm run dev
```

Open `http://localhost:3000` in your browser.

### Interface

- **Chat Panel**: Real-time streaming with SSE, session controls, auto-scroll
- **File Tree**: Live workspace structure with auto-refresh (3s intervals)
- **Metrics Panel**: 2x2 grid showing Turn, Messages, Files, and Latency

See `web_ui/README.md` for API endpoints and detailed documentation.

## Evaluation & LangSmith

Full observability with LangSmith tracing, metrics, and automated evaluation.

<p align="center">
  <img src="media/evals.png" alt="LangSmith Evaluation Dashboard" width="800" />
</p>

### Setup

```bash
# Configure environment
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=your-api-key
export LANGSMITH_PROJECT=coding_agent

# Create dataset and run evaluations
python evals/create_langsmith_dataset.py
python evals/run_evals.py
```

### What's Tracked

- **Session Metrics**: Session ID, turn number, message count, conversation history
- **Performance**: Latency, tool usage, file context, success rate
- **Smart Tags**: Auto-categorized by task type, complexity, and tool usage
- **Test Coverage**: 20+ test cases across 7 categories (CRUD, multi-file, error handling, Git)
- **Custom Evaluators**: 7 specialized functions for file creation, content correctness, and workflow validation

See `evals/README.md` for detailed documentation.

## Project Structure

```
coding-agent/
├── src/
│   ├── agent.py          # Main agent logic with contextual awareness
│   ├── tools.py          # File/shell operations with workspace support
│   ├── git_tools.py      # Git operations (branch, commit, push)
│   ├── state.py          # State management & conversation types
│   ├── memory.py         # Session persistence & management
│   └── config.py         # Configuration management
├── interface/
│   └── cli.py            # Rich CLI interface with multi-line support
├── web_ui/
│   ├── backend/
│   │   ├── server.py     # FastAPI backend with SSE streaming
│   │   ├── test_server.py # Backend test suite
│   │   └── README.md     # Backend documentation
│   ├── frontend/
│   │   ├── app/          # Next.js app directory
│   │   ├── components/   # React components (Chat, FileTree, Metrics)
│   │   └── README.md     # Frontend documentation
│   └── README.md         # Web UI overview
├── evals/
│   ├── datasets/
│   │   └── test_cases.py # 20+ test cases across 7 categories
│   ├── create_langsmith_dataset.py # Upload test cases to LangSmith
│   ├── run_evals.py      # Execute evaluation suite
│   ├── evaluators.py     # Custom evaluation functions
│   └── README.md         # Evaluation documentation
├── docs/
│   ├── langsmith_metrics.md # LangSmith metrics documentation
│   └── streaming_guidelines.md # Streaming implementation guide
├── agent_runs/           # Default workspace directory
├── .agent_memory/        # Session storage
├── main.py               # CLI entry point
├── requirements.txt       
├── .env                  # Configuration file (optional)
└── README.md
```

## Technical Stack

- **Core Agent**: LangChain (AgentExecutor with tool calling), `astream_events()` API for streaming
- **State Management**: In-memory with JSON persistence
- **CLI**: Rich + Click with async support
- **Web UI**: Next.js 15 + TypeScript + Tailwind CSS frontend, FastAPI + SSE backend
- **Evaluation**: LangSmith tracing with custom evaluators and smart tagging

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Command not found** | Commands run in workspace directory; use relative paths from workspace |
| **Session context lost** | Use `sessions` to list, `session <id>` to switch sessions |
| **Config not loading** | Check `.env` file in project root; use `config` command to verify |
| **Streaming slow** | Normal token-by-token behavior; use `--no-stream` for batch mode |
| **Git errors** | Ensure Git is installed with credentials; workspace must be in a Git repo |
| **Web UI not connecting** | Start backend on port 8000 before frontend on port 3000 |
| **LangSmith no traces** | Verify `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` are set |
