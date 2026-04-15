# ai-builder

**Lightweight Python CLI framework for building composable AI tools, agents, and pipelines.**

No heavy IDE. No Docker for development. Just Python + Pydantic + `uv`.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## Install

```bash
# From GitHub
pip install git+https://github.com/rohaanuv/ai-builder.git

# With extras
pip install "ai-builder[rag,llm] @ git+https://github.com/rohaanuv/ai-builder.git"
```

## Create a Project

```bash
ai-builder create rag my-search          # RAG pipeline
ai-builder create tool my-cleaner        # Custom tool
ai-builder create agent-langchain my-bot # LangChain agent
ai-builder create agent-deep researcher  # Multi-agent system
ai-builder create pipeline my-etl        # Data pipeline
```

```bash
cd my-search
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install -e "."
```

## Use

```bash
ai-builder run . --input data/raw/       # Run a tool/pipeline
ai-builder run . --query "What is AI?"   # Run an agent
ai-builder visualize .                   # Flow diagram → browser
ai-builder serve .                       # Live dashboard
```

## Python API

```python
# Compose tools with the pipe operator
from ai_builder.tools import DocumentLoader, TextSplitter, Embedder, VectorStoreWriter

pipeline = DocumentLoader() | TextSplitter() | Embedder() | VectorStoreWriter()
pipeline.run(ToolInput(data="./docs/"))

# Agent-to-agent communication
from ai_builder import AgentBus, AgentMessage
bus = AgentBus()
bus.register_agent(agent_a)
response = bus.send(AgentMessage(sender="a", receiver="b", content="analyze this"))

# Tracing with Langfuse
from ai_builder.tracing import Tracer
Tracer.configure(backend="langfuse", public_key="pk-...", secret_key="sk-...")
```

## What's Inside

| Module | Description |
|--------|-------------|
| `ai_builder.core` | BaseTool, BaseAgent, Pipeline, Config, AgentBus (all Pydantic) |
| `ai_builder.tools` | 7 built-in tools: loader, splitter, embedder, vector_store, retriever, llm, web_search |
| `ai_builder.tracing` | Observability with Langfuse integration |
| `ai_builder.deploy` | Dockerfile, docker-compose, K8s manifest generators |
| `ai_builder.templates` | 5 scaffold generators (tool, agent-langchain, agent-deep, rag, pipeline) |
| `ai_builder.visualize` | Mermaid.js flow diagram generation |

## Every Scaffolded Project Includes

- `README.md` — end-to-end documentation
- `pyproject.toml` — uv-compatible, with all deps
- `requirements.txt` — includes `ipykernel` for notebooks
- `.env` — configuration
- `pipeline.yaml` — flow definition for visualization
- `Dockerfile` — multi-stage with BuildKit pip cache
- `docker-compose.yml` — local dev with model cache volume
- `k8s/` — deployment, service, configmap, HPA
- `tests/` — unit tests

## Optional Extras

```bash
pip install "ai-builder[rag]"       # sentence-transformers, faiss-cpu
pip install "ai-builder[llm]"       # openai, anthropic
pip install "ai-builder[agents]"    # langchain, langgraph
pip install "ai-builder[tracing]"   # langfuse
pip install "ai-builder[serve]"     # fastapi, uvicorn
pip install "ai-builder[all]"       # everything
```

## Full Documentation

See [`ai-builder/README.md`](ai-builder/README.md) for complete docs including:
- Detailed installation for new projects
- All template descriptions with generated code examples
- Core concepts (tool interface, piping, agent communication, tracing)
- Built-in tools reference
- Deployment guide (Docker + Kubernetes)
- Configuration reference

## Contributing

This project is licensed under **AGPL-3.0**. This means:

- You **can** use, modify, and distribute this software freely
- If you **modify** the source code, you **must** make your changes available under the same license
- If you run a modified version as a **network service**, you must provide the source code to users
- This ensures all improvements flow back to the community

See [LICENSE](LICENSE) for the full text.

## License

[GNU Affero General Public License v3.0](LICENSE) — Free to use, modify, and distribute. All modifications must be open-sourced.
