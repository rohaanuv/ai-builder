"""Render a self-contained interactive HTML page with the pipeline flow diagram."""

from __future__ import annotations

from typing import Any

import json


def render_html(
    pipeline_data: dict[str, Any],
    mermaid_code: str,
    embedded: bool = False,
) -> str:
    """Generate a complete HTML page with Mermaid diagram and pipeline metadata."""
    name = pipeline_data.get("name", "pipeline")
    steps = pipeline_data.get("steps", [])
    steps_json = json.dumps(steps, indent=2, default=str)

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{name} — ai-builder</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{
            --bg: #0f0f1a;
            --surface: #1a1a2e;
            --border: #16213e;
            --text: #e2e8f0;
            --text-dim: #94a3b8;
            --accent: #818cf8;
            --accent-dim: #4f46e5;
            --success: #34d399;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }}
        .header {{
            padding: 1.5rem 2rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .header h1 {{
            font-size: 1.25rem;
            font-weight: 600;
        }}
        .header .badge {{
            background: var(--accent-dim);
            color: white;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            font-size: 0.75rem;
        }}
        .main {{
            display: grid;
            grid-template-columns: 1fr 320px;
            height: calc(100vh - 64px);
        }}
        .diagram-pane {{
            padding: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: auto;
        }}
        .diagram-pane .mermaid {{
            max-width: 100%;
        }}
        .sidebar {{
            background: var(--surface);
            border-left: 1px solid var(--border);
            padding: 1.5rem;
            overflow-y: auto;
        }}
        .sidebar h2 {{
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-dim);
            margin-bottom: 1rem;
        }}
        .step-card {{
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 0.5rem;
            padding: 0.75rem;
            margin-bottom: 0.75rem;
            transition: border-color 0.2s;
        }}
        .step-card:hover {{
            border-color: var(--accent);
        }}
        .step-card .step-name {{
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 0.25rem;
        }}
        .step-card .step-tool {{
            color: var(--accent);
            font-size: 0.8rem;
        }}
        .step-card .step-config {{
            margin-top: 0.5rem;
            font-size: 0.75rem;
            color: var(--text-dim);
            font-family: 'SF Mono', 'Fira Code', monospace;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .step-index {{
            display: inline-block;
            width: 1.5rem;
            height: 1.5rem;
            line-height: 1.5rem;
            text-align: center;
            background: var(--accent-dim);
            border-radius: 50%;
            font-size: 0.7rem;
            font-weight: 700;
            margin-right: 0.5rem;
        }}
        @media (max-width: 768px) {{
            .main {{ grid-template-columns: 1fr; }}
            .sidebar {{ border-left: none; border-top: 1px solid var(--border); }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{name}</h1>
        <span class="badge">{len(steps)} steps</span>
        <span class="badge" style="background: var(--success); color: #000;">ai-builder</span>
    </div>
    <div class="main">
        <div class="diagram-pane">
            <pre class="mermaid">
{mermaid_code}
            </pre>
        </div>
        <div class="sidebar">
            <h2>Pipeline Steps</h2>
            {"".join(_render_step_card(i, s) for i, s in enumerate(steps))}
        </div>
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            themeVariables: {{
                primaryColor: '#4f46e5',
                primaryTextColor: '#e2e8f0',
                primaryBorderColor: '#818cf8',
                lineColor: '#818cf8',
                secondaryColor: '#1a1a2e',
                tertiaryColor: '#0f3460',
                background: '#0f0f1a',
                mainBkg: '#1a1a2e',
                nodeBorder: '#818cf8',
            }},
            flowchart: {{
                curve: 'basis',
                padding: 20,
            }},
        }});
    </script>
</body>
</html>"""


def _render_step_card(index: int, step: dict) -> str:
    name = step.get("name", step.get("tool", f"step-{index}"))
    tool = step.get("tool", step.get("type", "unknown"))
    config = step.get("config", {})
    config_str = "\n".join(f"  {k}: {v}" for k, v in config.items()) if config else "  (default)"
    return f"""
            <div class="step-card">
                <div class="step-name"><span class="step-index">{index + 1}</span>{name}</div>
                <div class="step-tool">{tool}</div>
                <div class="step-config">{config_str}</div>
            </div>"""
