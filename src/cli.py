"""ai-builder CLI — main entry point."""

import typer
from rich.console import Console

from ai_builder import __version__
from ai_builder.commands.create import create_app
from ai_builder.commands.add import add_command
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
app.command("add")(add_command)
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
    table.add_column("Optional Extras")

    table.add_row(
        "create tool <name>",
        "Composable tool with typed Input → Output",
        "langfuse, dev",
    )
    table.add_row(
        "create agent-langchain <name>",
        "LangChain/LangGraph agent (hello-world runs without LLM)",
        "langchain, langfuse, dev",
    )
    table.add_row(
        "create agent-deep <name>",
        "Multi-agent research system (hello-world runs without LLM)",
        "langchain, search, langfuse, dev",
    )
    table.add_row(
        "create rag <name>",
        "RAG pipeline (wizard: embeddings, LLM, formats → requirements.txt)",
        "embeddings-local, docs, llm-openai, faiss, …",
    )
    table.add_row(
        "create pipeline <name>",
        "Data pipeline (hello-world: stdlib csv/json)",
        "pandas, langfuse, dev",
    )
    console.print(table)
    console.print()
    console.print("[dim]All templates work out-of-the-box with zero optional deps.[/dim]")
    console.print("[dim]Add tools on demand: ai-builder add <tool-name>[/dim]")
    console.print("[dim]See available tools: ai-builder add[/dim]")
