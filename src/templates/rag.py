"""Template: ai-builder create rag <name> — imports from built-in tools library."""

from pathlib import Path

from ai_builder.templates import register, _to_snake, _write
from ai_builder.templates.rag_scaffold import (
    RagScaffoldChoices,
    config_defaults_for_template,
    render_dot_env_example,
    render_pyproject_toml,
    render_requirements_txt,
)
from ai_builder.deploy.generators import (
    generate_dockerfile,
    generate_docker_compose,
    generate_k8s_namespace,
    generate_k8s_pvc_rag_staging,
    generate_k8s_pvc_qdrant,
    generate_k8s_qdrant_deployment,
    generate_k8s_qdrant_service,
    generate_k8s_configmap_rag,
    generate_k8s_job_rag_stage,
    generate_k8s_rag_readme,
)


@register("rag")
def generate(name: str, target: Path, *, choices: RagScaffoldChoices | None = None) -> None:
    pkg = _to_snake(name)
    cls = "".join(w.capitalize() for w in name.split("-"))
    vp, ds, qu, em = config_defaults_for_template(choices)

    _write(target / "pyproject.toml", render_pyproject_toml(name, choices))
    _write(target / "requirements.txt", render_requirements_txt(name, choices))
    _write(target / ".env.example", render_dot_env_example(name, choices))

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

    uv pip install -e ".[embeddings-local,faiss]"
    # See app/full_rag.py
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
install the optional extras and see app/full_rag.py:

    uv pip install -e ".[embeddings-local,faiss]"
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
        print("  uv pip install -e \\".[embeddings-local,faiss]\\"   # add vector embeddings")
        print("  python app/full_rag.py                     # run the full pipeline")
    finally:
        Tracer.flush()


if __name__ == "__main__":
    ingest()
""")

    # ── config.py ──
    _write(target / "src" / pkg / "config.py", f"""\
from pathlib import Path

from pydantic import Field

from ai_builder.core.config import BaseConfig


class {cls}Config(BaseConfig):
    \"\"\"Loads from `.env` (copy `.env.example` → `.env`).\"\"\"

    project_name: str = "{name}"
    data_dir: Path = Path("data")

    # Chunking
    chunk_size: int = Field(default=1000, ge=50)
    chunk_overlap: int = Field(default=200, ge=0)

    # Data source — see ai_builder.tools.data_source and DATA_SOURCE_* in `.env`
    data_source_type: str = Field(default="{ds}", description="local | efs | s3 | azure_blob | gcs | …")

    # Vector store — faiss/chroma/qdrant implemented in ai-builder; others need custom indexing
    vector_provider: str = Field(default="{vp}", description="VECTOR_PROVIDER")
    qdrant_url: str = Field(default="{qu}")

    # sentence-transformers (must match index + query) — see SUPPORTED_MODELS in ai_builder.tools.embeddings.config
    embedding_model_id: str = Field(
        default={em!r},
        description="HuggingFace / ST model id for Embedder and Retriever",
    )
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

    # ── app/full_rag.py — full pipeline: load → split → embed → store → retrieve ──
    _write(target / "app" / "full_rag.py", f"""\
\"\"\"
Full RAG path: document load, chunking, embeddings, vector store, similarity search.

Prerequisites (install the project and optional RAG extras)::

    cp .env.example .env
    uv venv .venv && source .venv/bin/activate
    uv pip install -e "."
    uv pip install -e ".[embeddings-local,faiss]"

    # Qdrant (e.g. ``docker compose up`` with the Qdrant service) instead of FAISS:
    # uv pip install -e ".[embeddings-local,qdrant]"

Run::

    python app/full_rag.py
\"\"\"

from __future__ import annotations

from ai_builder.core.tool import ToolInput
from ai_builder.tools import (
    DocumentLoader,
    TextSplitter,
    SplitterConfig,
    Embedder,
    EmbedderConfig,
    VectorStoreWriter,
    VectorStoreConfig,
    Retriever,
    RetrieverConfig,
    RetrieverInput,
)
from ai_builder.tracing import Tracer, configure_tracing_from_env

from {pkg}.config import {cls}Config

config = {cls}Config()

# Ingestion: load → split → embed → index (provider from config / .env)
loader = DocumentLoader()
splitter = TextSplitter(
    SplitterConfig(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
    )
)
embedder = Embedder(EmbedderConfig(model_id=config.embedding_model_id))
store = VectorStoreWriter(
    VectorStoreConfig(
        provider=config.vector_provider,  # faiss | chroma | qdrant
        store_path=str(config.data_dir / "vectorstore"),
        qdrant_url=config.qdrant_url,
    )
)

ingest_pipeline = loader | splitter | embedder | store

retriever = Retriever(
    RetrieverConfig(
        provider=config.vector_provider,
        store_path=str(config.data_dir / "vectorstore"),
        qdrant_url=config.qdrant_url,
        embedding_model=config.embedding_model_id,
    )
)


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
      formats: [txt, md, pdf, docx, doc, pptx, html, htm, rtf, xlsx, xls, csv, json, xml, epub, odt]
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
"""Thin re-exports from ai-builder (document loaders only in this scaffold).

Examples::

    from tools.document_loader import loader_pdf, DocumentLoader
    from tools.data_source import LocalFilesystemDataSource
"""
''',
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
        target / "src" / "tools" / "data_source" / "__init__.py",
        '''\
"""Optional re-exports — data corpus location (sync or path) before DocumentLoader.

Examples::

    from tools.data_source import LocalFilesystemDataSource, S3DataSource
"""

from ai_builder.tools.data_source import (
    AzureBlobDataSource,
    CephRgwDataSource,
    GcsDataSource,
    GoogleDriveDataSource,
    LocalFilesystemDataSource,
    MinioDataSource,
    OneDriveDataSource,
    S3DataSource,
)

__all__ = [
    "LocalFilesystemDataSource",
    "S3DataSource",
    "MinioDataSource",
    "CephRgwDataSource",
    "AzureBlobDataSource",
    "GcsDataSource",
    "GoogleDriveDataSource",
    "OneDriveDataSource",
]
''',
    )

    # ── Kubernetes stage runner (Jobs: extract → chunk → embed) ──
    _write(
        target / "src" / pkg / "workers" / "__init__.py",
        f'"""Stage workers for ``python -m {pkg}.workers.stage_runner`` (see ``k8s/README.md``)."""\n',
    )

    _write(
        target / "src" / pkg / "workers" / "stage_runner.py",
        f'''\
"""Run one RAG stage for Kubernetes Jobs (`RAG_STAGE` env).

Stages write JSON checkpoints under ``data/staging/``:

- **extract** — ``DocumentLoader`` → ``documents.json``
- **chunk** — ``TextSplitter`` → ``chunks.json``
- **embed** — ``Embedder`` | ``VectorStoreWriter`` → vector DB (needs ``.[embeddings-local,qdrant]`` or faiss extras)

Configure Langfuse via `.env` / ConfigMap so spans appear in Langfuse when keys are set.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from ai_builder.core.tool import ToolInput
from ai_builder.tracing import Tracer, configure_tracing_from_env

from {pkg}.config import {cls}Config

STAGE_EXTRACT = "extract"
STAGE_CHUNK = "chunk"
STAGE_EMBED = "embed"

DOCS_NAME = "documents.json"
CHUNKS_NAME = "chunks.json"


def _staging_dir() -> Path:
    root = Path(os.environ.get("RAG_DATA_DIR", "data"))
    staging = root / "staging"
    staging.mkdir(parents=True, exist_ok=True)
    return staging


def run_extract() -> int:
    from ai_builder.tools import DocumentLoader

    src = os.environ.get("RAG_SOURCE_DIR", "data/raw/")
    loader = DocumentLoader()
    result = loader.run(ToolInput(data=src))
    if not result.success:
        print(result.error or "loader failed", file=sys.stderr)
        return 1
    docs = result.data or []
    path = _staging_dir() / DOCS_NAME
    path.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {{len(docs)}} documents to {{path}}")
    return 0


def run_chunk() -> int:
    from ai_builder.tools import TextSplitter, SplitterConfig

    staging = _staging_dir()
    docs_path = staging / DOCS_NAME
    if not docs_path.exists():
        print("Missing staging/documents.json — run extract stage first.", file=sys.stderr)
        return 1

    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    cfg = {cls}Config()
    splitter = TextSplitter(
        SplitterConfig(chunk_size=cfg.chunk_size, chunk_overlap=cfg.chunk_overlap)
    )
    result = splitter.run(ToolInput(data=docs))
    if not result.success:
        print(result.error or "splitter failed", file=sys.stderr)
        return 1
    chunks = result.data or []
    out = staging / CHUNKS_NAME
    out.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {{len(chunks)}} chunks to {{out}}")
    return 0


def run_embed() -> int:
    from ai_builder.tools import Embedder, VectorStoreConfig, VectorStoreWriter

    staging = _staging_dir()
    chunks_path = staging / CHUNKS_NAME
    if not chunks_path.exists():
        print("Missing staging/chunks.json — run chunk stage first.", file=sys.stderr)
        return 1

    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    cfg = {cls}Config()
    embedder = Embedder()
    store = VectorStoreWriter(
        VectorStoreConfig(
            provider=cfg.vector_provider,
            store_path=str(cfg.data_dir / "vectorstore"),
            qdrant_url=cfg.qdrant_url,
        )
    )
    pipeline = embedder | store
    result = pipeline.run(ToolInput(data=chunks))
    if not result.success:
        failed = next((s for s in result.steps if not s.success), None)
        print(failed.error if failed else "embed/store failed", file=sys.stderr)
        return 1
    print("Embedding and index write completed.")
    return 0


def main() -> int:
    configure_tracing_from_env()
    cfg = {cls}Config()
    Tracer.new_trace(f"{{cfg.project_name}}-rag-{{os.environ.get('RAG_STAGE', '?')}}")
    try:
        stage = os.environ.get("RAG_STAGE", "").strip().lower()
        if stage == STAGE_EXTRACT:
            return run_extract()
        if stage == STAGE_CHUNK:
            return run_chunk()
        if stage == STAGE_EMBED:
            return run_embed()
        print(
            "Set RAG_STAGE to extract | chunk | embed (Kubernetes Job env).",
            file=sys.stderr,
        )
        return 2
    finally:
        Tracer.flush()


if __name__ == "__main__":
    raise SystemExit(main())
''',
    )

    # ── Deployment files ──
    _dockerfile = generate_dockerfile(name, pkg).replace(
        "RUN pip install --no-cache-dir -e .",
        'RUN pip install --no-cache-dir -e ".[embeddings-local,qdrant]"',
        1,
    )
    _write(target / "Dockerfile", _dockerfile)
    _write(target / "docker-compose.yml", generate_docker_compose(name, pkg, include_qdrant=True))
    _write(target / "k8s" / "README.md", generate_k8s_rag_readme(name, pkg))
    _write(target / "k8s" / "namespace.yaml", generate_k8s_namespace(name))
    _write(target / "k8s" / "pvc-rag-staging.yaml", generate_k8s_pvc_rag_staging(name))
    _write(target / "k8s" / "pvc-qdrant.yaml", generate_k8s_pvc_qdrant(name))
    _write(target / "k8s" / "configmap-rag.yaml", generate_k8s_configmap_rag(name, pkg))
    _write(target / "k8s" / "qdrant-deployment.yaml", generate_k8s_qdrant_deployment(name))
    _write(target / "k8s" / "qdrant-service.yaml", generate_k8s_qdrant_service(name))
    _write(target / "k8s" / "job-rag-extract.yaml", generate_k8s_job_rag_stage(name, pkg, "extract"))
    _write(target / "k8s" / "job-rag-chunk.yaml", generate_k8s_job_rag_stage(name, pkg, "chunk"))
    _write(target / "k8s" / "job-rag-embed.yaml", generate_k8s_job_rag_stage(name, pkg, "embed"))

    # ── README ──
    _write(target / "README.md", f"""\
# {name}

RAG (Retrieval-Augmented Generation) pipeline built with **ai-builder** (requires **Python 3.13+**).

## 1. Environment

Create the virtualenv **inside this project** so `.venv/bin/activate` exists here:

```bash
cd /path/to/{name}
uv venv --python 3.13 .venv
source .venv/bin/activate          # Windows: .venv/Scripts/activate
cp .env.example .env
uv pip install -e "."
```

Installing the project in editable mode pulls **ai-builder** from `pyproject.toml` and registers `{pkg}` — required for `import ai_builder` and `python app/full_rag.py`.

## 2. Hello path (no optional ML deps)

```bash
python -m {pkg}
# or
ai-builder run .
```

Loads `data/raw/hello.md`, splits into chunks, prints a preview. Uses **Langfuse** only if keys are set (see below).

## 3. Full pipeline (embeddings + vector store)

```bash
uv pip install -e ".[embeddings-local,faiss]"
python app/full_rag.py
```

For **Qdrant** (matches `docker-compose` sidecar): `uv pip install -e ".[embeddings-local,qdrant]"` and set `VECTOR_PROVIDER=qdrant` in `.env`.

## 4. Langfuse observability

Traces use `configure_tracing_from_env()` (already wired in `main.py` and `app/full_rag.py`).

1. Create a project in [Langfuse](https://cloud.langfuse.com/) and copy API keys.
2. Edit `.env`:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENABLED=true
```

3. Run any pipeline command; open Langfuse → Traces.

Self-hosted Langfuse: set `LANGFUSE_HOST` to your instance URL.

## 5. Document formats

| Format | Extra |
|--------|--------|
| TXT, MD, CSV, JSON, XML | _(none)_ |
| PDF | `-e ".[pdf]"` or `-e ".[docs]"` |
| DOCX / legacy Word | `-e ".[word]"` or `-e ".[docs]"` |
| PPTX | `-e ".[slides]"` or `-e ".[docs]"` |
| HTML | `-e ".[html]"` or `-e ".[docs]"` |
| RTF | `-e ".[rtf]"` or `-e ".[docs]"` |
| XLSX / XLS | `-e ".[spreadsheet]"` or `-e ".[docs]"` |
| EPUB | `-e ".[epub]"` or `-e ".[docs]"` |
| ODT | `-e ".[odt]"` or `-e ".[docs]"` |

## 6. Docker Compose

Requires `.env` (copy from `.env.example`). Compose adds a **Qdrant** service and points the app at it.

```bash
docker compose up --build
```

## 7. Kubernetes (split services)

Manifests separate **data extraction**, **chunking**, **embedding/indexing**, and **Qdrant** — see `k8s/README.md`. Jobs must run **extract → chunk → embed** in order (shared PVC).

## 8. Optional extras

Granular installs (pick what you use):

```bash
uv pip install -e ".[notebook]"
uv pip install -e ".[embeddings-local]"   # sentence-transformers (built-in Embedder)
uv pip install -e ".[embeddings-openai]" # openai — API embedding workflows (custom code)
uv pip install -e ".[faiss]"
uv pip install -e ".[qdrant]"
uv pip install -e ".[pdf]"               # plus: word, slides, html, epub, odt, …
uv pip install -e ".[docs]"              # all document parsers
uv pip install -e ".[llm-openai]"       # OpenAI SDK — OpenAI / Ollama (`base_url`) / proxies
uv pip install -e ".[llm-anthropic]"
uv pip install -e ".[llm-bedrock]"
uv pip install -e ".[llm]"               # openai + anthropic
uv pip install -e ".[all]"
```

After `ai-builder create rag`, `requirements.txt` lists packages for the profile you chose in the wizard (non-interactive: see comments there).

## Layout

```
{name}/
├── app/
│   └── full_rag.py           # Full ingest + retrieve script
├── src/{pkg}/
│   ├── main.py               # Loader + splitter demo
│   ├── config.py             # Settings (.env)
│   └── workers/
│       └── stage_runner.py   # Kubernetes Job stages
├── src/tools/document_loader/
├── src/tools/data_source/    # Thin re-exports from ai-builder
├── data/raw/hello.md
├── pipeline.yaml
├── tests/
├── Dockerfile
├── docker-compose.yml        # App + Qdrant
├── k8s/                     # Namespace, PVCs, Qdrant, Jobs
├── .env.example
└── pyproject.toml
```
""")
