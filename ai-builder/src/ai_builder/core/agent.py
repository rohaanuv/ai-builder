"""Base agent interface for LangChain/LangGraph agents."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AgentInput(BaseModel):
    """Input to an agent — typically a user query plus optional context."""

    query: str
    context: dict[str, Any] = Field(default_factory=dict)
    chat_history: list[dict[str, str]] = Field(default_factory=list)

    model_config = {"extra": "allow"}


class AgentOutput(BaseModel):
    """Output from an agent — response text plus metadata."""

    response: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error: str | None = None

    model_config = {"extra": "allow"}


class BaseAgent(ABC):
    """
    Base class for ai-builder agents.

    Agents wrap LangChain / LangGraph graphs with a consistent interface.

    Usage:
        class MyAgent(BaseAgent):
            name = "my-agent"

            def build_graph(self):
                # Define your LangGraph StateGraph here
                ...

            def invoke(self, inp: AgentInput) -> AgentOutput:
                graph = self.build_graph()
                result = graph.invoke({"query": inp.query})
                return AgentOutput(response=result["output"])
    """

    name: str = "unnamed-agent"
    description: str = ""
    version: str = "0.1.0"

    @abstractmethod
    def build_graph(self) -> Any:
        """Build and return the LangGraph / LangChain graph."""
        ...

    @abstractmethod
    def invoke(self, inp: AgentInput) -> AgentOutput:
        """Run the agent on input and return output."""
        ...

    def run(self, query: str, **kwargs: Any) -> AgentOutput:
        """Convenience wrapper: string in, AgentOutput out."""
        inp = AgentInput(query=query, **kwargs)
        logger.info(f"[{self.name}] invoked with: {query[:80]}...")
        try:
            result = self.invoke(inp)
            logger.info(f"[{self.name}] completed (success={result.success})")
            return result
        except Exception as exc:
            logger.exception(f"[{self.name}] failed: {exc}")
            return AgentOutput(response="", success=False, error=str(exc))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
