"""Generate Mermaid.js diagram code from pipeline definitions."""

from __future__ import annotations

from typing import Any

STEP_ICONS = {
    "loader": "📄",
    "splitter": "✂️",
    "embedder": "🧮",
    "vector_store": "🗄️",
    "retriever": "🔍",
    "llm": "🤖",
    "source": "📥",
    "transform": "⚙️",
    "aggregate": "📊",
    "sink": "📤",
    "tool": "🔧",
    "agent": "🤖",
}


def generate_mermaid(pipeline_data: dict[str, Any]) -> str:
    """Generate Mermaid flowchart from a pipeline definition dict."""
    lines = ["graph LR"]
    steps = pipeline_data.get("steps", [])
    name = pipeline_data.get("name", "pipeline")

    if not steps:
        lines.append('    empty["No steps defined"]')
        return "\n".join(lines)

    for i, step in enumerate(steps):
        step_name = step.get("name", step.get("tool", f"step-{i}"))
        tool_type = step.get("tool", step.get("type", "tool"))
        icon = STEP_ICONS.get(tool_type, "🔧")
        config = step.get("config", {})

        node_id = f"s{i}"
        config_summary = _config_summary(config)
        label = f"{icon} {step_name}"
        if config_summary:
            label += f"\\n{config_summary}"

        lines.append(f'    {node_id}["{label}"]')

    for i in range(len(steps) - 1):
        lines.append(f"    s{i} --> s{i + 1}")

    # Style
    lines.append("")
    lines.append("    classDef default fill:#1a1a2e,stroke:#16213e,color:#e2e8f0,stroke-width:2px")
    lines.append("    classDef active fill:#0f3460,stroke:#533483,color:#e2e8f0,stroke-width:2px")

    return "\n".join(lines)


def _config_summary(config: dict) -> str:
    """Create a brief one-line summary of step config."""
    if not config:
        return ""
    parts = []
    for k, v in list(config.items())[:3]:
        val = str(v)
        if len(val) > 25:
            val = val[:22] + "..."
        parts.append(f"{k}: {val}")
    return " | ".join(parts)
