"""Base tool interface — every tool accepts typed input and produces typed output."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ToolInput(BaseModel):
    """Base input model. Subclass to define your tool's input schema."""

    data: Any = Field(default=None, description="Primary input data")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Passthrough metadata")

    model_config = {"extra": "allow"}


class ToolOutput(BaseModel):
    """Base output model. Subclass to define your tool's output schema."""

    data: Any = Field(default=None, description="Primary output data")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Passthrough metadata")
    success: bool = True
    error: str | None = None

    model_config = {"extra": "allow"}


InputT = TypeVar("InputT", bound=ToolInput)
OutputT = TypeVar("OutputT", bound=ToolOutput)


class BaseTool(ABC, Generic[InputT, OutputT]):
    """
    Base class for all ai-builder tools.

    Every tool is a function:  InputT → OutputT
    Tools compose via the | operator:  tool_a | tool_b  creates a Pipeline.

    Usage:
        class MyTool(BaseTool[MyInput, MyOutput]):
            name = "my-tool"
            description = "Does something useful"

            def execute(self, inp: MyInput) -> MyOutput:
                return MyOutput(data=process(inp.data))

        result = MyTool().run(MyInput(data="hello"))
    """

    name: str = "unnamed-tool"
    description: str = ""
    version: str = "0.1.0"

    @abstractmethod
    def execute(self, inp: InputT) -> OutputT:
        """Core logic. Override this in your tool."""
        ...

    def run(self, inp: InputT) -> OutputT:
        """Execute with logging and error handling."""
        logger.info(f"[{self.name}] starting")
        try:
            result = self.execute(inp)
            logger.info(f"[{self.name}] completed (success={result.success})")
            return result
        except Exception as exc:
            logger.exception(f"[{self.name}] failed: {exc}")
            return ToolOutput(data=None, success=False, error=str(exc))  # type: ignore[return-value]

    def __or__(self, other: BaseTool) -> "Pipeline":
        """Pipe operator: tool_a | tool_b creates a Pipeline."""
        from ai_builder.core.pipeline import Pipeline, PipelineStep

        steps = [
            PipelineStep(tool=self, name=self.name),
            PipelineStep(tool=other, name=other.name),
        ]
        return Pipeline(name=f"{self.name}|{other.name}", steps=steps)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
