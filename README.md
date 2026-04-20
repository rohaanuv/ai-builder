# ai-builder

<p align="center">
  <em>Composable AI tools, agents, and pipelines — typed, minimal, CLI + library.</em>
</p>

<p align="center">
  <a href="https://www.python.org/"><code>python</code></a> ·
  <a href="https://pydantic.dev/"><code>pydantic</code></a> ·
  <a href="https://typer.tiangolo.com/"><code>typer</code></a> ·
  <a href="https://github.com/topics/rag"><code>rag</code></a> ·
  <a href="https://github.com/topics/llm"><code>llm</code></a> ·
  <a href="https://github.com/topics/langchain"><code>langchain</code></a> ·
  <a href="https://github.com/topics/agents"><code>agents</code></a> ·
  <a href="https://github.com/topics/cli"><code>cli</code></a>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/release/python-3130/"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.13 or newer"/></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-AGPL--3.0-blue?style=flat-square" alt="License AGPL 3.0"/></a>
  <a href="./pyproject.toml"><img src="https://img.shields.io/badge/package-1.1.0-2ea44f?style=flat-square" alt="ai-builder package version 1.1.0"/></a>
  <a href="https://github.com/rohaanuv/ai-builder/graphs/contributors"><img src="https://img.shields.io/github/contributors/rohaanuv/ai-builder?style=flat-square&logo=github&label=contributors" alt="GitHub contributor count"/></a>
  <a href="https://github.com/rohaanuv/ai-builder/stargazers"><img src="https://img.shields.io/github/stars/rohaanuv/ai-builder?style=flat-square&logo=github&label=stars&color=yellow" alt="GitHub stars for rohaanuv ai-builder"/></a>
  <a href="https://github.com/rohaanuv/ai-builder/network/members"><img src="https://img.shields.io/github/forks/rohaanuv/ai-builder?style=flat-square&logo=github&label=forks" alt="GitHub forks"/></a>
  <a href="https://github.com/rohaanuv/ai-builder/issues"><img src="https://img.shields.io/github/issues/rohaanuv/ai-builder?style=flat-square&logo=github&label=issues" alt="Open GitHub issues"/></a>
  <a href="https://github.com/rohaanuv/ai-builder/pulls"><img src="https://img.shields.io/github/issues-pr/rohaanuv/ai-builder?style=flat-square&logo=github&label=PRs" alt="GitHub pull requests"/></a>
  <a href="https://github.com/rohaanuv/ai-builder/commits/main/"><img src="https://img.shields.io/github/last-commit/rohaanuv/ai-builder/main?style=flat-square&logo=github&label=last%20commit" alt="Last commit on main branch"/></a>
</p>

---

## Overview

**ai-builder** ([github.com/rohaanuv/ai-builder](https://github.com/rohaanuv/ai-builder)) is an open-source **Python** framework and **CLI** for **retrieval-augmented generation (RAG)**, **LLM pipelines**, and lightweight **AI agents**. Build **document ingestion**, **chunking**, **embeddings** (including **sentence-transformers** and **OpenAI**-compatible flows), and **vector search** over **FAISS**, **Chroma**, or **Qdrant** using **Pydantic**-typed **`ToolInput` → `ToolOutput`** tools, **pipeline composition** with `|`, and **`.env`** configuration. Optional **Langfuse** tracing and **Docker / Kubernetes** deploy templates help you go from prototype to production without a heavyweight runtime.

| Principle | What you get |
| :--- | :--- |
| **Design** | Small surface area; **optional extras** so you install only document parsers, **vector DB** clients, and **LLM** SDKs you need |
| **RAG** | Interactive **`ai-builder create rag`** wizard (CLI **≥ 1.1**): data sources, embedding model, vector backend, LLM, formats → **`pyproject.toml`**, **`requirements.txt`**, **`.env.example`** |
| **Vectors** | Built-in **FAISS**, **Chroma**, **Qdrant**; other backends ship as optional clients for your own wiring |

---

## Table of contents

- [Installation](#installation)
- [Quickstart](#quickstart)
- [Clone and local development](#clone-and-local-development)
- [Documentation](#documentation)
- [Features & modules](#features--modules)
- [Optional extras](#optional-extras)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

Install **ai-builder** from GitHub (recommended until the package is published on PyPI):

```bash
pip install "git+https://github.com/rohaanuv/ai-builder.git"
```

Upgrade:

```bash
pip install --upgrade "git+https://github.com/rohaanuv/ai-builder.git"
```

Install with common stacks (examples):

```bash
pip install "ai-builder[rag,tracing] @ git+https://github.com/rohaanuv/ai-builder.git"
```

Granular extras keep containers and virtualenvs small — see [Optional extras](#optional-extras).

---

## Quickstart

**CLI — scaffold a RAG project** (interactive dependency profile):

```bash
ai-builder create rag my-app
cd my-app && uv venv --python 3.13 .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
cp .env.example .env && uv pip install -e "."
python -m my_app   # package name matches your project (e.g. my-app → my_app)
```

Use **`ai-builder version`** to confirm **≥ 1.1** for the full **`create rag`** wizard. Use **`--no-wizard`** for a minimal **`requirements.txt`** with comment hints.

**Library — compose tools as a pipeline:**

```python
from ai_builder.tools import DocumentLoader, TextSplitter, Embedder

pipeline = DocumentLoader() | TextSplitter() | Embedder()
```

---

## Clone and local development

Fork or clone the repository to run **ai-builder** from source or contribute changes:

```bash
git clone https://github.com/rohaanuv/ai-builder.git
cd ai-builder
```

Editable install and dev workflow (details in [Contributing](docs/contributing.md)):

```bash
uv venv --python 3.13 .venv && source .venv/bin/activate
uv pip install -e ".[dev]"
ai-builder version
```

---

## Documentation

| Resource | Description |
|----------|-------------|
| **[Documentation hub](docs/README.md)** | Getting started, CLI, concepts, templates, deployment |
| **[Installation & upgrade](docs/installation-and-upgrade.md)** | Pinning versions, **`uv`**, extras |
| **[AGENTS.md](AGENTS.md)** | Repository layout for contributors |
| **[Issues](https://github.com/rohaanuv/ai-builder/issues)** | Bugs and feature requests |

---

## Features & modules

- **`ai_builder.tools`** — **document loaders** (PDF, Office, HTML, … via extras), **text splitter**, **embeddings** (`ai_builder.tools.embeddings`, **Hugging Face** / **sentence-transformers**), **vector stores** (**FAISS** / **Chroma** / **Qdrant**), **retriever**, **LLM** connectors (**OpenAI**, **Anthropic**, **Bedrock**, **Azure**, **Ollama**), optional **web search**
- **`ai_builder.tools.data_source`** — **local** paths / **EFS**; **Amazon S3** (**MinIO**, **Ceph RGW**); **Azure Blob**; **Google Cloud Storage**; stubs for **Google Drive** / **Microsoft OneDrive**
- **`ai_builder.deploy`** — **Dockerfile**, **Compose**, **Kubernetes** manifests from templates
- **`ai_builder.visualize`** — pipeline diagrams for docs and reviews

---

## Optional extras

Document parsers are **optional** — only installed formats can be read:

| Extra | Formats |
|-------|---------|
| `docs-pdf` | `.pdf` |
| `docs-word` | `.docx`, `.dotx`, legacy `.doc` / `.dot` |
| `docs-slides` | `.pptx` |
| `docs-html` | `.html`, `.htm` |
| `docs-rtf` | `.rtf` |
| `docs-spreadsheet` | `.xlsx`, `.xls` |
| `docs-epub` | `.epub` |
| `docs-odt` | `.odt` |
| **`docs`** | **All** of the above |

**Embeddings:** `embeddings-local`, `embeddings-openai`. **LLMs:** `llm-openai`, `llm-anthropic`, `llm-bedrock`, or `llm`.

PDF-only example:

```bash
pip install "ai-builder[docs-pdf] @ git+https://github.com/rohaanuv/ai-builder.git"
```

---

## FAQ

### What is ai-builder used for?

**ai-builder** helps you ship **RAG apps** and **LLM-backed tools** in **Python**: ingest documents, chunk text, embed with **sentence-transformers** or API clients, index into a **vector database**, and query with a **retriever**—with a **CLI** that scaffolds dependency profiles and config.

### How does ai-builder relate to LangChain?

**ai-builder** focuses on **small, typed tools** and **`|` composition**. You can combine it with **LangChain** / **LangGraph**-style stacks via optional **`agents`** extras when you need those integrations.

### Where do I report bugs or request features?

Use **[GitHub Issues](https://github.com/rohaanuv/ai-builder/issues)** on [rohaanuv/ai-builder](https://github.com/rohaanuv/ai-builder).

### What Python version is required?

**Python 3.13+** — see [`pyproject.toml`](./pyproject.toml).

---

## Contributing

Contributions are welcome: **fork** the repo, create a branch, and open a **pull request**. Guidelines, editable install, and dev dependencies are in **[docs/contributing.md](docs/contributing.md)**.

---

## License

**AGPL-3.0-or-later** — see [LICENSE](LICENSE).
