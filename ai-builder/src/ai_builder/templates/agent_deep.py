"""Template: ai-builder create agent-deep <name>"""

from pathlib import Path

from ai_builder.templates import register, _to_snake, _write
from ai_builder.deploy.generators import (
    generate_dockerfile, generate_docker_compose,
    generate_k8s_deployment, generate_k8s_service, generate_k8s_configmap, generate_k8s_hpa,
)


@register("agent-deep")
def generate(name: str, target: Path) -> None:
    pkg = _to_snake(name)
    cls = "".join(w.capitalize() for w in name.split("-")) + "Agent"

    _write(target / "pyproject.toml", f"""\
[project]
name = "{name}"
version = "0.1.0"
description = "Multi-agent deep research system: {name}"
requires-python = ">=3.11"
dependencies = [
    "ai-builder @ git+https://github.com/rohaanuv/ai-builder.git#subdirectory=ai-builder",
    "langchain>=0.3",
    "langchain-openai>=0.3",
    "langchain-anthropic>=0.3",
    "langchain-community>=0.3",
    "langgraph>=0.2",
    "pydantic>=2.0",
    "tavily-python>=0.5",
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
langchain>=0.3
langchain-openai>=0.3
langchain-anthropic>=0.3
langchain-community>=0.3
langgraph>=0.2
pydantic>=2.0
tavily-python>=0.5
ipykernel>=6.29
""")

    _write(target / ".env", f"""\
# {name} configuration
PROJECT_NAME={name}
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
TAVILY_API_KEY=
MODEL_NAME=gpt-4o-mini
MAX_ITERATIONS=5
LOG_LEVEL=INFO
""")

    _write(target / "src" / pkg / "__init__.py", f"""\
from {pkg}.main import agent, {cls}

__all__ = ["agent", "{cls}"]
""")

    _write(target / "src" / pkg / "main.py", f"""\
\"\"\"
{name} — multi-agent deep research system.

Architecture:
    Supervisor → [Researcher, Analyst, Writer]

Sub-agents communicate via the AgentBus. The supervisor routes queries,
the researcher gathers information, the analyst extracts insights,
and the writer produces the final report.

Usage:
    from {pkg} import agent
    result = agent.run("Research the latest trends in AI agents")
\"\"\"

from typing import Any, Literal

from ai_builder.core.agent import BaseAgent, AgentInput, AgentOutput
from ai_builder.core.communication import AgentBus, AgentMessage, AgentCard
from {pkg}.config import {cls}Config


class {cls}(BaseAgent):
    name = "{name}"
    description = "Multi-agent deep research system with supervisor routing"

    def __init__(self) -> None:
        self.config = {cls}Config()
        self.bus = AgentBus()

    def build_graph(self) -> Any:
        from langchain_openai import ChatOpenAI
        from langgraph.graph import StateGraph, START, END
        from typing import TypedDict, Annotated
        from langgraph.graph.message import add_messages

        class State(TypedDict):
            messages: Annotated[list, add_messages]
            next_agent: str
            research: str
            analysis: str
            draft: str

        llm = ChatOpenAI(model=self.config.model_name, temperature=0.3)
        creative_llm = ChatOpenAI(model=self.config.model_name, temperature=0.7)

        def supervisor(state: State) -> dict:
            from langchain_core.messages import SystemMessage
            sys = SystemMessage(content=(
                "You are a supervisor routing tasks. Based on the conversation, "
                "decide which agent should act next: 'researcher', 'analyst', 'writer', or 'FINISH'. "
                "Respond with ONLY the agent name."
            ))
            resp = llm.invoke([sys] + state["messages"])
            next_step = resp.content.strip().lower()
            if next_step not in ("researcher", "analyst", "writer"):
                next_step = "FINISH"
            return {{"next_agent": next_step}}

        def researcher(state: State) -> dict:
            from langchain_core.messages import SystemMessage, AIMessage
            sys = SystemMessage(content=(
                "You are a research specialist. Gather facts and provide comprehensive findings."
            ))
            resp = llm.invoke([sys] + state["messages"])
            self.bus.broadcast(AgentMessage(
                sender="researcher", receiver="analyst",
                content=resp.content, message_type="event",
            ))
            return {{
                "messages": [AIMessage(content=f"[Researcher] {{resp.content}}")],
                "research": resp.content,
            }}

        def analyst(state: State) -> dict:
            from langchain_core.messages import SystemMessage, AIMessage
            research = state.get("research", "")
            sys = SystemMessage(content=f"Analyze this research and extract key insights:\\n\\n{{research}}")
            resp = llm.invoke([sys] + state["messages"])
            return {{
                "messages": [AIMessage(content=f"[Analyst] {{resp.content}}")],
                "analysis": resp.content,
            }}

        def writer(state: State) -> dict:
            from langchain_core.messages import SystemMessage, AIMessage
            analysis = state.get("analysis", "")
            sys = SystemMessage(content=f"Create a well-structured report from this analysis:\\n\\n{{analysis}}")
            resp = creative_llm.invoke([sys] + state["messages"])
            return {{
                "messages": [AIMessage(content=f"[Writer] {{resp.content}}")],
                "draft": resp.content,
            }}

        def route(state: State) -> Literal["researcher", "analyst", "writer", "__end__"]:
            next_step = state.get("next_agent", "FINISH")
            return "__end__" if next_step == "FINISH" else next_step

        graph = StateGraph(State)
        graph.add_node("supervisor", supervisor)
        graph.add_node("researcher", researcher)
        graph.add_node("analyst", analyst)
        graph.add_node("writer", writer)

        graph.add_edge(START, "supervisor")
        graph.add_conditional_edges("supervisor", route)
        for n in ("researcher", "analyst", "writer"):
            graph.add_edge(n, "supervisor")

        return graph.compile()

    def invoke(self, inp: AgentInput) -> AgentOutput:
        graph = self.build_graph()
        from langchain_core.messages import HumanMessage

        result = graph.invoke({{
            "messages": [HumanMessage(content=inp.query)],
            "next_agent": "", "research": "", "analysis": "", "draft": "",
        }})

        draft = result.get("draft") or result["messages"][-1].content
        return AgentOutput(
            response=draft,
            metadata={{
                "model": self.config.model_name,
                "agents_used": ["supervisor", "researcher", "analyst", "writer"],
                "bus_history_count": len(self.bus.history),
            }},
        )


agent = {cls}()
""")

    _write(target / "src" / pkg / "config.py", f"""\
from ai_builder.core.config import BaseConfig


class {cls}Config(BaseConfig):
    project_name: str = "{name}"
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.3
    max_tokens: int = 8192
    max_iterations: int = 5
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    tavily_api_key: str = ""
""")

    _write(target / "src" / pkg / "tools" / "__init__.py", "")

    _write(target / "src" / pkg / "prompts" / "system.md", f"""\
# {name} — Multi-Agent System

## Architecture
- **Supervisor**: Routes queries to specialist agents
- **Researcher**: Gathers information and facts
- **Analyst**: Extracts insights from research
- **Writer**: Produces final structured report

Sub-agents communicate via `AgentBus`.
""")

    _write(target / "pipeline.yaml", f"""\
name: {name}
description: Multi-agent deep research system
steps:
  - name: supervisor
    tool: supervisor
    type: agent
    config:
      role: router
  - name: researcher
    tool: researcher
    type: agent
    config:
      role: research
  - name: analyst
    tool: analyst
    type: agent
    config:
      role: analysis
  - name: writer
    tool: writer
    type: agent
    config:
      role: writing
""")

    _write(target / "tests" / "test_agent.py", f"""\
from {pkg}.main import {cls}
from ai_builder.core.communication import AgentBus, AgentMessage


def test_agent_creates():
    a = {cls}()
    assert a.name == "{name}"
    assert a.bus is not None


def test_bus_communication():
    bus = AgentBus()
    received = []

    def handler(msg):
        received.append(msg)
        return AgentMessage(sender="b", receiver="a", content="reply", message_type="response")

    bus.register("agent-b", handler)
    resp = bus.send(AgentMessage(sender="a", receiver="agent-b", content="hello"))
    assert resp is not None
    assert resp.content == "reply"
""")

    _write(target / "Dockerfile", generate_dockerfile(name, pkg))
    _write(target / "docker-compose.yml", generate_docker_compose(name, pkg))
    _write(target / "k8s" / "deployment.yaml", generate_k8s_deployment(name))
    _write(target / "k8s" / "service.yaml", generate_k8s_service(name))
    _write(target / "k8s" / "configmap.yaml", generate_k8s_configmap(name))
    _write(target / "k8s" / "hpa.yaml", generate_k8s_hpa(name))

    _write(target / "README.md", f"""\
# {name}

Multi-agent deep research system built with **ai-builder**.

## Architecture

```
User Query → Supervisor → Researcher → Supervisor → Analyst → Supervisor → Writer → Report
                 ↑                                                              |
                 └──────────────────────────────────────────────────────────────┘
```

Sub-agents communicate via `AgentBus` (Pydantic-typed messages).

## Quick Start

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." >> .env
ai-builder run . --query "Research the latest AI trends"
```

## Python API

```python
from {pkg} import agent

result = agent.run("Research the impact of LLMs on software engineering")
print(result.response)   # Structured report
print(result.metadata)   # Which agents were used
```

## Agent-to-Agent Communication

```python
from ai_builder.core.communication import AgentBus, AgentMessage

bus = AgentBus()
bus.register_agent(agent)
bus.register_agent(another_agent)

# Agents can now exchange messages
response = bus.send(AgentMessage(
    sender="coordinator",
    receiver="{name}",
    content="Research quantum computing trends",
))
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
| `TAVILY_API_KEY` | — | For web search |
| `MODEL_NAME` | `gpt-4o-mini` | LLM model |
| `MAX_ITERATIONS` | `5` | Max supervisor routing cycles |

## Deploy

```bash
docker compose up --build
kubectl apply -f k8s/
```

## Project Structure

```
{name}/
├── src/{pkg}/
│   ├── main.py            # Multi-agent graph (LangGraph)
│   ├── config.py           # Pydantic settings
│   ├── tools/              # Custom tools for sub-agents
│   └── prompts/system.md
├── tests/
├── pipeline.yaml
├── Dockerfile
├── docker-compose.yml
├── k8s/
└── .env
```
""")
