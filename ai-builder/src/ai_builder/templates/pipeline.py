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
    "pydantic>=2.0",
    "ipykernel>=6.29",
    "langfuse>=2.0",
]

[project.optional-dependencies]
pandas = ["pandas>=2.2"]
dev = ["pytest>=8.0"]
all = ["{name}[pandas]"]

[tool.setuptools.packages.find]
where = ["src"]

[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"
""")

    _write(target / "requirements.txt", f"""\
# Core (installed automatically)
ai-builder @ git+https://github.com/rohaanuv/ai-builder.git#subdirectory=ai-builder
pydantic>=2.0

# Add packages as needed — install with: uv pip install <package>
# Or install a group: uv pip install -e ".[pandas]"
#
# Data processing:  uv pip install pandas
# Note: ipykernel + langfuse ship with the default install.
#
# Or install everything at once: uv pip install -e ".[all]"
""")

    _write(target / ".env", f"""\
PROJECT_NAME={name}
INPUT_PATH=data/input/
OUTPUT_PATH=data/output/
LOG_LEVEL=INFO

LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENABLED=true
""")

    _write(target / "src" / pkg / "__init__.py", f"""\
\"\"\"
{name} — data pipeline built with ai-builder.

Quick start (works immediately):

    from {pkg} import pipeline
    from ai_builder.core.tool import ToolInput
    result = pipeline.run(ToolInput(data="data/input/"))

For pandas-based processing:

    uv pip install -e ".[pandas]"
    # See examples/pandas_pipeline.py
\"\"\"

from {pkg}.main import pipeline

__all__ = ["pipeline"]
""")

    # ── main.py — hello-world pipeline using stdlib only ──
    _write(target / "src" / pkg / "main.py", f"""\
\"\"\"
{name} — data pipeline: source → transform → aggregate → sink.

This hello-world pipeline reads JSON/CSV using Python stdlib,
transforms and aggregates the data, and writes output — no extra
packages needed.

    python -m {pkg}.main

For pandas-based processing:

    uv pip install -e ".[pandas]"
    python examples/pandas_pipeline.py
\"\"\"

import csv
import json
from pathlib import Path
from typing import Any

from pydantic import Field

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput

from {pkg}.config import {cls}Config

config = {cls}Config()


class SourceOutput(ToolOutput):
    data: list[dict[str, Any]] = Field(default_factory=list)


class DataSource(BaseTool[ToolInput, SourceOutput]):
    name = "source"
    description = "Read CSV/JSON data files (stdlib — no pandas needed)"

    def execute(self, inp: ToolInput) -> SourceOutput:
        path = Path(inp.data) if inp.data else Path(config.input_path)
        files = [path] if path.is_file() else sorted(
            list(path.glob("*.csv")) + list(path.glob("*.json"))
        )
        if not files:
            return SourceOutput(data=[], success=False, error=f"No data files in {{path}}")

        records: list[dict[str, Any]] = []
        for f in files:
            if f.suffix == ".csv":
                with open(f, newline="", encoding="utf-8") as fh:
                    records.extend(csv.DictReader(fh))
            elif f.suffix == ".json":
                raw = json.loads(f.read_text(encoding="utf-8"))
                if isinstance(raw, list):
                    records.extend(raw)
                elif isinstance(raw, dict):
                    records.append(raw)

        return SourceOutput(data=records, metadata={{**inp.metadata, "rows": len(records)}})


class TransformOutput(ToolOutput):
    data: list[dict[str, Any]] = Field(default_factory=list)


class Transformer(BaseTool[ToolInput, TransformOutput]):
    name = "transform"
    description = "Apply data transformations"

    def execute(self, inp: ToolInput) -> TransformOutput:
        records = inp.data if isinstance(inp.data, list) else []
        if not records:
            return TransformOutput(data=[], success=False, error="No data to transform")
        # TODO: implement your transformations here
        transformed = [r for r in records if r]
        return TransformOutput(data=transformed, metadata={{**inp.metadata, "rows": len(transformed)}})


class AggregateOutput(ToolOutput):
    data: dict[str, Any] = Field(default_factory=dict)


class Aggregator(BaseTool[ToolInput, AggregateOutput]):
    name = "aggregate"
    description = "Compute summary statistics"

    def execute(self, inp: ToolInput) -> AggregateOutput:
        records = inp.data if isinstance(inp.data, list) else []
        if not records:
            return AggregateOutput(data={{}}, success=False, error="No data")

        columns = list(records[0].keys()) if records else []
        numeric_cols = []
        for col in columns:
            try:
                float(records[0][col])
                numeric_cols.append(col)
            except (ValueError, TypeError, KeyError):
                pass

        summary: dict[str, Any] = {{"rows": len(records), "columns": columns}}
        for col in numeric_cols:
            values = [float(r[col]) for r in records if r.get(col) is not None]
            if values:
                summary[f"{{col}}_sum"] = sum(values)
                summary[f"{{col}}_avg"] = sum(values) / len(values)
                summary[f"{{col}}_min"] = min(values)
                summary[f"{{col}}_max"] = max(values)

        return AggregateOutput(data=summary, metadata={{**inp.metadata}})


class DataSink(BaseTool[ToolInput, ToolOutput]):
    name = "sink"
    description = "Write results to output file"

    def execute(self, inp: ToolInput) -> ToolOutput:
        out_dir = Path(config.output_path)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "output.json"
        out_file.write_text(json.dumps(inp.data, indent=2, default=str))
        return ToolOutput(data=str(out_file), metadata={{**inp.metadata, "output": str(out_file)}})


source = DataSource()
transform = Transformer()
aggregate = Aggregator()
sink = DataSink()

pipeline = source | transform | aggregate | sink


if __name__ == "__main__":
    from ai_builder.tracing import Tracer, configure_tracing_from_env

    configure_tracing_from_env()
    Tracer.new_trace("{name}-pipeline")
    try:
        result = pipeline.run(ToolInput(data=str(config.input_path)))
        if result.success:
            print(f"Pipeline completed in {{result.total_duration_ms:.0f}}ms")
            for step in result.steps:
                print(f"  {{step.step_name}}: {{step.duration_ms:.0f}}ms")
            if result.final_output:
                print(f"\\nOutput: {{result.final_output.data}}")
        else:
            failed = next((s for s in result.steps if not s.success), None)
            print(f"Pipeline failed at '{{failed.step_name if failed else '?'}}': {{failed.error if failed else '?'}}")
    finally:
        Tracer.flush()
""")

    _write(target / "src" / pkg / "config.py", f"""\
from pathlib import Path
from ai_builder.core.config import BaseConfig


class {cls}Config(BaseConfig):
    project_name: str = "{name}"
    input_path: Path = Path("data/input")
    output_path: Path = Path("data/output")
""")

    # ── sample data so first run produces output ──
    _write(target / "data" / "input" / "sample.json", """\
[
  {"name": "Alice", "department": "Engineering", "salary": 95000},
  {"name": "Bob", "department": "Marketing", "salary": 72000},
  {"name": "Charlie", "department": "Engineering", "salary": 105000},
  {"name": "Diana", "department": "Sales", "salary": 68000},
  {"name": "Eve", "department": "Engineering", "salary": 110000}
]
""")

    _write(target / "data" / "output" / ".gitkeep", "")

    # ── examples/pandas_pipeline.py ──
    _write(target / "examples" / "pandas_pipeline.py", f"""\
\"\"\"
Data pipeline with pandas-based processing.

Prerequisites:
    uv pip install -e ".[pandas]"

Usage:
    python examples/pandas_pipeline.py
\"\"\"

from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import Field

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput

from {pkg}.config import {cls}Config

config = {cls}Config()


class DataFrameOutput(ToolOutput):
    data: list[dict[str, Any]] = Field(default_factory=list)


class PandasSource(BaseTool[ToolInput, DataFrameOutput]):
    name = "pandas-source"
    description = "Read data using pandas"

    def execute(self, inp: ToolInput) -> DataFrameOutput:
        path = Path(inp.data) if inp.data else Path(config.input_path)
        files = [path] if path.is_file() else sorted(
            list(path.glob("*.csv")) + list(path.glob("*.json"))
        )
        frames = []
        for f in files:
            df = pd.read_csv(f) if f.suffix == ".csv" else pd.read_json(f)
            frames.append(df)

        combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        return DataFrameOutput(data=combined.to_dict(orient="records"))


class PandasTransform(BaseTool[ToolInput, DataFrameOutput]):
    name = "pandas-transform"
    description = "Transform using pandas"

    def execute(self, inp: ToolInput) -> DataFrameOutput:
        df = pd.DataFrame(inp.data if isinstance(inp.data, list) else [])
        # TODO: your pandas transformations here
        return DataFrameOutput(data=df.to_dict(orient="records"))


class PandasAggregate(BaseTool[ToolInput, ToolOutput]):
    name = "pandas-aggregate"
    description = "Aggregate using pandas describe()"

    def execute(self, inp: ToolInput) -> ToolOutput:
        df = pd.DataFrame(inp.data if isinstance(inp.data, list) else [])
        summary = {{"rows": len(df), "columns": list(df.columns)}}
        numeric = df.select_dtypes(include="number")
        if not numeric.empty:
            summary["stats"] = numeric.describe().to_dict()
        return ToolOutput(data=summary)


if __name__ == "__main__":
    from ai_builder.core.tool import ToolInput

    pipeline = PandasSource() | PandasTransform() | PandasAggregate()
    result = pipeline.run(ToolInput(data=str(config.input_path)))

    if result.success:
        print(f"Pipeline completed in {{result.total_duration_ms:.0f}}ms")
        import json
        print(json.dumps(result.final_output.data, indent=2, default=str))
    else:
        print(f"Failed: {{result.steps[-1].error}}")
""")

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
from {pkg}.main import DataSource, Transformer
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


def test_pipeline_runs_with_sample():
    from {pkg} import pipeline
    result = pipeline.run(ToolInput(data="data/input/"))
    assert result.success
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

## Quick Start (works immediately)

```bash
source .venv/bin/activate
python -m {pkg}.main
```

This processes `data/input/sample.json` through the pipeline and writes
results to `data/output/output.json`. No extra packages needed.

## Architecture

```
data/input/  →  Source  →  Transform  →  Aggregate  →  Sink  →  data/output/
```

## Level Up — Pandas Processing

```bash
uv pip install -e ".[pandas]"
python examples/pandas_pipeline.py
```

## Python API

```python
from {pkg} import pipeline
from ai_builder.core.tool import ToolInput

result = pipeline.run(ToolInput(data="data/input/"))
print(f"Completed in {{result.total_duration_ms:.0f}}ms")
```

## Optional Extras

```bash
uv pip install -e ".[pandas]"        # pandas DataFrames
uv pip install -e ".[all]"           # pandas optional extra (Langfuse + ipykernel are default deps)
```

## Configuration

Edit `.env` — set `LANGFUSE_*` keys to send pipeline traces to Langfuse (optional).

| Variable | Default | Description |
|----------|---------|-------------|
| `INPUT_PATH` | `data/input/` | Source data directory |
| `OUTPUT_PATH` | `data/output/` | Output directory |

## Deploy

```bash
docker compose up --build         # Docker
kubectl apply -f k8s/             # Kubernetes
```

## Project Structure

```
{name}/
├── src/{pkg}/
│   ├── main.py             # Pipeline (stdlib — no pandas needed)
│   └── config.py
├── examples/
│   └── pandas_pipeline.py  # Pandas-based version
├── data/input/sample.json   # Sample data
├── data/output/
├── tests/
├── pipeline.yaml
├── Dockerfile
├── docker-compose.yml
├── k8s/
└── .env
```
""")
