"""ai-builder create — scaffold new projects from templates."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import typer
from rich.console import Console

console = Console()

create_app = typer.Typer(no_args_is_help=True)

UV_BIN = shutil.which("uv")


def _run_uv(args: list[str], cwd: Path) -> bool:
    """Run a uv command inside the project directory. Returns True on success."""
    if UV_BIN is None:
        console.print("[yellow]uv not found — skipping environment setup.[/yellow]")
        console.print("[dim]Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh[/dim]")
        return False
    try:
        subprocess.run(
            [UV_BIN, *args],
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        return True
    except subprocess.CalledProcessError as exc:
        console.print(f"[yellow]uv {' '.join(args)} failed:[/yellow]")
        if exc.stdout:
            console.print(exc.stdout.decode(errors="replace"))
        return False


def _scaffold(
    template_name: str,
    project_name: str,
    output_dir: Path | None,
    *,
    rag_choices: object | None = None,
) -> None:
    """Scaffold a project and auto-setup with uv (venv + install)."""
    from ai_builder.templates import TEMPLATE_REGISTRY

    if template_name not in TEMPLATE_REGISTRY:
        console.print(f"[red]Unknown template: {template_name}[/red]")
        raise typer.Exit(1)

    target = (output_dir or Path.cwd()) / project_name
    if target.exists():
        console.print(f"[red]Directory already exists:[/red] {target}")
        raise typer.Exit(1)

    generator = TEMPLATE_REGISTRY[template_name]
    kwargs: dict[str, object] = {}
    if template_name == "rag":
        kwargs["choices"] = rag_choices
    generator(project_name, target, **kwargs)
    console.print(f"\n[bold green]✓[/bold green] Created [cyan]{project_name}[/cyan] at {target}")

    # --- uv-based environment setup ---
    console.print("\n[bold]Setting up environment…[/bold]")

    venv_ok = _run_uv(["venv", ".venv"], cwd=target)
    if venv_ok:
        console.print("[green]  ✓ Virtual environment created (.venv)[/green]")

    install_ok = _run_uv(["pip", "install", "-e", "."], cwd=target)
    if install_ok:
        console.print("[green]  ✓ Core dependencies installed[/green]")

    # --- Done ---
    console.print(f"\n[bold green]Ready![/bold green] Next steps:\n")
    console.print(f"  [cyan]cd {project_name}[/cyan]")
    console.print(f"  [cyan]source .venv/bin/activate[/cyan]")
    if not install_ok:
        console.print(f"  [cyan]uv pip install -e \".\"[/cyan]")
    console.print()
    console.print("[dim]Add packages as you need them:[/dim]")
    console.print("[dim]  uv pip install <package>[/dim]")
    console.print("[dim]  uv pip install -e \".[all]\"     # install all optional deps[/dim]")
    console.print("[dim]See requirements.txt (and pyproject optional extras).[/dim]\n")


@create_app.command("tool")
def create_tool(
    name: str = typer.Argument(help="Name of the tool (e.g. my-embedder)"),
    output_dir: Path | None = typer.Option(None, "--output", "-o", help="Parent directory"),
) -> None:
    """Create a composable tool with typed Input → Output interface."""
    _scaffold("tool", name, output_dir)


@create_app.command("agent-langchain")
def create_agent_langchain(
    name: str = typer.Argument(help="Name of the agent (e.g. my-chatbot)"),
    output_dir: Path | None = typer.Option(None, "--output", "-o", help="Parent directory"),
) -> None:
    """Create a LangChain/LangGraph agent with tool calling."""
    _scaffold("agent-langchain", name, output_dir)


@create_app.command("agent-deep")
def create_agent_deep(
    name: str = typer.Argument(help="Name of the deep agent (e.g. research-bot)"),
    output_dir: Path | None = typer.Option(None, "--output", "-o", help="Parent directory"),
) -> None:
    """Create a multi-agent deep research system."""
    _scaffold("agent-deep", name, output_dir)


@create_app.command("rag")
def create_rag(
    name: str = typer.Argument(help="Name of the RAG pipeline (e.g. doc-search)"),
    output_dir: Path | None = typer.Option(None, "--output", "-o", help="Parent directory"),
    wizard: bool = typer.Option(
        True,
        "--wizard/--no-wizard",
        help="Interactive prompts for LLM, embeddings, vector DB, and document formats",
    ),
) -> None:
    """Create a RAG pipeline: load → split → embed → store → retrieve."""
    from ai_builder import __version__
    from ai_builder.commands.rag_wizard import prompt_rag_choices_optional

    console.print(f"[dim]ai-builder {__version__} — dependency profile[/dim]")
    choices = prompt_rag_choices_optional(wizard)
    _scaffold("rag", name, output_dir, rag_choices=choices)


@create_app.command("pipeline")
def create_pipeline(
    name: str = typer.Argument(help="Name of the pipeline (e.g. etl-sales)"),
    output_dir: Path | None = typer.Option(None, "--output", "-o", help="Parent directory"),
) -> None:
    """Create a generic data pipeline with YAML-defined steps."""
    _scaffold("pipeline", name, output_dir)
