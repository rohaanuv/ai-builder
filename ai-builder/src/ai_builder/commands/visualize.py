"""ai-builder visualize — generate interactive flow diagram from pipeline.yaml or project."""

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def visualize_command(
    path: Path = typer.Argument(Path("."), help="Project directory or pipeline.yaml"),
    output: Path = typer.Option(None, "--output", "-o", help="Output HTML file path"),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Open in browser"),
    format: str = typer.Option("html", "--format", "-f", help="Output format: html, mermaid, svg"),
) -> None:
    """Generate an interactive flow diagram from a pipeline definition."""
    project = path.resolve()

    # Find pipeline definition
    pipeline_data = _load_pipeline_data(project)
    if not pipeline_data:
        console.print("[red]No pipeline.yaml found.[/red]")
        console.print("[dim]Create one with 'ai-builder create rag <name>' or 'ai-builder create pipeline <name>'[/dim]")
        raise typer.Exit(1)

    from ai_builder.visualize.mermaid import generate_mermaid
    from ai_builder.visualize.html_template import render_html

    mermaid_code = generate_mermaid(pipeline_data)

    if format == "mermaid":
        out = output or (project / "pipeline.mmd" if project.is_dir() else project.with_suffix(".mmd"))
        out.write_text(mermaid_code)
        console.print(f"[green]Mermaid diagram written to:[/green] {out}")
        return

    # Generate HTML
    html = render_html(pipeline_data, mermaid_code)
    out = output or (project / "pipeline.html" if project.is_dir() else project.with_suffix(".html"))
    out.write_text(html)
    console.print(f"[bold green]✓[/bold green] Flow diagram generated: [cyan]{out}[/cyan]")

    if open_browser:
        import webbrowser
        webbrowser.open(f"file://{out.resolve()}")


def _load_pipeline_data(project: Path) -> dict | None:
    """Find and load pipeline definition from a project path."""
    import yaml

    candidates = []
    if project.is_file() and project.suffix in (".yaml", ".yml"):
        candidates = [project]
    elif project.is_dir():
        candidates = [
            project / "pipeline.yaml",
            project / "pipeline.yml",
            project / "pipelines" / "pipeline.yaml",
        ]

    for p in candidates:
        if p.exists():
            return yaml.safe_load(p.read_text())

    return None
