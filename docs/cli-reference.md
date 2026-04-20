# CLI reference

Invoke the top-level CLI as **`ai-builder`** after installing the package (`pip install …`). Use **`--help`** on any command for Typer-generated details.

---

## Global behavior

- **`no_args_is_help`** — running `ai-builder` alone prints help.
- Subcommands are grouped under **`create`**.

---

## `ai-builder version`

Print the installed **`ai-builder`** package version.

```bash
ai-builder version
```

---

## `ai-builder list-templates`

Show the table of scaffold templates (`create tool`, `create rag`, …) and reminder text for **`ai-builder add`**.

---

## `ai-builder create`

Scaffold a new project. Syntax:

```bash
ai-builder create <subcommand> <name> [--output DIR]
```

| Subcommand | Description |
|------------|-------------|
| `tool <name>` | Composable `BaseTool` project |
| `rag <name>` | RAG pipeline (built-in loader, splitter, optional embed/store) |
| `agent-langchain <name>` | LangChain/LangGraph-style agent |
| `agent-deep <name>` | Multi-agent research-style layout |
| `pipeline <name>` | YAML-oriented data pipeline |

Options:

| Option | Short | Meaning |
|--------|-------|---------|
| `--output` | `-o` | Parent directory for the new folder (default: current working directory). |

Behavior:

- If **`uv`** is available, `create` may run **`uv venv .venv`** and **`uv pip install -e .`** inside the new project.

---

## `ai-builder run`

Execute a project’s entry point.

```bash
ai-builder run [PATH] [--input TEXT] [--query TEXT] [--verbose]
```

| Argument / option | Meaning |
|-------------------|---------|
| `PATH` | Project directory (default: `.`). Looks for **`src/<package>/main.py`** and imports `<package>.main`. Can also point to a **`pipeline.yaml`** file (limited; see runtime message). |
| `--input` / `-i` | String passed into tools/pipelines as `ToolInput(data=…)` where applicable. |
| `--query` / `-q` | Query string for **agents** (`BaseAgent`). |
| `--verbose` / `-v` | More logging. |

Discovery:

- Adds **`src/`** to **`sys.path`** so local packages resolve.
- Looks for **`tool`**, **`agent`**, **`pipeline`**, **`main`** on the imported **`main`** module (`src/<pkg>/main.py`).

---

## `ai-builder visualize`

Generate flow diagrams from **`pipeline.yaml`**.

```bash
ai-builder visualize [PATH] [--output FILE] [--open/--no-open] [--format FORMAT]
```

| Option | Short | Meaning |
|--------|-------|---------|
| `PATH` | — | Project directory or a `.yaml` file (default: `.`). |
| `--output` | `-o` | Output path (`pipeline.html`, `pipeline.mmd`, …). |
| `--open` / `--no-open` | — | Open HTML in browser (default: open). |
| `--format` | `-f` | `html` (default), `mermaid`, `svg`. |

---

## `ai-builder serve`

Start a small **FastAPI** dashboard for pipeline visualization (requires **`ai-builder[serve]`**).

```bash
ai-builder serve [PATH] [--port PORT] [--host HOST]
```

| Option | Short | Default |
|--------|-------|---------|
| `--port` | `-p` | `8501` |
| `--host` | — | `127.0.0.1` |

---

## `ai-builder add`

Install optional built-in tooling into the **current** ai-builder project and add helpful stubs.

```bash
ai-builder add           # list catalog
ai-builder add loader    # example: add loader-focused deps / snippets
```

With **no argument**, prints the catalog of names (`loader`, `splitter`, `embedder`, …). Run from a directory tree that contains a scaffolded project (`pyproject.toml`, `src/<pkg>/`).

See source: `ai_builder/commands/add.py` **`TOOL_CATALOG`** for the authoritative list.

---

## Related

- [Getting started](getting-started.md)
- [Templates](templates.md)
