"""Template: ai-builder create rag <name> — imports from built-in tools library."""

from pathlib import Path

from ai_builder.templates import register, _to_snake, _write
from ai_builder.deploy.generators import (
    generate_dockerfile, generate_docker_compose,
    generate_k8s_deployment, generate_k8s_service, generate_k8s_configmap, generate_k8s_hpa,
)


@register("rag")
def generate(name: str, target: Path) -> None:
    pkg = _to_snake(name)
    cls = "".join(w.capitalize() for w in name.split("-"))

    _write(target / "pyproject.toml", f"""\
[project]
name = "{name}"
version = "0.1.0"
description = "RAG pipeline: {name}"
requires-python = ">=3.11"
dependencies = [
    "ai-builder @ git+https://github.com/rohaanuv/ai-builder.git#subdirectory=ai-builder",
    "pydantic>=2.0",
]

[project.optional-dependencies]
embeddings = ["sentence-transformers>=3.3"]
faiss = ["faiss-cpu>=1.9"]
docs = [
    "pdfplumber>=0.11",
    "python-docx>=1.1",
    "python-pptx>=1.0",
    "beautifulsoup4>=4.12",
    "striprtf>=0.0.26",
]
llm = ["openai>=1.0", "anthropic>=0.40"]
chroma = ["chromadb>=0.5"]
qdrant = ["qdrant-client>=1.12"]
langfuse = ["langfuse>=2.0"]
dev = ["pytest>=8.0", "ipykernel>=6.29"]
all = ["{name}[embeddings,faiss,docs,llm,langfuse]"]

[tool.setuptools.packages.find]
where = ["src"]

[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"
""")

    _write(target / "requirements.txt", f"""\
# Core (installed automatically)
ai-builder @ git+https://github.com/rohaanuv/ai-builder.git#subdirectory=ai-builder
pydantic>=2.0

# Add packages as needed — install with: uv pip install <package>
# Or install a group: uv pip install -e ".[embeddings]"
#
# Embeddings:      uv pip install sentence-transformers
# Vector store:    uv pip install faiss-cpu
# PDF support:     uv pip install pdfplumber
# DOCX support:    uv pip install python-docx
# PPTX support:    uv pip install python-pptx
# HTML parsing:    uv pip install beautifulsoup4
# RTF support:     uv pip install striprtf
# OpenAI LLM:     uv pip install openai
# Anthropic LLM:  uv pip install anthropic
# Tracing:        uv pip install langfuse
# Chroma DB:      uv pip install chromadb
# Qdrant DB:      uv pip install qdrant-client
# Notebooks:      uv pip install ipykernel
#
# Or install everything at once: uv pip install -e ".[all]"
""")

    _write(target / ".env", f"""\
# {name} configuration
PROJECT_NAME={name}
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_PROVIDER=faiss
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=5
LOG_LEVEL=INFO

# LLM (optional — for RAG generation step)
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=

# Langfuse tracing (optional)
# LANGFUSE_PUBLIC_KEY=
# LANGFUSE_SECRET_KEY=
# LANGFUSE_HOST=https://cloud.langfuse.com
""")

    _write(target / "src" / pkg / "__init__.py", f"""\
\"\"\"
{name} — RAG pipeline built with ai-builder.

Usage:
    from {pkg} import ingest, query, pipeline
\"\"\"

from {pkg}.main import pipeline, ingest, query

__all__ = ["pipeline", "ingest", "query"]
""")

    _write(target / "src" / pkg / "main.py", f"""\
\"\"\"
{name} — RAG pipeline using ai-builder built-in tools.

The pipeline imports pre-built tools and composes them:
    loader | splitter | embedder | vector_store

No need to implement tool logic — just configure and run.

Usage:
    # CLI
    ai-builder run .

    # Python
    from {pkg} import ingest, query
    ingest("./data/raw/")
    result = query("What is the main topic?")
\"\"\"

from pathlib import Path

from ai_builder.core.tool import ToolInput
from ai_builder.core.agent import AgentOutput
from ai_builder.tools import (
    DocumentLoader, LoaderConfig,
    TextSplitter, SplitterConfig,
    Embedder, EmbedderConfig,
    VectorStoreWriter, VectorStoreConfig,
    Retriever, RetrieverConfig, RetrieverInput,
    LLMTool, LLMConfig,
)
from ai_builder.tracing import Tracer, traced_pipeline

from {pkg}.config import {cls}Config

# ── Load configuration from .env ──
config = {cls}Config()

# ── Instantiate built-in tools with project config ──
loader = DocumentLoader(LoaderConfig(source_dir=str(config.data_dir / "raw")))

splitter = TextSplitter(SplitterConfig(
    chunk_size=config.chunk_size,
    chunk_overlap=config.chunk_overlap,
))

embedder = Embedder(EmbedderConfig(model_id=config.embedding_model))

store = VectorStoreWriter(VectorStoreConfig(
    provider=config.vector_provider,
    store_path=str(config.vector_store_path),
    collection_name=config.collection_name,
))

retriever = Retriever(RetrieverConfig(
    provider=config.vector_provider,
    store_path=str(config.vector_store_path),
    collection_name=config.collection_name,
    top_k=config.top_k,
    embedding_model=config.embedding_model,
))

llm = LLMTool(LLMConfig(
    provider=config.llm_provider,
    model=config.llm_model,
    system_prompt="Answer the question using only the provided context. If unsure, say so.",
))

# ── Compose the ingestion pipeline ──
pipeline = loader | splitter | embedder | store


def ingest(source_dir: str | Path = "data/raw/") -> None:
    \"\"\"Ingest documents into the vector store.\"\"\"
    Tracer.new_trace(f"{{config.project_name}}:ingest")
    traced = traced_pipeline(pipeline)

    result = traced.run(ToolInput(data=str(source_dir)))
    Tracer.flush()

    if result.success:
        print(f"Ingested successfully ({{result.total_duration_ms:.0f}}ms)")
        for step in result.steps:
            print(f"  {{step.step_name}}: {{step.duration_ms:.0f}}ms")
    else:
        failed = next((s for s in result.steps if not s.success), None)
        print(f"Ingestion failed: {{failed.error if failed else 'unknown'}}")


def query(question: str, top_k: int | None = None, skip_llm: bool = False) -> AgentOutput:
    \"\"\"Retrieve relevant chunks and optionally generate an answer.\"\"\"
    Tracer.new_trace(f"{{config.project_name}}:query")

    k = top_k or config.top_k
    retrieval_result = retriever.run(RetrieverInput(data=question, metadata={{"top_k": k}}))
    if not retrieval_result.success:
        return AgentOutput(response="", success=False, error=retrieval_result.error)

    chunks = retrieval_result.data
    context = "\\n\\n".join(c.get("text", "") for c in chunks)

    if skip_llm:
        Tracer.flush()
        return AgentOutput(
            response=context,
            sources=[{{"text": c.get("text", "")[:200], "source": c.get("source", ""),
                      "score": c.get("score", 0)}} for c in chunks],
        )

    llm_result = llm.run(ToolInput(data=question, metadata={{"context": context}}))
    Tracer.flush()

    return AgentOutput(
        response=llm_result.data if llm_result.success else "",
        sources=[{{"text": c.get("text", "")[:200], "source": c.get("source", "")}} for c in chunks],
        success=llm_result.success,
        error=llm_result.error,
    )


# Module-level reference for `ai-builder run`
tool = None  # not a single tool
agent = None
""")

    _write(target / "src" / pkg / "config.py", f"""\
from pathlib import Path

from ai_builder.core.config import BaseConfig


class {cls}Config(BaseConfig):
    project_name: str = "{name}"
    data_dir: Path = Path("data")

    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Embedding
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Vector store
    vector_provider: str = "faiss"
    vector_store_path: Path = Path("data/vectorstore")
    collection_name: str = "default"
    top_k: int = 5

    # LLM (optional, for generation step)
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
""")

    _write(target / "data" / "raw" / ".gitkeep", "")

    _write(target / "pipeline.yaml", f"""\
name: {name}
description: "RAG pipeline: load → split → embed → store → retrieve"
steps:
  - name: loader
    tool: loader
    type: loader
    config:
      source: data/raw/
      formats: [txt, md, pdf, docx, pptx, html, rtf]
  - name: splitter
    tool: splitter
    type: splitter
    config:
      chunk_size: 1000
      chunk_overlap: 200
  - name: embedder
    tool: embedder
    type: embedder
    config:
      model: sentence-transformers/all-MiniLM-L6-v2
      batch_size: 64
  - name: vector_store
    tool: vector_store
    type: vector_store
    config:
      provider: faiss
      path: data/vectorstore/
  - name: retriever
    tool: retriever
    type: retriever
    config:
      top_k: 5
""")

    _write(target / "tests" / "test_pipeline.py", f"""\
from pathlib import Path
from ai_builder.tools import DocumentLoader, TextSplitter
from ai_builder.core.tool import ToolInput


def test_loader_missing_dir():
    loader = DocumentLoader()
    result = loader.run(ToolInput(data="/nonexistent"))
    assert not result.success


def test_splitter_chunks():
    splitter = TextSplitter()
    result = splitter.run(ToolInput(data=[{{"text": "a" * 2000, "source": "test.txt"}}]))
    assert result.success
    assert len(result.data) > 1


def test_pipeline_import():
    from {pkg} import pipeline
    assert pipeline is not None
    assert len(pipeline.steps) == 4
""")

    # ── Deployment files ──
    _write(target / "Dockerfile", generate_dockerfile(name, pkg))
    _write(target / "docker-compose.yml", generate_docker_compose(name, pkg))
    _write(target / "k8s" / "deployment.yaml", generate_k8s_deployment(name))
    _write(target / "k8s" / "service.yaml", generate_k8s_service(name))
    _write(target / "k8s" / "configmap.yaml", generate_k8s_configmap(name))
    _write(target / "k8s" / "hpa.yaml", generate_k8s_hpa(name))

    # ── README ──
    _write(target / "README.md", f"""\
# {name}

RAG (Retrieval-Augmented Generation) pipeline built with **ai-builder**.

## Architecture

```
data/raw/  →  DocumentLoader  →  TextSplitter  →  Embedder  →  VectorStore
                                                                    ↓
                                                Query  →  Retriever  →  LLM  →  Answer
```

All tools are imported from `ai_builder.tools` — no custom tool code needed.
Configuration lives in `.env` and `{pkg}/config.py`.

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Add documents
cp your-docs/* data/raw/

# 3. Ingest (embed + index)
ai-builder run . --input data/raw/

# 4. Query
python -c "from {pkg} import query; print(query('What is this about?').response)"
```

## Python API

```python
from {pkg} import ingest, query

# Ingest documents into the vector store
ingest("data/raw/")

# Query with retrieval
result = query("What are the key findings?")
print(result.response)
print(result.sources)

# Query without LLM (retrieval only)
result = query("key findings", skip_llm=True)
```

## Configuration

Edit `.env` to configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | HuggingFace embedding model |
| `VECTOR_PROVIDER` | `faiss` | Vector DB: `faiss`, `chroma`, `qdrant` |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `TOP_K` | `5` | Number of results to retrieve |
| `OPENAI_API_KEY` | — | For LLM generation step |

## Tracing (Langfuse)

Enable observability by setting Langfuse credentials in `.env`:

```env
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
```

Then in your code:
```python
from ai_builder.tracing import Tracer
Tracer.configure(backend="langfuse", public_key="pk-...", secret_key="sk-...")
```

## Visualize

```bash
ai-builder visualize .   # Opens interactive flow diagram in browser
```

## Deploy

### Docker
```bash
docker compose up --build
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

## Project Structure

```
{name}/
├── src/{pkg}/
│   ├── __init__.py
│   ├── main.py          # Pipeline composition (imports built-in tools)
│   └── config.py         # Pydantic settings from .env
├── data/raw/              # Input documents
├── data/vectorstore/      # FAISS index (generated)
├── pipeline.yaml          # Flow definition (for visualization)
├── tests/
├── Dockerfile
├── docker-compose.yml
├── k8s/                   # Kubernetes manifests
├── .env
├── requirements.txt
└── pyproject.toml
```

## Supported Document Formats

PDF, DOCX, PPTX, TXT, MD, HTML, RTF, CSV, JSON

## Vector Store Providers

| Provider | Local | Setup |
|----------|-------|-------|
| **FAISS** | Yes | Default, no server needed |
| **Chroma** | Yes/Remote | `pip install chromadb` |
| **Qdrant** | Remote | `pip install qdrant-client` |
""")
