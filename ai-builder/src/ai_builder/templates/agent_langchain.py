"""Template: ai-builder create agent-langchain <name>"""

from pathlib import Path

from ai_builder.templates import register, _to_snake, _write
from ai_builder.deploy.generators import (
    generate_dockerfile, generate_docker_compose,
    generate_k8s_deployment, generate_k8s_service, generate_k8s_configmap, generate_k8s_hpa,
)


@register("agent-langchain")
def generate(name: str, target: Path) -> None:
    pkg = _to_snake(name)
    cls = "".join(w.capitalize() for w in name.split("-")) + "Agent"

    _write(target / "pyproject.toml", f"""\
[project]
name = "{name}"
version = "0.1.0"
description = "LangChain/LangGraph agent: {name}"
requires-python = ">=3.11"
dependencies = [
    "ai-builder @ git+https://github.com/rohaanuv/ai-builder.git#subdirectory=ai-builder",
    "pydantic>=2.0",
]

[project.optional-dependencies]
langchain = [
    "langchain>=0.3",
    "langchain-openai>=0.3",
    "langchain-anthropic>=0.3",
    "langchain-community>=0.3",
    "langgraph>=0.2",
]
langfuse = ["langfuse>=2.0"]
dev = ["pytest>=8.0", "ipykernel>=6.29"]
all = ["{name}[langchain,langfuse]"]

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
# Or install a group: uv pip install -e ".[langchain]"
#
# LangChain stack:  uv pip install langchain langchain-openai langgraph
# Anthropic:        uv pip install langchain-anthropic
# Community tools:  uv pip install langchain-community
# Tracing:          uv pip install langfuse
# Notebooks:        uv pip install ipykernel
#
# Or install everything at once: uv pip install -e ".[all]"
""")

    _write(target / ".env", f"""\
# {name} configuration
PROJECT_NAME={name}
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
MODEL_NAME=gpt-4o-mini
TEMPERATURE=0.7
LOG_LEVEL=INFO

# Langfuse (optional)
# LANGFUSE_PUBLIC_KEY=
# LANGFUSE_SECRET_KEY=
""")

    _write(target / "src" / pkg / "__init__.py", f"""\
from {pkg}.main import agent, {cls}

__all__ = ["agent", "{cls}"]
""")

    _write(target / "src" / pkg / "main.py", f"""\
\"\"\"
{name} — LangChain/LangGraph agent with tool calling.

Usage:
    from {pkg} import agent
    result = agent.run("What is the capital of France?")
    print(result.response)

Agent-to-agent communication:
    from ai_builder.core.communication import AgentBus
    bus = AgentBus()
    bus.register_agent(agent)
    bus.send(AgentMessage(sender="user", receiver="{name}", content="Hello"))
\"\"\"

from typing import Any

from ai_builder.core.agent import BaseAgent, AgentInput, AgentOutput
from {pkg}.config import {cls}Config


class {cls}(BaseAgent):
    name = "{name}"
    description = "LangChain/LangGraph agent with tool calling"

    def __init__(self) -> None:
        self.config = {cls}Config()

    def build_graph(self) -> Any:
        from langchain_openai import ChatOpenAI
        from langgraph.graph import StateGraph, START, END
        from langgraph.prebuilt import ToolNode
        from typing import TypedDict, Annotated
        from langgraph.graph.message import add_messages

        class State(TypedDict):
            messages: Annotated[list, add_messages]

        llm = ChatOpenAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
        )

        tools = self._get_tools()
        llm_with_tools = llm.bind_tools(tools) if tools else llm

        def agent_node(state: State) -> dict:
            return {{"messages": [llm_with_tools.invoke(state["messages"])]}}

        def should_continue(state: State) -> str:
            last = state["messages"][-1]
            if hasattr(last, "tool_calls") and last.tool_calls:
                return "tools"
            return END

        graph = StateGraph(State)
        graph.add_node("agent", agent_node)

        if tools:
            graph.add_node("tools", ToolNode(tools))
            graph.add_edge(START, "agent")
            graph.add_conditional_edges("agent", should_continue, {{"tools": "tools", END: END}})
            graph.add_edge("tools", "agent")
        else:
            graph.add_edge(START, "agent")
            graph.add_edge("agent", END)

        return graph.compile()

    def _get_tools(self) -> list:
        \"\"\"LangChain tools. Add custom tools in the tools/ directory.\"\"\"
        return []

    def invoke(self, inp: AgentInput) -> AgentOutput:
        graph = self.build_graph()
        from langchain_core.messages import HumanMessage

        messages = [HumanMessage(content=inp.query)]
        result = graph.invoke({{"messages": messages}})
        last_msg = result["messages"][-1]

        return AgentOutput(
            response=last_msg.content,
            metadata={{"model": self.config.model_name}},
        )


agent = {cls}()
""")

    _write(target / "src" / pkg / "config.py", f"""\
from ai_builder.core.config import BaseConfig


class {cls}Config(BaseConfig):
    project_name: str = "{name}"
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 4096
    openai_api_key: str = ""
    anthropic_api_key: str = ""
""")

    _write(target / "src" / pkg / "tools" / "__init__.py", f"""\
\"\"\"Custom LangChain tools for {name}. Import and add to _get_tools().\"\"\"
""")

    _write(target / "src" / pkg / "prompts" / "system.md", f"""\
# System Prompt for {name}

You are a helpful AI assistant. Answer questions accurately and concisely.
""")

    _write(target / "pipeline.yaml", f"""\
name: {name}
description: LangChain/LangGraph agent
steps:
  - name: input
    tool: agent
    type: agent
    config:
      model: gpt-4o-mini
  - name: process
    tool: agent
    type: agent
    config:
      tools: custom
  - name: output
    tool: agent
    type: agent
    config:
      format: text
""")

    _write(target / "tests" / "test_agent.py", f"""\
from {pkg}.main import {cls}
from ai_builder.core.communication import AgentBus, AgentMessage


def test_agent_creates():
    a = {cls}()
    assert a.name == "{name}"


def test_agent_registers_on_bus():
    a = {cls}()
    bus = AgentBus()
    bus.register_agent(a)
    assert "{name}" in bus.agents
""")

    _write(target / "Dockerfile", generate_dockerfile(name, pkg))
    _write(target / "docker-compose.yml", generate_docker_compose(name, pkg))
    _write(target / "k8s" / "deployment.yaml", generate_k8s_deployment(name))
    _write(target / "k8s" / "service.yaml", generate_k8s_service(name))
    _write(target / "k8s" / "configmap.yaml", generate_k8s_configmap(name))
    _write(target / "k8s" / "hpa.yaml", generate_k8s_hpa(name))

    _write(target / "README.md", f"""\
# {name}

LangChain/LangGraph agent built with **ai-builder**.

## Quick Start

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." >> .env
ai-builder run . --query "What is AI?"
```

## Python API

```python
from {pkg} import agent

result = agent.run("Explain quantum computing")
print(result.response)
```

## Agent-to-Agent Communication

```python
from ai_builder.core.communication import AgentBus, AgentMessage
from {pkg} import agent
from other_agent import other

bus = AgentBus()
bus.register_agent(agent)
bus.register_agent(other)

response = bus.send(AgentMessage(
    sender="other-agent",
    receiver="{name}",
    content="Analyze this data",
))
print(response.content)
```

## Adding Tools

Add LangChain `@tool` functions in `src/{pkg}/tools/`:

```python
from langchain_core.tools import tool

@tool
def search_db(query: str) -> str:
    \"\"\"Search the database.\"\"\"
    return "results..."
```

Then register in `main.py`:
```python
def _get_tools(self):
    from {pkg}.tools.my_tool import search_db
    return [search_db]
```

## Tracing

```python
from ai_builder.tracing import Tracer
Tracer.configure(backend="langfuse", public_key="pk-...", secret_key="sk-...")
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | OpenAI API key |
| `MODEL_NAME` | `gpt-4o-mini` | LLM model |
| `TEMPERATURE` | `0.7` | Generation temperature |

## Deploy

```bash
docker compose up --build         # Docker
kubectl apply -f k8s/             # Kubernetes
```

## Project Structure

```
{name}/
├── src/{pkg}/
│   ├── main.py            # Agent definition (LangGraph)
│   ├── config.py           # Pydantic settings
│   ├── tools/              # Custom LangChain tools
│   └── prompts/system.md   # System prompt
├── tests/
├── pipeline.yaml
├── Dockerfile
├── docker-compose.yml
├── k8s/
└── .env
```
""")
