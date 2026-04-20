"""ai-builder serve — lightweight web dashboard for pipeline visualization and monitoring."""

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def serve_command(
    path: Path = typer.Argument(Path("."), help="Project directory"),
    port: int = typer.Option(8501, "--port", "-p", help="Port to serve on"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind to"),
) -> None:
    """Start a lightweight web dashboard for pipeline visualization and run history."""
    try:
        from fastapi import FastAPI
        from fastapi.responses import HTMLResponse
        import uvicorn
    except ImportError:
        console.print("[red]Install serve dependencies:[/red] uv pip install 'ai-builder[serve]'")
        raise typer.Exit(1)

    project = path.resolve()

    web = FastAPI(title="ai-builder dashboard")

    @web.get("/", response_class=HTMLResponse)
    async def dashboard() -> str:
        from ai_builder.commands.visualize import _load_pipeline_data
        from ai_builder.visualize.mermaid import generate_mermaid
        from ai_builder.visualize.html_template import render_html

        pipeline_data = _load_pipeline_data(project)
        if not pipeline_data:
            return "<h1>No pipeline.yaml found</h1><p>Create a project first.</p>"

        mermaid_code = generate_mermaid(pipeline_data)
        return render_html(pipeline_data, mermaid_code, embedded=True)

    @web.get("/api/pipeline")
    async def pipeline_info() -> dict:
        from ai_builder.commands.visualize import _load_pipeline_data

        data = _load_pipeline_data(project)
        return data or {"error": "No pipeline.yaml found"}

    console.print(f"\n[bold green]ai-builder dashboard[/bold green] → http://{host}:{port}\n")
    uvicorn.run(web, host=host, port=port, log_level="warning")
