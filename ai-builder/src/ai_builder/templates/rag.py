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
    "ipykernel>=6.29",
    "langfuse>=2.0",
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
    "openpyxl>=3.1",
    "docx2txt>=0.8",
]
llm = ["openai>=1.0", "anthropic>=0.40"]
chroma = ["chromadb>=0.5"]
qdrant = ["qdrant-client>=1.12"]
dev = ["pytest>=8.0"]
all = ["{name}[embeddings,faiss,docs,llm]"]

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
# DOC support:     uv pip install docx2txt
# PPTX support:    uv pip install python-pptx
# XLSX support:    uv pip install openpyxl
# HTML parsing:    uv pip install beautifulsoup4
# RTF support:     uv pip install striprtf
# OpenAI LLM:     uv pip install openai
# Anthropic LLM:  uv pip install anthropic
# Note: ipykernel + langfuse are in the default install (Jupyter + observability).
# Chroma DB:      uv pip install chromadb
# Qdrant DB:      uv pip install qdrant-client
#
# Or install all optional RAG extras: uv pip install -e ".[all]"
""")

    _write(target / ".env", f"""\
# {name} configuration
PROJECT_NAME={name}
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
LOG_LEVEL=INFO

# Langfuse observability — set keys to export traces from pipeline runs (optional)
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENABLED=true
""")

    # ── __init__.py ──
    # Lazy-load pipeline/ingest so ``python -m {pkg}.main`` does not import ``main`` twice
    # (avoids RuntimeWarning about test_rag.main in sys.modules).
    _write(target / "src" / pkg / "__init__.py", f"""\
\"\"\"
{name} — RAG pipeline built with ai-builder.

Quick start (works immediately — no extra packages needed):

    from {pkg} import ingest
    ingest()                    # loads data/raw/hello.md, splits, prints chunks

Full RAG (after installing extras):

    uv pip install -e ".[embeddings,faiss]"
    # See examples/full_rag.py
\"\"\"

from __future__ import annotations

from typing import Any

__all__ = ["pipeline", "ingest"]


def __getattr__(name: str) -> Any:
    if name == "pipeline":
        from {pkg}.main import pipeline as _pipeline

        return _pipeline
    if name == "ingest":
        from {pkg}.main import ingest as _ingest

        return _ingest
    raise AttributeError(
        "module " + repr(__name__) + " has no attribute " + repr(name),
    )


def __dir__() -> list[str]:
    return sorted(__all__)
""")

    _write(
        target / "src" / pkg / "__main__.py",
        f"""\
\"\"\"Entry point: ``python -m {pkg}`` (same as ``python -m {pkg}.main``).\"\"\"

from {pkg}.main import ingest

if __name__ == "__main__":
    ingest()
""",
    )

    # ── main.py — hello-world that works with zero optional deps ──
    _write(target / "src" / pkg / "main.py", f"""\
\"\"\"
{name} — RAG pipeline using ai-builder built-in tools.

This hello-world demo loads text files and splits them into chunks.
It works immediately with zero optional packages.

    python -m {pkg}
    python -m {pkg}.main

To build the full RAG pipeline (embed → store → retrieve → LLM),
install the optional extras and see examples/full_rag.py:

    uv pip install -e ".[embeddings,faiss]"
\"\"\"

from ai_builder.tools import DocumentLoader, TextSplitter
from ai_builder.core.tool import ToolInput
from ai_builder.tracing import Tracer, configure_tracing_from_env

from {pkg}.config import {cls}Config

config = {cls}Config()

loader = DocumentLoader()
splitter = TextSplitter()

pipeline = loader | splitter


def ingest(source: str = "data/raw/") -> None:
    \"\"\"Load documents and split into chunks (hello-world demo).\"\"\"
    configure_tracing_from_env()
    Tracer.new_trace("{name}-ingest")
    try:
        with Tracer.span("rag.pipeline.run", source=source):
            result = pipeline.run(ToolInput(data=source))

        if not result.success:
            failed = next((s for s in result.steps if not s.success), None)
            print(f"Failed: {{failed.error if failed else 'unknown'}}")
            return

        chunks = result.final_output.data if result.final_output else []
        print(f"Loaded and split into {{len(chunks)}} chunks ({{result.total_duration_ms:.0f}}ms)")
        print()
        for c in chunks[:5]:
            preview = c["text"][:120].replace("\\n", " ")
            print(f"  [{{c['source'].split('/')[-1]}}] {{preview}}...")
        if len(chunks) > 5:
            print(f"  ... and {{len(chunks) - 5}} more chunks")

        print()
        print("Next steps:")
        print("  uv pip install -e \\".[embeddings,faiss]\\"   # add vector embeddings")
        print("  python examples/full_rag.py                 # run the full pipeline")
    finally:
        Tracer.flush()


if __name__ == "__main__":
    ingest()
""")

    # ── config.py ──
    _write(target / "src" / pkg / "config.py", f"""\
from pathlib import Path

from ai_builder.core.config import BaseConfig


class {cls}Config(BaseConfig):
    project_name: str = "{name}"
    data_dir: Path = Path("data")

    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 200
""")

    # ── sample data so first run produces output ──
    _write(target / "data" / "raw" / "hello.md", f"""\
# Welcome to {name}

This is a sample document included with your new RAG pipeline project.
It exists so that `python -m {pkg}` produces output on first run.

## What is RAG?

Retrieval-Augmented Generation (RAG) is a technique that combines
information retrieval with text generation. Instead of relying solely
on a language model's training data, RAG first searches a knowledge
base for relevant documents, then uses those documents as context
when generating a response.

## How this project works

1. **Load** — The DocumentLoader reads files from `data/raw/`
   (supports TXT, MD, PDF, DOCX, DOC, PPTX, HTML, RTF, XLSX, CSV, JSON, XML).
2. **Split** — The TextSplitter breaks documents into overlapping chunks
   suitable for embedding.
3. **Embed** — (optional) The Embedder converts chunks into vector
   representations using sentence-transformers.
4. **Store** — (optional) The VectorStoreWriter indexes embeddings
   in FAISS, Chroma, or Qdrant.
5. **Retrieve** — (optional) The Retriever finds the most relevant
   chunks for a given query.
6. **Generate** — (optional) The LLMTool uses the retrieved context
   to produce a final answer.

Steps 1-2 work immediately. Steps 3-6 require installing optional
packages — see the README for details.

## Getting started

Replace this file with your own documents and run:

    python -m {pkg}

Or use the CLI:

    ai-builder run . --input data/raw/
""")

    # ── examples/full_rag.py — full pipeline with embeddings + retrieval ──
    _write(target / "examples" / "full_rag.py", f"""\
\"\"\"
Full RAG pipeline: load → split → embed → store → retrieve → LLM.

Prerequisites:
    uv pip install -e ".[embeddings,faiss]"
    # For LLM generation, also: uv pip install -e ".[llm]"
    # and set OPENAI_API_KEY in .env

Usage:
    python examples/full_rag.py
\"\"\"

from pathlib import Path

from ai_builder.core.tool import ToolInput
from ai_builder.tools import (
    DocumentLoader,
    TextSplitter, SplitterConfig,
    Embedder, EmbedderConfig,
    VectorStoreWriter, VectorStoreConfig,
    Retriever, RetrieverConfig, RetrieverInput,
)
from ai_builder.tracing import Tracer, configure_tracing_from_env

from {pkg}.config import {cls}Config

config = {cls}Config()

# ── Build the ingestion pipeline ──
loader = DocumentLoader()
splitter = TextSplitter(SplitterConfig(
    chunk_size=config.chunk_size,
    chunk_overlap=config.chunk_overlap,
))
embedder = Embedder()
store = VectorStoreWriter(VectorStoreConfig(
    store_path=str(config.data_dir / "vectorstore"),
))

ingest_pipeline = loader | splitter | embedder | store

# ── Build the retriever ──
retriever = Retriever(RetrieverConfig(
    store_path=str(config.data_dir / "vectorstore"),
))


def main() -> None:
    configure_tracing_from_env()
    Tracer.new_trace("{name}-full-rag")
    try:
        # Ingest
        print("Ingesting documents from data/raw/ ...")
        result = ingest_pipeline.run(ToolInput(data="data/raw/"))
        if not result.success:
            failed = next((s for s in result.steps if not s.success), None)
            print(f"Ingestion failed: {{failed.error if failed else 'unknown'}}")
            return
        print(f"Ingested in {{result.total_duration_ms:.0f}}ms")
        for step in result.steps:
            print(f"  {{step.step_name}}: {{step.duration_ms:.0f}}ms")

        # Query
        question = "What is RAG?"
        print(f"\\nQuerying: {{question}}")
        results = retriever.run(RetrieverInput(data=question))
        if results.success:
            for i, chunk in enumerate(results.data, 1):
                print(f"  [{{i}}] (score={{chunk.get('score', 0):.3f}}) {{chunk['text'][:100]}}...")
        else:
            print(f"Query failed: {{results.error}}")
    finally:
        Tracer.flush()


if __name__ == "__main__":
    main()
""")

    # ── pipeline.yaml ──
    _write(target / "pipeline.yaml", f"""\
name: {name}
description: "RAG pipeline: load → split → embed → store → retrieve"
steps:
  - name: loader
    tool: loader
    type: loader
    config:
      source: data/raw/
      formats: [txt, md, pdf, docx, doc, pptx, html, htm, rtf, xlsx, csv, json, xml]
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

    # ── tests ──
    _write(target / "tests" / "test_pipeline.py", f"""\
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


def test_pipeline_runs():
    from {pkg} import pipeline
    assert pipeline is not None
    assert len(pipeline.steps) == 2
""")

    # ── src/tools/ — app imports without ``ai_builder`` prefix (``from tools.llm import …``) ──
    _write(
        target / "src" / "tools" / "__init__.py",
        '''\
"""Thin re-exports from ai-builder so app code can use ``tools`` as the package root.

Examples::

    from tools.document_loader import loader_rtf, DocumentLoader
    from tools.llm import connect_openai, connect_azure
""",
    )

    _write(
        target / "src" / "tools" / "document_loader" / "__init__.py",
        '''\
"""Document loaders — ``from tools.document_loader import loader_pdf`` etc."""

from ai_builder.tools.document_loader import (
    DocumentLoader,
    FormatLoader,
    LoaderConfig,
    LoaderInput,
    LoaderOutput,
    loader_epub,
    loader_html,
    loader_json,
    loader_pdf,
    loader_rtf,
    loader_slides,
    loader_spreadsheet,
    loader_text,
    loader_word,
    loader_xml,
)

__all__ = [
    "DocumentLoader",
    "FormatLoader",
    "LoaderConfig",
    "LoaderInput",
    "LoaderOutput",
    "loader_epub",
    "loader_html",
    "loader_json",
    "loader_pdf",
    "loader_rtf",
    "loader_slides",
    "loader_spreadsheet",
    "loader_text",
    "loader_word",
    "loader_xml",
]
''',
    )

    _write(
        target / "src" / "tools" / "llm" / "__init__.py",
        '''\
"""LLM connectors — ``from tools.llm import connect_openai``."""

from ai_builder.tools.llm import (
    LLMConfig,
    LLMInput,
    LLMOutput,
    LLMTool,
    connectAnthropic,
    connectAzure,
    connectBedrock,
    connectOllama,
    connectOpenAI,
    connectSelfHostedLLM,
    connect_anthropic,
    connect_azure,
    connect_bedrock,
    connect_ollama,
    connect_openai,
    connect_self_hosted_llm,
)

__all__ = [
    "LLMConfig",
    "LLMInput",
    "LLMOutput",
    "LLMTool",
    "connectAnthropic",
    "connectAzure",
    "connectBedrock",
    "connectOllama",
    "connectOpenAI",
    "connectSelfHostedLLM",
    "connect_anthropic",
    "connect_azure",
    "connect_bedrock",
    "connect_ollama",
    "connect_openai",
    "connect_self_hosted_llm",
]
''',
    )

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

## Quick Start (works immediately)

```bash
source .venv/bin/activate
python -m {pkg}
```

This loads `data/raw/hello.md`, splits it into chunks, and prints them.
No extra packages needed.

## Level Up — Full RAG Pipeline

```bash
# Add embeddings + vector store
uv pip install -e ".[embeddings,faiss]"

# Run the full pipeline
python examples/full_rag.py
```

## Add Your Own Documents

Replace `data/raw/hello.md` with your files:

| Format | Extra package needed? |
|--------|----------------------|
| TXT, MD, CSV, JSON, XML | No (works out of the box) |
| PDF | `uv pip install pdfplumber` |
| DOCX | `uv pip install python-docx` |
| DOC | `uv pip install docx2txt` |
| PPTX | `uv pip install python-pptx` |
| XLSX | `uv pip install openpyxl` |
| HTML, HTM | `uv pip install beautifulsoup4` |
| RTF | `uv pip install striprtf` |

Or install all document parsers at once: `uv pip install -e ".[docs]"`

## Optional Extras

```bash
uv pip install -e ".[embeddings]"    # sentence-transformers
uv pip install -e ".[faiss]"         # FAISS vector store
uv pip install -e ".[docs]"          # all document parsers
uv pip install -e ".[llm]"           # OpenAI + Anthropic
uv pip install -e ".[all]"           # optional RAG extras (ipykernel + Langfuse already default)
```

## Configuration

Edit `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `LANGFUSE_PUBLIC_KEY` | _(empty)_ | Langfuse observability (optional) |
| `LANGFUSE_SECRET_KEY` | _(empty)_ | Pair with public key to export traces |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse server URL |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |

## Deploy

```bash
docker compose up --build         # Docker
kubectl apply -f k8s/             # Kubernetes
```

## Project Structure

```
{name}/
├── src/tools/             # Re-exports for `from tools.document_loader / tools.llm import …`
│   ├── document_loader/
│   └── llm/
├── src/{pkg}/
│   ├── __main__.py        # ``python -m {pkg}`` → ingest()
│   ├── main.py            # Hello-world pipeline (loader + splitter)
│   └── config.py           # Pydantic settings from .env
├── examples/
│   └── full_rag.py         # Full pipeline (embed + store + retrieve)
├── data/raw/hello.md        # Sample document
├── pipeline.yaml
├── tests/
├── Dockerfile
├── docker-compose.yml
├── k8s/
├── .env
└── pyproject.toml
```
""")
