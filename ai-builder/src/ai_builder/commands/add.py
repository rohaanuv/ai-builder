"""ai-builder add — add built-in tools to an existing project on demand."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

console = Console()

UV_BIN = shutil.which("uv")

# ── Tool catalog — each entry describes a built-in tool's contract ──

TOOL_CATALOG: dict[str, dict[str, Any]] = {
    "loader": {
        "class": "DocumentLoader",
        "import": "from ai_builder.tools import DocumentLoader",
        "input": "LoaderInput(data='path/to/dir')",
        "output": "LoaderOutput(data=[{text, source, filename, format, chars}])",
        "extras": [],
        "description": "Load documents (TXT/MD/CSV/JSON/XML use stdlib; PDF/DOCX/HTML etc. need optional deps)",
        "extras_hint": "docs",
    },
    "splitter": {
        "class": "TextSplitter",
        "import": "from ai_builder.tools import TextSplitter",
        "input": "ToolInput(data=[{text, source, ...}])",
        "output": "SplitterOutput(data=[{text, source, chunk_index, chunk_id}])",
        "extras": [],
        "description": "Split documents into overlapping chunks with deterministic IDs",
        "extras_hint": None,
    },
    "embedder": {
        "class": "Embedder",
        "import": "from ai_builder.tools import Embedder",
        "input": "ToolInput(data=[{text, ...}])",
        "output": "EmbedderOutput(data=[{text, embedding, ...}])",
        "extras": ["sentence-transformers"],
        "description": "Generate vector embeddings using sentence-transformers",
        "extras_hint": "embeddings",
    },
    "vector-store": {
        "class": "VectorStoreWriter",
        "import": "from ai_builder.tools import VectorStoreWriter",
        "input": "ToolInput(data=[{text, embedding, ...}])",
        "output": "ToolOutput(data={indexed, total, provider})",
        "extras": ["faiss-cpu"],
        "description": "Index embeddings into FAISS, Chroma, or Qdrant",
        "extras_hint": "faiss",
    },
    "retriever": {
        "class": "Retriever",
        "import": "from ai_builder.tools import Retriever",
        "input": "RetrieverInput(data='query text')",
        "output": "RetrieverOutput(data=[{text, source, score}])",
        "extras": ["sentence-transformers", "faiss-cpu"],
        "description": "Retrieve relevant chunks via vector similarity search",
        "extras_hint": "embeddings,faiss",
    },
    "llm": {
        "class": "LLMTool",
        "import": "from ai_builder.tools import LLMTool",
        "input": "LLMInput(data='prompt text')",
        "output": "LLMOutput(data='generated text')",
        "extras": ["openai"],
        "description": "Generate text using OpenAI, Anthropic, or Ollama",
        "extras_hint": "llm",
    },
    "web-search": {
        "class": "WebSearchTool",
        "import": "from ai_builder.tools import WebSearchTool",
        "input": "WebSearchInput(data='search query')",
        "output": "WebSearchOutput(data=[{title, url, content, score}])",
        "extras": ["tavily-python"],
        "description": "Search the web using Tavily",
        "extras_hint": "search",
    },
}

_DEFAULT_INPUTS: dict[str, str] = {
    "loader": "data/raw",
    "splitter": "[]",
    "embedder": "[]",
    "vector-store": "[]",
    "retriever": "what is ai-builder?",
    "llm": "Hello, what can you help me with?",
    "web-search": "latest AI news",
}


def _find_project_root() -> Path | None:
    """Walk up from cwd looking for a pyproject.toml that depends on ai-builder."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        pp = parent / "pyproject.toml"
        if pp.exists() and "ai-builder" in pp.read_text(errors="replace"):
            return parent
    return None


def _find_package_dir(project_root: Path) -> Path | None:
    """Find the Python package directory inside src/."""
    src = project_root / "src"
    if not src.is_dir():
        return None
    for child in sorted(src.iterdir()):
        if child.is_dir() and (child / "__init__.py").exists():
            return child
    return None


def _install_deps(deps: list[str], project_root: Path) -> bool:
    if not deps or UV_BIN is None:
        return True
    try:
        subprocess.run(
            [UV_BIN, "pip", "install", *deps],
            cwd=project_root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        return True
    except subprocess.CalledProcessError as exc:
        console.print(f"[yellow]Failed to install {', '.join(deps)}:[/yellow]")
        if exc.stdout:
            console.print(exc.stdout.decode(errors="replace"))
        return False


def _generate_tool_file(tool_name: str, info: dict[str, Any], pkg_dir: Path) -> Path:
    """Generate a ready-to-use tool wrapper in the project's tools/ directory."""
    tools_dir = pkg_dir / "tools"
    tools_dir.mkdir(exist_ok=True)

    init_file = tools_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("")

    safe_name = tool_name.replace("-", "_")
    target = tools_dir / f"{safe_name}.py"

    cls = info["class"]
    imp = info["import"]
    default_input = _DEFAULT_INPUTS.get(tool_name, "hello")

    target.write_text(f'''\
"""{tool_name} — added via `ai-builder add {tool_name}`.

Input:  {info["input"]}
Output: {info["output"]}
"""

{imp}
from ai_builder.core.tool import ToolInput


def run(data):
    """Run the {tool_name} tool and return its output."""
    tool = {cls}()
    result = tool.run(ToolInput(data=data))
    if not result.success:
        raise RuntimeError(f"{tool_name} failed: {{result.error}}")
    return result.data


if __name__ == "__main__":
    import json
    output = run("{default_input}")
    print(json.dumps(output, indent=2, default=str))
''')
    return target


def add_command(
    tool_name: str = typer.Argument(
        None,
        help="Built-in tool to add (loader, splitter, embedder, vector-store, retriever, llm, web-search)",
    ),
) -> None:
    """Add a built-in tool to the current project and install its dependencies."""
    if tool_name is None:
        _list_tools()
        return

    if tool_name not in TOOL_CATALOG:
        console.print(f"[red]Unknown tool:[/red] {tool_name}")
        _list_tools()
        raise typer.Exit(1)

    project_root = _find_project_root()
    if project_root is None:
        console.print("[red]Not inside an ai-builder project.[/red]")
        console.print("[dim]Run from a project created with `ai-builder create`.[/dim]")
        raise typer.Exit(1)

    pkg_dir = _find_package_dir(project_root)
    if pkg_dir is None:
        console.print("[red]Could not find Python package under src/.[/red]")
        raise typer.Exit(1)

    info = TOOL_CATALOG[tool_name]
    console.print(f"\n[bold]Adding [cyan]{tool_name}[/cyan] to {project_root.name}…[/bold]\n")

    if info["extras"]:
        console.print(f"  Installing: {', '.join(info['extras'])}")
        ok = _install_deps(info["extras"], project_root)
        if ok:
            console.print("  [green]✓ Dependencies installed[/green]")
        else:
            console.print(f"  [yellow]⚠ Install manually: uv pip install {' '.join(info['extras'])}[/yellow]")
    else:
        console.print("  [green]✓ No extra dependencies needed[/green]")

    generated = _generate_tool_file(tool_name, info, pkg_dir)
    rel_path = generated.relative_to(project_root)
    console.print(f"  [green]✓ Created {rel_path}[/green]")

    console.print(f"\n[bold]Tool contract:[/bold]")
    console.print(f"  Input:  [cyan]{info['input']}[/cyan]")
    console.print(f"  Output: [cyan]{info['output']}[/cyan]")

    console.print(f"\n[bold]Usage:[/bold]\n")
    console.print(f"  [cyan]{info['import']}[/cyan]")
    console.print(f"  [cyan]tool = {info['class']}()[/cyan]")
    console.print(f"  [cyan]result = tool.run(ToolInput(data=...))[/cyan]")

    if info.get("extras_hint"):
        console.print(
            f"\n[dim]Or install via extras: uv pip install -e \".[{info['extras_hint']}]\"[/dim]"
        )
    console.print()


def _list_tools() -> None:
    """Display available tools in a rich table."""
    table = Table(title="Available Built-in Tools", show_lines=True)
    table.add_column("Tool", style="bold cyan")
    table.add_column("Class", style="green")
    table.add_column("Input → Output")
    table.add_column("Extra Deps")

    for name, info in sorted(TOOL_CATALOG.items()):
        deps = ", ".join(info["extras"]) if info["extras"] else "none"
        table.add_row(
            name,
            info["class"],
            f"{info['input']}\n→ {info['output']}",
            deps,
        )

    console.print()
    console.print(table)
    console.print("\n[dim]Usage: ai-builder add <tool-name>[/dim]")
    console.print("[dim]Example: ai-builder add embedder[/dim]\n")
