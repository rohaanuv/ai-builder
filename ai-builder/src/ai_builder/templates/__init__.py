"""Template registry — maps template names to generator functions."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

# Each generator takes (project_name, target_dir) and creates the scaffold.
GeneratorFn = Callable[[str, Path], None]

TEMPLATE_REGISTRY: dict[str, GeneratorFn] = {}


def register(name: str) -> Callable[[GeneratorFn], GeneratorFn]:
    """Decorator to register a template generator."""
    def decorator(fn: GeneratorFn) -> GeneratorFn:
        TEMPLATE_REGISTRY[name] = fn
        return fn
    return decorator


def _to_snake(name: str) -> str:
    """Convert 'my-tool-name' to 'my_tool_name'."""
    return name.replace("-", "_").replace(" ", "_").lower()


def _write(path: Path, content: str) -> None:
    """Write a file, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


# Import all template modules so they self-register
from ai_builder.templates import tool  # noqa: E402, F401
from ai_builder.templates import agent_langchain  # noqa: E402, F401
from ai_builder.templates import agent_deep  # noqa: E402, F401
from ai_builder.templates import rag  # noqa: E402, F401
from ai_builder.templates import pipeline  # noqa: E402, F401
