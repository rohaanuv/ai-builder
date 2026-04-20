# Getting started

This guide takes you from a clean machine to a running scaffolded project.

## Prerequisites

- **Python 3.13+** on your `PATH`.
- **`uv`** recommended ([installation](https://docs.astral.sh/uv/getting-started/installation/)); `pip` is sufficient for installing **ai-builder**.

## 1. Install the CLI

```bash
pip install "git+https://github.com/rohaanuv/ai-builder.git"
# Or upgrade so you get the latest `create rag` wizard and templates:
pip install --upgrade "git+https://github.com/rohaanuv/ai-builder.git"
```

From a clone, use an editable install so `ai-builder` on your PATH matches the repo:

```bash
cd ai-builder && uv pip install -e "."
```

Verify:

```bash
ai-builder version
ai-builder list-templates
```

## 2. Create a project

Example: RAG pipeline named `my-search`:

```bash
ai-builder create rag my-search      # interactive wizard (extras + .env.example profile)
# ai-builder create rag my-search --no-wizard
cd my-search
```

If `uv` is installed, the CLI may create a venv and install dependencies automatically. Otherwise:

```bash
uv venv --python 3.13 .venv
source .venv/bin/activate
cp .env.example .env
uv pip install -e "."
```

Always install the **project** in editable mode (`-e .`) so:

- The generated package (e.g. `my_search`) is importable.
- The `ai-builder` dependency from `pyproject.toml` resolves (`import ai_builder` works).

## 3. Run the hello path

From the project directory (with venv activated):

```bash
python -m my_search
```

or:

```bash
ai-builder run .
```

This exercises the default pipeline (for RAG: document load + split) using sample data under `data/raw/`.

## 4. Optional: full RAG stack

Install extras, then run the application script:

```bash
uv pip install -e ".[embeddings-local,faiss]"
python app/full_rag.py
```

Match extras to your wizard selections (see **`requirements.txt`** and the printed **`uv pip install -e ".[…]"`** line). See [Templates – create rag](templates.md#create-rag) and your project’s local **`README.md`**.

## 5. Optional: visualize the flow

```bash
ai-builder visualize .
```

Opens an HTML diagram derived from `pipeline.yaml` (requires a browser unless you pass `--no-open`).

## Next steps

- [Installation and upgrade](installation-and-upgrade.md) — extras, pinning, upgrades.
- [CLI reference](cli-reference.md) — every command.
- [Observability](observability.md) — Langfuse and tracing.
