"""ai-builder run — execute a tool, agent, or pipeline."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def run_command(
    path: Path = typer.Argument(
        Path("."), help="Path to a project directory or pipeline.yaml"
    ),
    input_data: str = typer.Option("", "--input", "-i", help="Input data string"),
    query: str = typer.Option("", "--query", "-q", help="Query string (for agents)"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Run a tool, agent, or pipeline from a project directory."""
    import importlib
    import logging
    import sys

    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s | %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")

    project = path.resolve()

    # Running a pipeline.yaml directly
    if project.is_file() and project.suffix in (".yaml", ".yml"):
        _run_pipeline_yaml(project, input_data)
        return

    if not project.is_dir():
        console.print(f"[red]Not found:[/red] {project}")
        raise typer.Exit(1)

    # Add project src/ to sys.path so imports work
    src_dir = project / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))

    # Detect project type from pyproject.toml metadata or main.py
    main_module = _find_main_module(project)
    if not main_module:
        console.print("[red]Cannot find main module.[/red] Expected src/<package>/main.py")
        raise typer.Exit(1)

    try:
        mod = importlib.import_module(main_module)
    except ImportError as exc:
        console.print(f"[red]Import error:[/red] {exc}")
        console.print("[dim]Hint: run 'uv sync' in the project directory first.[/dim]")
        raise typer.Exit(1) from exc

    # Look for standard entry points
    if hasattr(mod, "tool"):
        _run_tool(mod.tool, input_data)
    elif hasattr(mod, "agent"):
        _run_agent(mod.agent, query or input_data)
    elif hasattr(mod, "pipeline"):
        _run_pipeline_obj(mod.pipeline, input_data)
    elif hasattr(mod, "main"):
        mod.main()
    else:
        console.print("[red]No 'tool', 'agent', 'pipeline', or 'main' found in main.py[/red]")
        raise typer.Exit(1)


def _find_main_module(project: Path) -> str | None:
    """Discover the main module name from the project layout."""
    src = project / "src"
    if not src.exists():
        return None
    for pkg_dir in src.iterdir():
        if pkg_dir.is_dir() and (pkg_dir / "main.py").exists():
            return f"{pkg_dir.name}.main"
    return None


def _run_tool(tool_obj: object, input_data: str) -> None:
    from ai_builder.core.tool import BaseTool, ToolInput

    if not isinstance(tool_obj, BaseTool):
        console.print("[red]'tool' is not a BaseTool instance[/red]")
        raise typer.Exit(1)

    inp = ToolInput(data=input_data) if input_data else ToolInput()
    console.print(f"[bold]Running tool:[/bold] {tool_obj.name}\n")
    result = tool_obj.run(inp)
    _print_output(result.model_dump())


def _run_agent(agent_obj: object, query: str) -> None:
    from ai_builder.core.agent import BaseAgent

    if not isinstance(agent_obj, BaseAgent):
        console.print("[red]'agent' is not a BaseAgent instance[/red]")
        raise typer.Exit(1)

    if not query:
        console.print("[red]Provide a query with --query / -q[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]Running agent:[/bold] {agent_obj.name}\n")
    result = agent_obj.run(query)
    _print_output(result.model_dump())


def _run_pipeline_obj(pipeline_obj: object, input_data: str) -> None:
    from ai_builder.core.pipeline import Pipeline
    from ai_builder.core.tool import ToolInput

    if not isinstance(pipeline_obj, Pipeline):
        console.print("[red]'pipeline' is not a Pipeline instance[/red]")
        raise typer.Exit(1)

    inp = ToolInput(data=input_data) if input_data else ToolInput()
    console.print(f"[bold]Running pipeline:[/bold] {pipeline_obj.name}\n")
    result = pipeline_obj.run(inp)

    table = Table(title=f"Pipeline: {result.pipeline_name}")
    table.add_column("Step", style="cyan")
    table.add_column("Status")
    table.add_column("Duration", justify="right")

    for step in result.steps:
        status = "[green]OK[/green]" if step.success else f"[red]FAIL: {step.error}[/red]"
        table.add_row(step.step_name, status, f"{step.duration_ms:.0f}ms")

    console.print(table)
    console.print(f"\nTotal: {result.total_duration_ms:.0f}ms | Success: {result.success}\n")


def _run_pipeline_yaml(yaml_path: Path, input_data: str) -> None:
    console.print(f"[yellow]YAML pipeline execution requires a tool registry.[/yellow]")
    console.print(f"[dim]Use 'ai-builder run <project-dir>' instead, or import the pipeline in Python.[/dim]")


def _print_output(data: dict) -> None:
    from rich.json import JSON as RichJSON

    import json
    console.print(RichJSON(json.dumps(data, indent=2, default=str)))
