# ai-builder documentation

**ai-builder** is a lightweight Python framework and CLI for composable **tools**, **agents**, and **pipelines**: typed I/O (Pydantic), composition with the `|` operator, and configuration via `.env` and `BaseConfig`.

- **Repository:** [github.com/rohaanuv/ai-builder](https://github.com/rohaanuv/ai-builder)  
- **License:** [AGPL-3.0](../LICENSE)  
- **Python:** 3.13+ (framework 1.x)

---

## Table of contents

| Document | Description |
|----------|-------------|
| [Getting started](getting-started.md) | From install to a first RAG or tool project |
| [Installation and upgrade](installation-and-upgrade.md) | `pip` / `uv`, Git URL, extras, pinning versions |
| [CLI reference](cli-reference.md) | All commands: `create`, `run`, `visualize`, `serve`, `add`, … |
| [Core concepts](core-concepts.md) | `BaseTool`, `Pipeline`, config, agents, piping |
| [Templates](templates.md) | Scaffolds including **`create rag`** wizard, data sources, vector extras |
| [Built-in tools](built-in-tools.md) | Loader, splitter, embedder, vector stores, retriever, LLM, search |
| [Configuration and environment](configuration-and-environment.md) | `.env`, `BaseConfig`, project settings |
| [Observability](observability.md) | Tracing API and Langfuse export |
| [Deployment](deployment.md) | Docker, Compose, Kubernetes patterns from scaffolds |
| [Architecture](architecture.md) | **Repository tree**, **`ai_builder`** package layout, runtime diagram |
| [Contributing](contributing.md) | Local dev setup from source |

---

## Quick links

- Root overview (single-page summary): [README.md](../README.md)  
- Contributor / agent orientation: [AGENTS.md](../AGENTS.md)  
- Package readme (PyPI-style stub): [README.md](../README.md)

---

## Conventions

- Commands assume a Unix-style shell unless noted; on Windows use `.venv\Scripts\activate`.
- Paths like `ai-builder/` refer to the **Python package directory** inside this repository (not the repo root).
