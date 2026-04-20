# Installation and upgrade

## Install from GitHub (recommended)

The package lives in the `ai-builder/` subdirectory of the repository:

```bash
pip install "git+https://github.com/rohaanuv/ai-builder.git"
uv pip install "git+https://github.com/rohaanuv/ai-builder.git"
```

## Install with optional extras

Extras are defined in `pyproject.toml`. Examples:

```bash
pip install "ai-builder[rag,tracing,agents] @ git+https://github.com/rohaanuv/ai-builder.git"
```

Common extras:

| Extra | Purpose |
|-------|---------|
| `docs` | Document parsers (PDF, DOCX, …) |
| `rag` | Embeddings + related stack |
| `llm` | OpenAI / Anthropic clients |
| `agents` | LangChain / LangGraph-oriented dependencies |
| `tracing` | Langfuse client |
| `serve` | FastAPI + Uvicorn for `ai-builder serve` |
| `chroma`, `qdrant` | Vector database clients |
| `search` | Tavily web search |
| `all` | Broad bundle for development |

## Upgrade the framework

Use the **same Python / venv** you rely on day to day:

```bash
pip install --upgrade "git+https://github.com/rohaanuv/ai-builder.git"
uv pip install --upgrade "git+https://github.com/rohaanuv/ai-builder.git"
```

### Pin to a tag or commit

```bash
pip install --upgrade "git+https://github.com/rohaanuv/ai-builder.git@v1.0.0"
```

### Force a clean reinstall

```bash
pip install --upgrade --force-reinstall --no-cache-dir "git+https://github.com/rohaanuv/ai-builder.git"
```

### Projects that depend on ai-builder

If your scaffold’s `pyproject.toml` contains:

```toml
dependencies = [
    "ai-builder @ git+https://github.com/rohaanuv/ai-builder.git",
]
```

then after upgrading the **framework** globally, refresh the **project** environment:

```bash
cd your-project
uv pip install -e "."
```

## Python version

**ai-builder 1.x** requires **Python ≥ 3.13**. Older interpreters will fail dependency resolution (`requires-python`).

## Troubleshooting

- **`pip` or `ai-builder` point at the wrong Python** — ensure your shell `PATH` puts the intended `bin` first (for example Framework or `uv` venv), not an old user `pip` from Python 3.9.
- **`ModuleNotFoundError: ai_builder`** — activate the project venv and run `uv pip install -e "."` in the project root.
