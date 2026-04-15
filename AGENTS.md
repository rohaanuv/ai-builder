# AGENTS.md — ai-builder

This document orients human contributors and AI coding assistants on the **ai-builder** framework.

## What is ai-builder?

A **lightweight Python CLI framework** for building composable AI tools, agents, and pipelines. No heavy GUI, no Docker dependency for development — just Python, Pydantic, and `uv`.

**Design principle:** Tools are functions (`Input → Output`). Composition is piping (`tool_a | tool_b`). Config is `.env` + Pydantic. Visualization is generated HTML. Deployment is Dockerfile + K8s manifests.

## Install from GitHub

```bash
pip install "git+https://github.com/rohaanuv/ai-builder.git#subdirectory=ai-builder"
ai-builder create rag my-project
cd my-project && uv venv && uv pip install -e "."
```

See `ai-builder/README.md` for full installation and usage documentation.

## Architecture

```
ai-builder/src/ai_builder/
├── core/              # Pydantic-typed base classes
│   ├── tool.py        # BaseTool[Input, Output] with | pipe operator
│   ├── agent.py       # BaseAgent (LangGraph wrapper)
│   ├── pipeline.py    # Pipeline: sequential tool composition
│   ├── config.py      # BaseConfig (pydantic-settings, .env)
│   └── communication.py  # AgentBus, AgentMessage (A2A)
├── tools/             # Built-in reusable tool library (one package per tool)
│   ├── loader/        # Document loader (PDF, DOCX, TXT, MD, HTML, XLSX, ...)
│   │   ├── __init__.py, main.py, config.py
│   ├── splitter/      # Recursive text chunking with IDs
│   │   ├── __init__.py, main.py, config.py
│   ├── embedder/      # sentence-transformers embeddings
│   │   ├── __init__.py, main.py, config.py
│   ├── vector_store/  # FAISS / Chroma / Qdrant
│   │   ├── __init__.py, main.py, config.py
│   ├── retriever/     # Vector similarity search
│   │   ├── __init__.py, main.py, config.py
│   ├── llm/           # OpenAI / Anthropic / Ollama
│   │   ├── __init__.py, main.py, config.py
│   └── web_search/    # Tavily search
│       ├── __init__.py, main.py, config.py
├── tracing/           # Observability (Langfuse integration)
├── deploy/            # Dockerfile, docker-compose, K8s generators
├── templates/         # 5 scaffold generators
├── visualize/         # Mermaid.js flow diagram generation
├── commands/          # CLI command implementations
└── cli.py             # Typer entry point
```

## CLI Commands

```bash
ai-builder create tool <name>             # Composable tool scaffold
ai-builder create agent-langchain <name>  # LangChain/LangGraph agent
ai-builder create agent-deep <name>       # Multi-agent research system
ai-builder create rag <name>              # RAG pipeline (built-in tools)
ai-builder create pipeline <name>         # Data pipeline (source→transform→sink)

ai-builder add                            # List available built-in tools
ai-builder add <tool>                     # Add a tool on demand + install deps
ai-builder run <path>                     # Execute a tool/agent/pipeline
ai-builder visualize <path>               # Generate flow diagram → browser
ai-builder serve <path>                   # Live web dashboard
ai-builder version                        # Show version
ai-builder list-templates                 # Show all templates
```

## Key Patterns

### Tool interface (Pydantic typed)
```python
from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput

class MyTool(BaseTool[MyInput, MyOutput]):
    name = "my-tool"
    def execute(self, inp: MyInput) -> MyOutput:
        return MyOutput(data=process(inp.data))
```

### Pipeline composition
```python
pipeline = loader | splitter | embedder | store
result = pipeline.run(ToolInput(data="./docs/"))
```

### Agent communication
```python
from ai_builder.core.communication import AgentBus, AgentMessage
bus = AgentBus()
bus.register_agent(agent_a)
bus.register_agent(agent_b)
response = bus.send(AgentMessage(sender="a", receiver="b", content="hello"))
```

### Tracing (Langfuse)
```python
from ai_builder.tracing import Tracer
Tracer.configure(backend="langfuse", public_key="pk-...", secret_key="sk-...")
```

## How AI assistants should work in this repo

1. **Respect the tool interface** — every tool is `BaseTool[InputT, OutputT]`, uses Pydantic, composable via `|`
2. **Built-in tools first** — use `ai_builder.tools.*` before writing custom tool code
3. **Config via pydantic-settings** — all configuration in `.env`, read by `BaseConfig` subclasses
4. **Templates are generators** — templates in `ai_builder/templates/` are Python functions that write files
5. **Deployment-ready** — every scaffold includes Dockerfile, docker-compose.yml, and k8s/ manifests
6. **Minimal deps** — core framework needs only typer, rich, pydantic, pyyaml. Heavy deps (torch, langchain) are optional extras
7. **uv-native** — all projects use `pyproject.toml` compatible with `uv sync`

## License

**AGPL-3.0** — If you modify this source code, you **must** make your changes available under the same license and push them to a public repository. Network use counts as distribution. See [LICENSE](LICENSE).
