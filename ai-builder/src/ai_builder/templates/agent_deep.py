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
search = ["tavily-python>=0.5"]
dev = ["pytest>=8.0"]
all = ["{name}[langchain,search]"]

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
# Web search:       uv pip install tavily-python
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
# TAVILY_API_KEY=
# MODEL_NAME=gpt-4o-mini
# MAX_ITERATIONS=5

LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENABLED=true
""")

    _write(target / "src" / pkg / "__init__.py", f"""\
\"\"\"
{name} — multi-agent deep research system built with ai-builder.

Quick start (works immediately):

    from {pkg} import agent
    result = agent.run("Research topic X")
    print(result.response)

Full LLM-powered multi-agent system (after installing extras):

    uv pip install -e ".[langchain]"
    # See examples/langchain_deep.py
\"\"\"

from {pkg}.main import agent, {cls}

__all__ = ["agent", "{cls}"]
""")

    # ── main.py — hello-world multi-agent with AgentBus, no LLM ──
    _write(target / "src" / pkg / "main.py", f"""\
\"\"\"
{name} — multi-agent deep research system.

This hello-world demonstrates the multi-agent communication pattern
using AgentBus — no LLM or API keys needed.

Architecture:
    Supervisor → [Researcher, Analyst, Writer]

    python -m {pkg}.main

To build the full LLM-powered system:

    uv pip install -e ".[langchain]"
    echo "OPENAI_API_KEY=sk-..." >> .env
    python examples/langchain_deep.py
\"\"\"

from ai_builder.core.agent import BaseAgent, AgentInput, AgentOutput
from ai_builder.core.communication import AgentBus, AgentMessage


class ResearcherAgent(BaseAgent):
    name = "researcher"
    description = "Gathers information on a topic"

    def build_graph(self):
        return None

    def invoke(self, inp: AgentInput) -> AgentOutput:
        return AgentOutput(
            response=(
                f"Research findings on '{{inp.query}}':\\n"
                "1. This is a significant area of study.\\n"
                "2. Recent developments show promising results.\\n"
                "3. Multiple approaches have been proposed."
            ),
        )


class AnalystAgent(BaseAgent):
    name = "analyst"
    description = "Extracts insights from research"

    def build_graph(self):
        return None

    def invoke(self, inp: AgentInput) -> AgentOutput:
        return AgentOutput(
            response=(
                "Key insights:\\n"
                "- The field is rapidly evolving.\\n"
                "- Practical applications are emerging.\\n"
                "- Further investigation is warranted."
            ),
        )


class WriterAgent(BaseAgent):
    name = "writer"
    description = "Produces structured reports"

    def build_graph(self):
        return None

    def invoke(self, inp: AgentInput) -> AgentOutput:
        return AgentOutput(
            response=(
                "# Research Report\\n\\n"
                f"## Topic: {{inp.query}}\\n\\n"
                "Based on our research and analysis, here are the findings...\\n\\n"
                "(This is a hello-world demo. Install langchain extras for "
                "LLM-powered research.)"
            ),
        )


class {cls}(BaseAgent):
    \"\"\"Supervisor that coordinates the research team via AgentBus.\"\"\"

    name = "{name}"
    description = "Multi-agent deep research system with supervisor routing"

    def __init__(self) -> None:
        self.bus = AgentBus()
        self.bus.register_agent(ResearcherAgent())
        self.bus.register_agent(AnalystAgent())
        self.bus.register_agent(WriterAgent())

    def build_graph(self):
        return None

    def invoke(self, inp: AgentInput) -> AgentOutput:
        # Step 1: Research
        research_resp = self.bus.send(AgentMessage(
            sender=self.name, receiver="researcher", content=inp.query,
        ))
        research = research_resp.content if research_resp else ""

        # Step 2: Analyze
        analyst_resp = self.bus.send(AgentMessage(
            sender=self.name, receiver="analyst", content=str(research),
        ))
        analysis = analyst_resp.content if analyst_resp else ""

        # Step 3: Write report
        writer_resp = self.bus.send(AgentMessage(
            sender=self.name, receiver="writer", content=inp.query,
        ))
        report = writer_resp.content if writer_resp else ""

        return AgentOutput(
            response=str(report),
            metadata={{
                "agents_used": ["researcher", "analyst", "writer"],
                "bus_messages": len(self.bus.history),
                "mode": "hello-world",
            }},
        )


agent = {cls}()


if __name__ == "__main__":
    from ai_builder.tracing import Tracer, configure_tracing_from_env

    configure_tracing_from_env()
    Tracer.new_trace("{name}-deep-agent")
    query = "the impact of AI agents on software development"
    print(f"Query: {{query}}\\n")
    try:
        result = agent.run(query)
        print(result.response)
        print(f"\\nMetadata: {{result.metadata}}")
    finally:
        Tracer.flush()
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

    # ── examples/langchain_deep.py — full LangGraph multi-agent ──
    _write(target / "examples" / "langchain_deep.py", f"""\
\"\"\"
Full LLM-powered multi-agent deep research system.

Architecture: Supervisor → [Researcher, Analyst, Writer]
Uses LangGraph StateGraph for agent coordination.

Prerequisites:
    uv pip install -e ".[langchain]"
    echo "OPENAI_API_KEY=sk-..." >> .env

Usage:
    python examples/langchain_deep.py
\"\"\"

from typing import Any, Literal

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import TypedDict, Annotated

from ai_builder.core.agent import BaseAgent, AgentInput, AgentOutput
from {pkg}.config import {cls}Config


class State(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str
    research: str
    analysis: str
    draft: str


class LangChain{cls}(BaseAgent):
    name = "{name}"
    description = "LLM-powered multi-agent deep research system"

    def __init__(self) -> None:
        self.config = {cls}Config()

    def build_graph(self) -> Any:
        llm = ChatOpenAI(model=self.config.model_name, temperature=0.3)
        creative_llm = ChatOpenAI(model=self.config.model_name, temperature=0.7)

        def supervisor(state: State) -> dict:
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
            sys = SystemMessage(content=(
                "You are a research specialist. Gather facts and provide comprehensive findings."
            ))
            resp = llm.invoke([sys] + state["messages"])
            return {{
                "messages": [AIMessage(content=f"[Researcher] {{resp.content}}")],
                "research": resp.content,
            }}

        def analyst(state: State) -> dict:
            research = state.get("research", "")
            sys = SystemMessage(content=f"Analyze this research and extract key insights:\\n\\n{{research}}")
            resp = llm.invoke([sys] + state["messages"])
            return {{
                "messages": [AIMessage(content=f"[Analyst] {{resp.content}}")],
                "analysis": resp.content,
            }}

        def writer(state: State) -> dict:
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
            }},
        )


if __name__ == "__main__":
    from ai_builder.tracing import Tracer, configure_tracing_from_env

    configure_tracing_from_env()
    Tracer.new_trace("{name}-deep-langchain")
    agent = LangChain{cls}()
    try:
        result = agent.run("Research the latest trends in AI agents")
        print(result.response)
    finally:
        Tracer.flush()
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
from ai_builder.core.communication import AgentBus


def test_agent_runs():
    a = {cls}()
    result = a.run("test query")
    assert result.success
    assert "Research Report" in result.response


def test_agent_uses_bus():
    a = {cls}()
    result = a.run("test")
    assert result.metadata["bus_messages"] > 0
    assert "researcher" in result.metadata["agents_used"]
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

## Quick Start (works immediately)

```bash
source .venv/bin/activate
python -m {pkg}.main
```

This runs a hello-world multi-agent system where:
- **Supervisor** coordinates the team via `AgentBus`
- **Researcher** gathers information
- **Analyst** extracts insights
- **Writer** produces a report

No API keys or extra packages needed.

## Level Up — LLM-Powered Agents

```bash
uv pip install -e ".[langchain]"
echo "OPENAI_API_KEY=sk-..." >> .env
python examples/langchain_deep.py
```

## Python API

```python
from {pkg} import agent

result = agent.run("Research the impact of LLMs on software engineering")
print(result.response)
print(result.metadata)   # shows which agents were used
```

## Agent-to-Agent Communication

```python
from ai_builder.core.communication import AgentBus, AgentMessage
from {pkg} import agent

bus = AgentBus()
bus.register_agent(agent)

response = bus.send(AgentMessage(
    sender="coordinator",
    receiver="{name}",
    content="Research quantum computing trends",
))
```

## Optional Extras

```bash
uv pip install -e ".[langchain]"     # LangChain + LangGraph
uv pip install -e ".[search]"        # Tavily web search
uv pip install -e ".[all]"           # langchain + search (Langfuse + ipykernel are default deps)
```

## Deploy

```bash
docker compose up --build         # Docker
kubectl apply -f k8s/             # Kubernetes
```

## Project Structure

```
{name}/
├── src/{pkg}/
│   ├── main.py             # Hello-world multi-agent (works immediately)
│   ├── config.py
│   ├── tools/
│   └── prompts/system.md
├── examples/
│   └── langchain_deep.py   # Full LLM-powered multi-agent system
├── tests/
├── pipeline.yaml
├── Dockerfile
├── docker-compose.yml
├── k8s/
└── .env
```
""")
