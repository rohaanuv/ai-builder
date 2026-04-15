"""Template: ai-builder create pipeline <name>"""

from pathlib import Path

from ai_builder.templates import register, _to_snake, _write
from ai_builder.deploy.generators import (
    generate_dockerfile, generate_docker_compose,
    generate_k8s_deployment, generate_k8s_service, generate_k8s_configmap, generate_k8s_hpa,
)


@register("pipeline")
def generate(name: str, target: Path) -> None:
    pkg = _to_snake(name)
    cls = "".join(w.capitalize() for w in name.split("-"))

    _write(target / "pyproject.toml", f"""\
[project]
name = "{name}"
version = "0.1.0"
description = "Data pipeline: {name}"
requires-python = ">=3.11"
dependencies = [
    "ai-builder @ git+https://github.com/rohaanuv/ai-builder.git#subdirectory=ai-builder",
    "pandas>=2.2",
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
pandas>=2.2
pydantic>=2.0
ipykernel>=6.29
""")

    _write(target / ".env", f"""\
PROJECT_NAME={name}
INPUT_PATH=data/input/
OUTPUT_PATH=data/output/
LOG_LEVEL=INFO
""")

    _write(target / "src" / pkg / "__init__.py", f"""\
from {pkg}.main import pipeline

__all__ = ["pipeline"]
""")

    _write(target / "src" / pkg / "main.py", f"""\
\"\"\"
{name} — data pipeline: source → transform → aggregate → sink.

Usage:
    ai-builder run . --input data/input/sales.csv
\"\"\"

from {pkg}.source import DataSource
from {pkg}.transform import Transformer
from {pkg}.aggregate import Aggregator
from {pkg}.sink import DataSink

source = DataSource()
transform = Transformer()
aggregate = Aggregator()
sink = DataSink()

pipeline = source | transform | aggregate | sink
""")

    _write(target / "src" / pkg / "config.py", f"""\
from pathlib import Path
from ai_builder.core.config import BaseConfig


class {cls}Config(BaseConfig):
    project_name: str = "{name}"
    input_path: Path = Path("data/input")
    output_path: Path = Path("data/output")
""")

    _write(target / "src" / pkg / "source.py", f"""\
from pathlib import Path
import pandas as pd
from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput
from pydantic import Field
from typing import Any


class SourceOutput(ToolOutput):
    data: list[dict[str, Any]] = Field(default_factory=list)


class DataSource(BaseTool[ToolInput, SourceOutput]):
    name = "source"
    description = "Read CSV/JSON data files"

    def execute(self, inp: ToolInput) -> SourceOutput:
        path = Path(inp.data) if inp.data else Path("data/input")
        files = [path] if path.is_file() else list(path.glob("*.csv")) + list(path.glob("*.json"))
        if not files:
            return SourceOutput(data=[], success=False, error=f"No data files in {{path}}")

        records: list[dict] = []
        for f in files:
            df = pd.read_csv(f) if f.suffix == ".csv" else pd.read_json(f)
            records.extend(df.to_dict(orient="records"))

        return SourceOutput(data=records, metadata={{**inp.metadata, "rows": len(records)}})
""")

    _write(target / "src" / pkg / "transform.py", f"""\
from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput
from pydantic import Field
from typing import Any


class TransformOutput(ToolOutput):
    data: list[dict[str, Any]] = Field(default_factory=list)


class Transformer(BaseTool[ToolInput, TransformOutput]):
    name = "transform"
    description = "Apply data transformations"

    def execute(self, inp: ToolInput) -> TransformOutput:
        records = inp.data if isinstance(inp.data, list) else []
        if not records:
            return TransformOutput(data=[], success=False, error="No data to transform")
        # TODO: implement transformations
        transformed = [r for r in records if r]
        return TransformOutput(data=transformed, metadata={{**inp.metadata, "rows": len(transformed)}})
""")

    _write(target / "src" / pkg / "aggregate.py", f"""\
from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput
from pydantic import Field
from typing import Any
import pandas as pd


class AggregateOutput(ToolOutput):
    data: dict[str, Any] = Field(default_factory=dict)


class Aggregator(BaseTool[ToolInput, AggregateOutput]):
    name = "aggregate"
    description = "Compute summary statistics"

    def execute(self, inp: ToolInput) -> AggregateOutput:
        records = inp.data if isinstance(inp.data, list) else []
        if not records:
            return AggregateOutput(data={{}}, success=False, error="No data")
        df = pd.DataFrame(records)
        summary = {{"rows": len(df), "columns": list(df.columns)}}
        numeric = df.select_dtypes(include="number")
        if not numeric.empty:
            summary["stats"] = numeric.describe().to_dict()
        return AggregateOutput(data=summary, metadata={{**inp.metadata}})
""")

    _write(target / "src" / pkg / "sink.py", f"""\
import json
from pathlib import Path
from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput
from {pkg}.config import {cls}Config


class DataSink(BaseTool[ToolInput, ToolOutput]):
    name = "sink"
    description = "Write results to output file"

    def __init__(self) -> None:
        self.config = {cls}Config()

    def execute(self, inp: ToolInput) -> ToolOutput:
        out_dir = Path(self.config.output_path)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "output.json"
        out_file.write_text(json.dumps(inp.data, indent=2, default=str))
        return ToolOutput(data=str(out_file), metadata={{**inp.metadata, "output": str(out_file)}})
""")

    _write(target / "data" / "input" / ".gitkeep", "")
    _write(target / "data" / "output" / ".gitkeep", "")

    _write(target / "pipeline.yaml", f"""\
name: {name}
description: "Data pipeline: source → transform → aggregate → sink"
steps:
  - name: source
    tool: source
    type: source
    config:
      path: data/input/
  - name: transform
    tool: transform
    type: transform
    config: {{}}
  - name: aggregate
    tool: aggregate
    type: aggregate
    config: {{}}
  - name: sink
    tool: sink
    type: sink
    config:
      path: data/output/
""")

    _write(target / "tests" / "test_pipeline.py", f"""\
from {pkg}.source import DataSource
from {pkg}.transform import Transformer
from ai_builder.core.tool import ToolInput


def test_source_missing():
    s = DataSource()
    result = s.run(ToolInput(data="/nonexistent"))
    assert not result.success


def test_transform_passthrough():
    t = Transformer()
    result = t.run(ToolInput(data=[{{"a": 1}}, {{"b": 2}}]))
    assert result.success
    assert len(result.data) == 2
""")

    _write(target / "Dockerfile", generate_dockerfile(name, pkg))
    _write(target / "docker-compose.yml", generate_docker_compose(name, pkg))
    _write(target / "k8s" / "deployment.yaml", generate_k8s_deployment(name))
    _write(target / "k8s" / "service.yaml", generate_k8s_service(name))
    _write(target / "k8s" / "configmap.yaml", generate_k8s_configmap(name))
    _write(target / "k8s" / "hpa.yaml", generate_k8s_hpa(name))

    _write(target / "README.md", f"""\
# {name}

Data pipeline built with **ai-builder**.

## Architecture

```
data/input/  →  Source  →  Transform  →  Aggregate  →  Sink  →  data/output/
```

## Quick Start

```bash
uv sync
cp your-data.csv data/input/
ai-builder run . --input data/input/your-data.csv
```

## Python API

```python
from {pkg} import pipeline
from ai_builder.core.tool import ToolInput

result = pipeline.run(ToolInput(data="data/input/"))
print(f"Completed in {{result.total_duration_ms:.0f}}ms")
```

## Visualize

```bash
ai-builder visualize .
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `INPUT_PATH` | `data/input/` | Source data directory |
| `OUTPUT_PATH` | `data/output/` | Output directory |

## Deploy

```bash
docker compose up --build
kubectl apply -f k8s/
```

## Project Structure

```
{name}/
├── src/{pkg}/
│   ├── main.py            # Pipeline composition
│   ├── source.py           # Data source tool
│   ├── transform.py        # Transformation tool
│   ├── aggregate.py        # Aggregation tool
│   ├── sink.py             # Output tool
│   └── config.py
├── data/input/
├── data/output/
├── tests/
├── pipeline.yaml
├── Dockerfile
├── docker-compose.yml
├── k8s/
└── .env
```
""")
