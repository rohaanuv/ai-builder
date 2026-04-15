"""ai-builder CLI — main entry point."""

import typer
from rich.console import Console

from ai_builder import __version__
from ai_builder.commands.create import create_app
from ai_builder.commands.run import run_command
from ai_builder.commands.visualize import visualize_command
from ai_builder.commands.serve import serve_command

console = Console()

app = typer.Typer(
    name="ai-builder",
    help="Lightweight CLI framework for building composable AI tools, agents, and pipelines.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

app.add_typer(create_app, name="create", help="Scaffold a new tool, agent, RAG pipeline, or data pipeline.")
app.command("run")(run_command)
app.command("visualize")(visualize_command)
app.command("serve")(serve_command)


@app.command()
def version() -> None:
    """Show ai-builder version."""
    console.print(f"ai-builder [bold green]v{__version__}[/bold green]")


@app.command()
def list_templates() -> None:
    """List available project templates."""
    from rich.table import Table

    table = Table(title="Available Templates", show_lines=True)
    table.add_column("Command", style="bold cyan")
    table.add_column("Description")
    table.add_column("Key Dependencies")

    table.add_row(
        "create tool <name>",
        "Composable tool with typed Input → Output",
        "ipykernel, pydantic",
    )
    table.add_row(
        "create agent-langchain <name>",
        "LangChain/LangGraph agent with tool calling",
        "langchain, langgraph, ipykernel",
    )
    table.add_row(
        "create agent-deep <name>",
        "Multi-agent deep research system",
        "langchain, langgraph, tavily-python",
    )
    table.add_row(
        "create rag <name>",
        "RAG pipeline: load → split → embed → store → retrieve",
        "sentence-transformers, faiss-cpu, ipykernel",
    )
    table.add_row(
        "create pipeline <name>",
        "Generic data pipeline with YAML-defined steps",
        "pandas, ipykernel",
    )
    console.print(table)
