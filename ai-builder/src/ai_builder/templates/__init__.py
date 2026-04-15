"""Template registry — maps template names to generator functions."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

GeneratorFn = Callable[[str, Path], None]

TEMPLATE_REGISTRY: dict[str, GeneratorFn] = {}

_PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"

_GITIGNORE = """\
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
.env
*.faiss
*.pkl
data/vectorstore/
.ruff_cache/
.pytest_cache/
"""


def register(name: str) -> Callable[[GeneratorFn], GeneratorFn]:
    """Decorator that registers a generator and wraps it to emit common files."""
    def decorator(fn: GeneratorFn) -> GeneratorFn:
        def wrapper(project_name: str, target: Path) -> None:
            fn(project_name, target)
            _write(target / ".python-version", _PYTHON_VERSION + "\n")
            _write(target / ".gitignore", _GITIGNORE)
        TEMPLATE_REGISTRY[name] = wrapper
        return wrapper
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
