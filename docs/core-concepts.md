# Core concepts

## Tools: `BaseTool`

Every tool follows **Input → Output**:

- Inputs and outputs subclass **`ToolInput`** / **`ToolOutput`** (Pydantic models).
- **`BaseTool.execute(inp)`** implements one step.
- **`BaseTool.run(inp)`** wraps execution with logging and uniform error handling.

Define a tool by subclassing **`BaseTool`** and setting **`name`**:

```python
from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput

class EchoTool(BaseTool):
    name = "echo"

    def execute(self, inp: ToolInput) -> ToolOutput:
        return ToolOutput(data=inp.data)
```

---

## Pipelines and the `|` operator

Two **`BaseTool`** instances compose with **`|`** into a **`Pipeline`**:

```python
from ai_builder.tools import DocumentLoader, TextSplitter
from ai_builder.core.tool import ToolInput

pipeline = DocumentLoader() | TextSplitter()
result = pipeline.run(ToolInput(data="data/raw/"))
```

The **first tool’s output** feeds the **next tool’s input**. **`Pipeline.run`** returns a structured result with per-step timing and success flags.

---

## Configuration: `BaseConfig`

Subclass **`BaseConfig`** (`ai_builder.core.config`) for pydantic-settings–backed configuration:

```python
from pathlib import Path
from ai_builder.core.config import BaseConfig

class AppConfig(BaseConfig):
    project_name: str = "demo"
    data_dir: Path = Path("data")
```

By default **`model_config`** reads **`.env`** from the working directory and maps **`FIELD_NAME`** ↔ environment variables (e.g. **`CHUNK_SIZE`** ↔ **`chunk_size`** depending on subclass fields).

See [Configuration and environment](configuration-and-environment.md).

---

## Agents: `BaseAgent`

Agents expose a higher-level **`run(query)`** (see **`core/agent.py`**) for LangChain-oriented scaffolds. Templates wire optional LLM backends when extras are installed.

---

## Agent-to-agent messaging: `AgentBus`

**`AgentBus`** registers **`BaseAgent`** instances and routes **`AgentMessage`** / **`AgentEvent`** payloads for multi-agent templates (`agent-deep`, …).

Imports:

```python
from ai_builder.core.communication import AgentBus, AgentMessage, AgentEvent
```

See **`core/communication.py`** for message shapes and discovery helpers.

---

## Visualization: `pipeline.yaml`

Declarative YAML lists steps for **documentation** and **`ai-builder visualize`** (Mermaid/HTML). Execution of arbitrary YAML pipelines from the CLI is not a full interpreter; prefer importing **`Pipeline`** objects in Python or using **`ai-builder run`** against **`main.py`**.
