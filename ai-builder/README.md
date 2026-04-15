# ai-builder

Lightweight Python CLI framework for building **composable AI tools, agents, and pipelines**.

No heavy IDE. No Docker for development. Just Python + Pydantic + `uv`.

```bash
pip install git+https://github.com/rohaanuv/ai-builder.git
ai-builder create rag my-search
cd my-search && uv sync
```

---

## Table of Contents

- [Installation](#installation)
  - [Starting a New Project](#starting-a-new-project-from-scratch)
- [Quick Start](#quick-start)
- [Commands](#commands)
- [Templates](#templates)
  - [Tool](#1-tool)
  - [RAG Pipeline](#2-rag-pipeline)
  - [LangChain Agent](#3-langchain-agent)
  - [Deep Research Agent](#4-deep-research-agent)
  - [Data Pipeline](#5-data-pipeline)
- [Core Concepts](#core-concepts)
  - [BaseTool (Input → Output)](#basetool-input--output)
  - [Pipeline Composition](#pipeline-composition)
  - [Agent-to-Agent Communication](#agent-to-agent-communication)
  - [Tracing & Observability](#tracing--observability)
- [Built-in Tools](#built-in-tools)
- [Visualization](#visualization)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Project Structure](#project-structure)

---

## Installation

### Prerequisites

- **Python 3.11+**
- **uv** (recommended) — install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Or just **pip**

### Install from GitHub

```bash
# With pip
pip install git+https://github.com/rohaanuv/ai-builder.git

# With uv
uv pip install git+https://github.com/rohaanuv/ai-builder.git

# With extras (e.g. RAG tools, LLM providers)
pip install "ai-builder[rag,llm] @ git+https://github.com/rohaanuv/ai-builder.git"
```

### Install from source (for contributors)

```bash
git clone https://github.com/rohaanuv/ai-builder.git
cd ai-builder
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e ".[all,dev]"
```

### Install from PyPI (once published)

```bash
pip install ai-builder                     # Core CLI only
pip install "ai-builder[rag]"              # + embeddings, FAISS
pip install "ai-builder[agents]"           # + LangChain, LangGraph
pip install "ai-builder[all]"              # Everything
```

### Starting a New Project from Scratch

Here's the complete flow when you start a brand new project on a fresh machine:

```bash
# 1. Install uv (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install ai-builder from GitHub
uv pip install git+https://github.com/rohaanuv/ai-builder.git

# 3. Verify installation
ai-builder version
ai-builder list-templates

# 4. Create your project (pick one)
ai-builder create rag my-doc-search          # RAG pipeline
ai-builder create tool my-custom-tool        # Custom tool
ai-builder create agent-langchain my-bot     # LangChain agent
ai-builder create agent-deep my-researcher   # Multi-agent system
ai-builder create pipeline my-etl            # Data pipeline

# 5. Enter your project
cd my-doc-search

# 6. Create venv and install dependencies
uv venv --python 3.12 .venv
source .venv/bin/activate       # Linux/Mac
# .venv\Scripts\activate        # Windows
uv pip install -e "."

# 7. Configure (edit .env with your API keys, settings)
nano .env

# 8. Run it
ai-builder run .                            # Run the tool/pipeline
ai-builder visualize .                      # See the flow diagram
ai-builder run . --query "your question"    # For agents

# 9. (Optional) Deploy
docker compose up --build                   # Docker
kubectl apply -f k8s/                       # Kubernetes
```

### Using ai-builder as a dependency in your own project

Add it to your project's `pyproject.toml`:

```toml
[project]
dependencies = [
    "ai-builder @ git+https://github.com/rohaanuv/ai-builder.git",
]

# Or with extras:
dependencies = [
    "ai-builder[rag,llm] @ git+https://github.com/rohaanuv/ai-builder.git",
]
```

Then `uv sync` or `pip install -e .` will pull it automatically.

### In a requirements.txt

```
git+https://github.com/rohaanuv/ai-builder.git
# or with extras:
ai-builder[rag,llm] @ git+https://github.com/rohaanuv/ai-builder.git
```

### Optional extras

| Extra | What it adds |
|-------|-------------|
| `rag` | sentence-transformers, faiss-cpu, langchain-text-splitters |
| `llm` | openai, anthropic |
| `agents` | langchain, langgraph |
| `tracing` | langfuse |
| `serve` | fastapi, uvicorn (for `ai-builder serve`) |
| `docs` | pdfplumber, python-docx, python-pptx, beautifulsoup4 |
| `chroma` | chromadb |
| `qdrant` | qdrant-client |
| `search` | tavily-python |
| `all` | All of the above |

---

## Quick Start

### Create a RAG pipeline (3 commands)

```bash
ai-builder create rag doc-search
cd doc-search
uv sync
```

This creates a complete project that imports built-in tools — no custom tool code needed:

```python
# doc-search/src/doc_search/main.py (generated)
from ai_builder.tools import DocumentLoader, TextSplitter, Embedder, VectorStoreWriter

pipeline = DocumentLoader() | TextSplitter() | Embedder() | VectorStoreWriter()
```

### Ingest and query

```python
from doc_search import ingest, query

# Add documents to data/raw/, then:
ingest("data/raw/")
result = query("What is the main finding?")
print(result.response)
```

### Create a custom tool

```bash
ai-builder create tool my-cleaner
cd my-cleaner
uv sync
ai-builder run . --input "messy text here"
```

---

## Commands

```bash
ai-builder create <template> <name>   # Scaffold a new project
ai-builder run <path> [--input|-i]     # Run a tool, agent, or pipeline
ai-builder run <path> [--query|-q]     # Run an agent with a query
ai-builder visualize <path>            # Generate flow diagram → opens browser
ai-builder visualize <path> --no-open  # Generate without opening
ai-builder visualize <path> -f mermaid # Output raw Mermaid code
ai-builder serve <path> [-p 8501]      # Start live web dashboard
ai-builder version                     # Show version
ai-builder list-templates              # Show all available templates
```

---

## Templates

### 1. Tool

```bash
ai-builder create tool <name>
```

Creates a composable tool with typed Pydantic input/output:

```
my-tool/
├── src/my_tool/
│   ├── main.py          # BaseTool implementation
│   └── config.py         # Pydantic settings
├── tests/test_main.py
├── pipeline.yaml          # For visualization
├── Dockerfile
├── docker-compose.yml
├── k8s/                   # Kubernetes manifests
├── .env
├── requirements.txt       # includes ipykernel
├── pyproject.toml
└── README.md
```

**Generated code pattern:**

```python
from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput

class MyToolInput(ToolInput):
    data: str = ""

class MyToolOutput(ToolOutput):
    data: str = ""

class MyTool(BaseTool[MyToolInput, MyToolOutput]):
    name = "my-tool"

    def execute(self, inp: MyToolInput) -> MyToolOutput:
        return MyToolOutput(data=inp.data.upper())

tool = MyTool()
```

---

### 2. RAG Pipeline

```bash
ai-builder create rag <name>
```

Pre-wired pipeline using **built-in tools** — no custom tool code:

```python
from ai_builder.tools import DocumentLoader, TextSplitter, Embedder, VectorStoreWriter
pipeline = DocumentLoader() | TextSplitter() | Embedder() | VectorStoreWriter()
```

**Includes:**
- `ingest(source_dir)` — load → split → embed → store
- `query(question)` — retrieve → (optional) LLM generate
- Configurable via `.env` (embedding model, vector provider, chunk size, etc.)

**Supports:** FAISS (default), Chroma, Qdrant | 7+ embedding models | PDF, DOCX, PPTX, TXT, MD, HTML, RTF

---

### 3. LangChain Agent

```bash
ai-builder create agent-langchain <name>
```

LangGraph-based agent with:
- Tool calling loop (agent → tools → agent)
- Custom tools directory (`src/<pkg>/tools/`)
- System prompt (`prompts/system.md`)
- Agent-to-agent communication via `AgentBus`

---

### 4. Deep Research Agent

```bash
ai-builder create agent-deep <name>
```

Multi-agent system: **Supervisor → Researcher → Analyst → Writer**

- Sub-agents communicate via `AgentBus` (typed Pydantic messages)
- Supervisor routes queries to specialists
- Configurable max iterations
- Tavily web search integration

---

### 5. Data Pipeline

```bash
ai-builder create pipeline <name>
```

ETL pipeline: **Source → Transform → Aggregate → Sink**

- Reads CSV/JSON from `data/input/`
- Outputs to `data/output/`
- Each step is a composable `BaseTool`

---

## Core Concepts

### BaseTool (Input → Output)

Every tool is a typed function. Input and output are Pydantic models:

```python
from ai_builder import BaseTool, ToolInput, ToolOutput

class Doubler(BaseTool[ToolInput, ToolOutput]):
    name = "doubler"

    def execute(self, inp: ToolInput) -> ToolOutput:
        return ToolOutput(data=inp.data * 2)
```

Run it:
```python
result = Doubler().run(ToolInput(data="abc"))
# result.data == "abcabc"
# result.success == True
```

### Pipeline Composition

Tools compose with the `|` (pipe) operator:

```python
pipeline = tool_a | tool_b | tool_c
result = pipeline.run(ToolInput(data="start"))

# Each step's output becomes the next step's input
# result.steps shows per-step timing and status
# result.final_output is the last step's output
```

Pipelines can also be defined in YAML and visualized:

```yaml
# pipeline.yaml
name: my-pipeline
steps:
  - name: loader
    tool: loader
    config:
      source: data/raw/
  - name: splitter
    tool: splitter
    config:
      chunk_size: 1000
```

### Agent-to-Agent Communication

Agents communicate via typed messages through an `AgentBus`:

```python
from ai_builder import AgentBus, AgentMessage

bus = AgentBus()

# Register agents
bus.register_agent(researcher)   # BaseAgent instance
bus.register_agent(writer)       # BaseAgent instance

# Send a message
response = bus.send(AgentMessage(
    sender="coordinator",
    receiver="researcher",
    content="Find data on climate change",
))
print(response.content)  # Researcher's response

# Broadcast events
from ai_builder.core.communication import AgentEvent
bus.broadcast(AgentEvent(sender="researcher", event="data_ready", payload={...}))

# Discover registered agents
cards = bus.discover()  # Returns AgentCard list
```

**Message types:** `request`, `response`, `event`, `error`
**Features:** correlation IDs for request-response tracking, message history, agent discovery via `AgentCard`

### Tracing & Observability

Built-in tracing with optional **Langfuse** export:

```python
from ai_builder.tracing import Tracer, trace, traced_tool, traced_pipeline

# Configure backend (console or langfuse)
Tracer.configure(backend="langfuse", public_key="pk-...", secret_key="sk-...")

# Decorator
@trace("my-operation")
def expensive_work():
    ...

# Context manager
with Tracer.span("embedding") as span:
    span.set_input({"count": 100})
    result = embed(texts)
    span.set_output({"dimension": 384})

# Auto-trace a tool or pipeline
traced_tool(my_tool)
traced_pipeline(my_pipeline)

# View collected spans
Tracer.get_spans()   # list of span dicts
Tracer.flush()       # send to Langfuse
```

---

## Built-in Tools

These tools are part of `ai_builder.tools` and can be imported into any project:

| Tool | Import | Description |
|------|--------|-------------|
| `DocumentLoader` | `from ai_builder.tools import DocumentLoader` | Load PDF, DOCX, PPTX, TXT, MD, HTML, RTF |
| `TextSplitter` | `from ai_builder.tools import TextSplitter` | Recursive chunking with overlap + chunk IDs |
| `Embedder` | `from ai_builder.tools import Embedder` | sentence-transformers (7+ models) |
| `VectorStoreWriter` | `from ai_builder.tools import VectorStoreWriter` | FAISS / Chroma / Qdrant |
| `Retriever` | `from ai_builder.tools import Retriever` | Similarity search across all providers |
| `LLMTool` | `from ai_builder.tools import LLMTool` | OpenAI / Anthropic / Ollama |
| `WebSearchTool` | `from ai_builder.tools import WebSearchTool` | Tavily web search |

**Example — full RAG in 5 lines:**

```python
from ai_builder.tools import DocumentLoader, TextSplitter, Embedder, VectorStoreWriter, Retriever
from ai_builder.core.tool import ToolInput

pipeline = DocumentLoader() | TextSplitter() | Embedder() | VectorStoreWriter()
pipeline.run(ToolInput(data="./my-docs/"))

results = Retriever().run(ToolInput(data="what is machine learning?"))
```

---

## Visualization

Every project has a `pipeline.yaml` that defines the flow. Visualize it:

```bash
ai-builder visualize .              # Interactive HTML → opens browser
ai-builder visualize . --no-open    # Generate without opening
ai-builder visualize . -f mermaid   # Raw Mermaid code
```

The generated HTML page shows:
- **Mermaid.js flow diagram** (dark themed, interactive)
- **Step sidebar** with configuration details
- Works offline (CDN-loaded Mermaid.js)

For a live dashboard:
```bash
ai-builder serve . --port 8501      # FastAPI dashboard at localhost:8501
```

---

## Deployment

Every scaffolded project includes production-ready deployment files:

### Docker

```bash
docker compose up --build
```

Generated `Dockerfile` uses:
- Multi-stage build (`python:3.12-slim`)
- BuildKit pip cache (survives rebuilds)
- HuggingFace model cache volume
- Non-root user (production)

### Kubernetes

```bash
kubectl apply -f k8s/
```

Generated manifests:
- `k8s/deployment.yaml` — Pod spec with resource limits, readiness probe
- `k8s/service.yaml` — ClusterIP service
- `k8s/configmap.yaml` — Environment configuration
- `k8s/hpa.yaml` — Horizontal Pod Autoscaler (CPU/memory)

---

## Configuration

All projects use **pydantic-settings** which auto-reads `.env` files:

```python
from ai_builder.core.config import BaseConfig

class MyConfig(BaseConfig):
    project_name: str = "my-project"
    openai_api_key: str = ""          # reads OPENAI_API_KEY from .env
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000
```

```env
# .env
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
CHUNK_SIZE=500
```

Fields automatically map: `my_field` ↔ `MY_FIELD` env var.

---

## Project Structure

```
ai-builder/                        # The framework itself
├── pyproject.toml                 # Package definition (uv-compatible)
├── README.md                      # This file
├── src/ai_builder/
│   ├── cli.py                     # Typer CLI entry point
│   ├── core/                      # Base classes (Pydantic)
│   │   ├── tool.py                #   BaseTool[Input, Output]
│   │   ├── agent.py               #   BaseAgent
│   │   ├── pipeline.py            #   Pipeline (sequential composition)
│   │   ├── config.py              #   BaseConfig (pydantic-settings)
│   │   └── communication.py       #   AgentBus, AgentMessage (A2A)
│   ├── tools/                     # Built-in reusable tools
│   │   ├── loader.py              #   Document loader
│   │   ├── splitter.py            #   Text splitter
│   │   ├── embedder.py            #   Embedding (sentence-transformers)
│   │   ├── vector_store.py        #   FAISS / Chroma / Qdrant
│   │   ├── retriever.py           #   Vector search
│   │   ├── llm.py                 #   OpenAI / Anthropic / Ollama
│   │   └── web_search.py          #   Tavily search
│   ├── tracing/                   # Observability
│   │   └── tracer.py              #   Spans, @trace, Langfuse export
│   ├── deploy/                    # Deployment file generators
│   │   └── generators.py          #   Dockerfile, K8s manifests
│   ├── templates/                 # 5 scaffold generators
│   │   ├── tool.py
│   │   ├── agent_langchain.py
│   │   ├── agent_deep.py
│   │   ├── rag.py
│   │   └── pipeline.py
│   ├── visualize/                 # Flow diagram generation
│   │   ├── mermaid.py             #   Pipeline → Mermaid.js
│   │   └── html_template.py       #   Interactive HTML page
│   └── commands/                  # CLI implementations
│       ├── create.py
│       ├── run.py
│       ├── visualize.py
│       └── serve.py
└── tests/
```

---

## License

[GNU Affero General Public License v3.0 (AGPL-3.0)](../LICENSE)

You are free to use, modify, and distribute this software. If you modify the source code, you **must** make your changes available under the same license and push them to a public repository. If you run a modified version as a network service, you must provide the source to your users. This ensures all improvements benefit the community.
