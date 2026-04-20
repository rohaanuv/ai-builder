"""Template: ai-builder create agent-langchain <name>"""

from pathlib import Path

from ai_builder.templates import register, _to_snake, _write
from ai_builder.deploy.generators import (
    generate_dockerfile, generate_docker_compose,
    generate_k8s_deployment, generate_k8s_service, generate_k8s_configmap, generate_k8s_hpa,
)


@register("agent-langchain")
def generate(name: str, target: Path, **_kwargs: object) -> None:
    pkg = _to_snake(name)
    cls = "".join(w.capitalize() for w in name.split("-")) + "Agent"

    _write(target / "pyproject.toml", f"""\
[project]
name = "{name}"
version = "0.1.0"
description = "LangChain/LangGraph agent: {name}"
requires-python = ">=3.13"
dependencies = [
    "ai-builder @ git+https://github.com/rohaanuv/ai-builder.git",
    "pydantic>=2.0",
    "ipykernel>=6.29",
    "langfuse>=2.0",
]

[project.optional-dependencies]
langchain = [
    "langchain>=0.3",
    "langchain-openai>=0.3",
    "langchain-anthropic>=0.3",
    "langchain-community>=0.3",
    "langgraph>=0.2",
]
dev = ["pytest>=8.0"]
all = ["{name}[langchain]"]

[tool.setuptools.packages.find]
where = ["src"]

[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"
""")

    _write(target / "requirements.txt", f"""\
# Core (installed automatically)
ai-builder @ git+https://github.com/rohaanuv/ai-builder.git
pydantic>=2.0

# Add packages as needed — install with: uv pip install <package>
# Or install a group: uv pip install -e ".[langchain]"
#
# LangChain stack:  uv pip install langchain langchain-openai langgraph
# Anthropic:        uv pip install langchain-anthropic
# Community tools:  uv pip install langchain-community
# Note: ipykernel + langfuse ship with the default install.
#
# Or install everything at once: uv pip install -e ".[all]"
""")

    _write(target / ".env", f"""\
# {name} configuration
PROJECT_NAME={name}
LOG_LEVEL=INFO

# LLM (set after installing langchain extras)
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
# MODEL_NAME=gpt-4o-mini
# TEMPERATURE=0.7

LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENABLED=true
""")

    _write(target / "src" / pkg / "__init__.py", f"""\
\"\"\"
{name} — LangChain/LangGraph agent built with ai-builder.

Quick start (works immediately):

    from {pkg} import agent
    result = agent.run("Hello!")
    print(result.response)

Full LangChain agent (after installing extras):

    uv pip install -e ".[langchain]"
    # See examples/langchain_agent.py
\"\"\"

from {pkg}.main import agent, {cls}

__all__ = ["agent", "{cls}"]
""")

    # ── main.py — hello-world agent, no LangChain needed ──
    _write(target / "src" / pkg / "main.py", f"""\
\"\"\"
{name} — agent built with ai-builder.

This hello-world agent works immediately with zero optional packages.
It echoes your query and demonstrates the BaseAgent + AgentBus pattern.

    python -m {pkg}.main

To build a real LLM-powered agent with LangChain/LangGraph:

    uv pip install -e ".[langchain]"
    echo "OPENAI_API_KEY=sk-..." >> .env
    python examples/langchain_agent.py
\"\"\"

from ai_builder.core.agent import BaseAgent, AgentInput, AgentOutput
from ai_builder.core.communication import AgentBus, AgentMessage


class {cls}(BaseAgent):
    name = "{name}"
    description = "Hello-world agent (install langchain extras for LLM support)"

    def build_graph(self):
        return None

    def invoke(self, inp: AgentInput) -> AgentOutput:
        return AgentOutput(
            response=(
                f"Hello! You asked: {{inp.query}}\\n\\n"
                "This is the hello-world agent. To enable LLM-powered responses:\\n"
                "  uv pip install -e \\".[langchain]\\"\\n"
                "  echo \\"OPENAI_API_KEY=sk-...\\" >> .env\\n"
                "  python examples/langchain_agent.py"
            ),
            metadata={{"agent": self.name, "mode": "hello-world"}},
        )


agent = {cls}()

# Demonstrate AgentBus registration
bus = AgentBus()
bus.register_agent(agent)


if __name__ == "__main__":
    from ai_builder.tracing import Tracer, configure_tracing_from_env

    configure_tracing_from_env()
    Tracer.new_trace("{name}-agent")
    query = "What is AI?"
    print(f"Query: {{query}}\\n")
    try:
        result = agent.run(query)
        print(result.response)
    finally:
        Tracer.flush()
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

    # ── examples/langchain_agent.py — full LangGraph agent ──
    _write(target / "examples" / "langchain_agent.py", f"""\
\"\"\"
Full LangChain/LangGraph agent with tool calling.

Prerequisites:
    uv pip install -e ".[langchain]"
    echo "OPENAI_API_KEY=sk-..." >> .env

Usage:
    python examples/langchain_agent.py
\"\"\"

from typing import Any

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage

from ai_builder.core.agent import BaseAgent, AgentInput, AgentOutput
from {pkg}.config import {cls}Config


class State(TypedDict):
    messages: Annotated[list, add_messages]


class LangChain{cls}(BaseAgent):
    name = "{name}"
    description = "LangChain/LangGraph agent with tool calling"

    def __init__(self) -> None:
        self.config = {cls}Config()

    def build_graph(self) -> Any:
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
        return []

    def invoke(self, inp: AgentInput) -> AgentOutput:
        graph = self.build_graph()
        messages = [HumanMessage(content=inp.query)]
        result = graph.invoke({{"messages": messages}})
        last_msg = result["messages"][-1]

        return AgentOutput(
            response=last_msg.content,
            metadata={{"model": self.config.model_name}},
        )


if __name__ == "__main__":
    agent = LangChain{cls}()
    result = agent.run("What is the capital of France?")
    print(result.response)
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


def test_agent_runs():
    a = {cls}()
    result = a.run("Hello!")
    assert result.success
    assert "Hello" in result.response


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

## Quick Start (works immediately)

```bash
source .venv/bin/activate
python -m {pkg}.main
```

This runs a hello-world agent that echoes your query.
No API keys or extra packages needed.

## Level Up — LLM-Powered Agent

```bash
uv pip install -e ".[langchain]"
echo "OPENAI_API_KEY=sk-..." >> .env
python examples/langchain_agent.py
```

## Python API

```python
from {pkg} import agent

result = agent.run("What is AI?")
print(result.response)
```

## Agent-to-Agent Communication

```python
from ai_builder.core.communication import AgentBus, AgentMessage
from {pkg} import agent

bus = AgentBus()
bus.register_agent(agent)

response = bus.send(AgentMessage(
    sender="user",
    receiver="{name}",
    content="Analyze this data",
))
print(response.content)
```

## Optional Extras

```bash
uv pip install -e ".[langchain]"     # LangChain + LangGraph
uv pip install -e ".[all]"           # same (Langfuse + ipykernel are default deps)
```

## Configuration

Edit `.env` and set `LANGFUSE_*` to export traces to Langfuse (optional).

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
│   ├── main.py             # Hello-world agent (works immediately)
│   ├── config.py            # Pydantic settings
│   ├── tools/               # Custom LangChain tools
│   └── prompts/system.md    # System prompt
├── examples/
│   └── langchain_agent.py   # Full LangGraph agent
├── tests/
├── pipeline.yaml
├── Dockerfile
├── docker-compose.yml
├── k8s/
└── .env
```
""")
