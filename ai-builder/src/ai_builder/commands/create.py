"""ai-builder create — scaffold new projects from templates."""

from pathlib import Path

import typer
from rich.console import Console

console = Console()

create_app = typer.Typer(no_args_is_help=True)


def _scaffold(template_name: str, project_name: str, output_dir: Path | None) -> None:
    """Common scaffolding logic — delegates to the appropriate template module."""
    from ai_builder.templates import TEMPLATE_REGISTRY

    if template_name not in TEMPLATE_REGISTRY:
        console.print(f"[red]Unknown template: {template_name}[/red]")
        raise typer.Exit(1)

    target = (output_dir or Path.cwd()) / project_name
    if target.exists():
        console.print(f"[red]Directory already exists:[/red] {target}")
        raise typer.Exit(1)

    generator = TEMPLATE_REGISTRY[template_name]
    generator(project_name, target)
    console.print(f"\n[bold green]✓[/bold green] Created [cyan]{project_name}[/cyan] at {target}")
    console.print(f"\n  [dim]cd {project_name} && uv sync[/dim]\n")


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
) -> None:
    """Create a RAG pipeline: load → split → embed → store → retrieve."""
    _scaffold("rag", name, output_dir)


@create_app.command("pipeline")
def create_pipeline(
    name: str = typer.Argument(help="Name of the pipeline (e.g. etl-sales)"),
    output_dir: Path | None = typer.Option(None, "--output", "-o", help="Parent directory"),
) -> None:
    """Create a generic data pipeline with YAML-defined steps."""
    _scaffold("pipeline", name, output_dir)
