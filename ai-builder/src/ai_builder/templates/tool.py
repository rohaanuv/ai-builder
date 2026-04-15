"""Template: ai-builder create tool <name>"""

from pathlib import Path

from ai_builder.templates import register, _to_snake, _write
from ai_builder.deploy.generators import (
    generate_dockerfile, generate_docker_compose,
    generate_k8s_deployment, generate_k8s_service, generate_k8s_configmap, generate_k8s_hpa,
)


@register("tool")
def generate(name: str, target: Path) -> None:
    pkg = _to_snake(name)
    cls = "".join(w.capitalize() for w in name.split("-")) + "Tool"

    _write(target / "pyproject.toml", f"""\
[project]
name = "{name}"
version = "0.1.0"
description = "AI Builder tool: {name}"
requires-python = ">=3.11"
dependencies = [
    "ai-builder @ git+https://github.com/rohaanuv/ai-builder.git#subdirectory=ai-builder",
    "pydantic>=2.0",
]

[project.optional-dependencies]
langfuse = ["langfuse>=2.0"]
dev = ["pytest>=8.0", "ipykernel>=6.29"]

[tool.setuptools.packages.find]
where = ["src"]

[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"
""")

    _write(target / "requirements.txt", """\
ai-builder @ git+https://github.com/rohaanuv/ai-builder.git#subdirectory=ai-builder
pydantic>=2.0
ipykernel>=6.29
""")

    _write(target / ".env", f"""\
# {name} configuration
PROJECT_NAME={name}
LOG_LEVEL=INFO
""")

    _write(target / "src" / pkg / "__init__.py", f"""\
from {pkg}.main import tool, {cls}

__all__ = ["tool", "{cls}"]
""")

    _write(target / "src" / pkg / "main.py", f"""\
\"\"\"
{name} — composable tool with typed Input → Output.

Usage:
    from {pkg} import tool
    result = tool.run({cls}Input(data="hello"))

    # Pipe with other tools:
    pipeline = tool | other_tool
    result = pipeline.run(ToolInput(data="hello"))

    # With tracing:
    from ai_builder.tracing import traced_tool
    traced = traced_tool(tool)
    result = traced.run({cls}Input(data="hello"))
\"\"\"

from pydantic import Field

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput


class {cls}Input(ToolInput):
    \"\"\"Input schema for {name}.\"\"\"
    data: str = Field(default="", description="Input data to process")


class {cls}Output(ToolOutput):
    \"\"\"Output schema for {name}.\"\"\"
    data: str = Field(default="", description="Processed output")


class {cls}(BaseTool[{cls}Input, {cls}Output]):
    name = "{name}"
    description = "TODO: describe what this tool does"

    def execute(self, inp: {cls}Input) -> {cls}Output:
        # TODO: implement your tool logic here
        result = inp.data.upper()  # placeholder
        return {cls}Output(
            data=result,
            metadata={{**inp.metadata, "tool": self.name}},
        )


# Module-level instance for `ai-builder run`
tool = {cls}()
""")

    _write(target / "src" / pkg / "config.py", f"""\
from ai_builder.core.config import BaseConfig


class {cls}Config(BaseConfig):
    project_name: str = "{name}"
    # Add your config fields here
""")

    _write(target / "tests" / "test_main.py", f"""\
from {pkg}.main import {cls}, {cls}Input


def test_tool_runs():
    t = {cls}()
    result = t.run({cls}Input(data="hello world"))
    assert result.success
    assert result.data == "HELLO WORLD"


def test_tool_pipe():
    from ai_builder.core.pipeline import Pipeline
    t1 = {cls}()
    t2 = {cls}()
    p = t1 | t2
    assert isinstance(p, Pipeline)
    assert len(p.steps) == 2
""")

    _write(target / "pipeline.yaml", f"""\
name: {name}
steps:
  - name: {name}
    tool: {pkg}
    config: {{}}
""")

    _write(target / "Dockerfile", generate_dockerfile(name, pkg))
    _write(target / "docker-compose.yml", generate_docker_compose(name, pkg))
    _write(target / "k8s" / "deployment.yaml", generate_k8s_deployment(name))
    _write(target / "k8s" / "service.yaml", generate_k8s_service(name))
    _write(target / "k8s" / "configmap.yaml", generate_k8s_configmap(name))
    _write(target / "k8s" / "hpa.yaml", generate_k8s_hpa(name))

    _write(target / "README.md", f"""\
# {name}

Composable AI tool built with **ai-builder**.

## Quick Start

```bash
uv sync
ai-builder run . --input "hello world"
```

## Python API

```python
from {pkg} import tool
from {pkg}.main import {cls}Input

result = tool.run({cls}Input(data="hello world"))
print(result.data)       # "HELLO WORLD"
print(result.success)    # True
```

## Compose with Other Tools

```python
from {pkg} import tool
from other_tool import other

pipeline = tool | other
result = pipeline.run(ToolInput(data="input"))
```

## Tracing

```python
from ai_builder.tracing import traced_tool
traced = traced_tool(tool)
result = traced.run({cls}Input(data="test"))
```

## Configuration

Edit `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `PROJECT_NAME` | `{name}` | Project identifier |
| `LOG_LEVEL` | `INFO` | Logging level |

## Deploy

```bash
docker compose up --build         # Docker
kubectl apply -f k8s/             # Kubernetes
```

## Project Structure

```
{name}/
├── src/{pkg}/
│   ├── __init__.py
│   ├── main.py            # Tool implementation
│   └── config.py           # Pydantic settings
├── tests/
├── pipeline.yaml           # For visualization
├── Dockerfile
├── docker-compose.yml
├── k8s/
├── .env
└── pyproject.toml
```
""")
