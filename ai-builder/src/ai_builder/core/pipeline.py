"""Pipeline: compose tools into a directed chain with typed data flow."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput

logger = logging.getLogger(__name__)


@dataclass
class PipelineStep:
    """A single step in a pipeline."""

    tool: BaseTool
    name: str = ""
    config: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.tool.name


class StepResult(BaseModel):
    """Result of a single pipeline step execution."""

    step_name: str
    success: bool
    duration_ms: float
    output: ToolOutput | None = None
    error: str | None = None


class PipelineResult(BaseModel):
    """Result of a full pipeline run."""

    pipeline_name: str
    steps: list[StepResult] = []
    success: bool = True
    total_duration_ms: float = 0.0
    final_output: ToolOutput | None = None


class Pipeline:
    """
    Composable pipeline of tools.

    Build with the | operator or explicitly:

        pipeline = tool_a | tool_b | tool_c
        result = pipeline.run(ToolInput(data="hello"))

    Or from YAML:

        pipeline = Pipeline.from_yaml("pipeline.yaml", tool_registry)
    """

    def __init__(self, name: str = "pipeline", steps: list[PipelineStep] | None = None) -> None:
        self.name = name
        self.steps: list[PipelineStep] = steps or []

    def add(self, tool: BaseTool, name: str = "", **config: Any) -> "Pipeline":
        """Add a tool to the pipeline. Returns self for chaining."""
        self.steps.append(PipelineStep(tool=tool, name=name or tool.name, config=config))
        return self

    def __or__(self, other: BaseTool | "Pipeline") -> "Pipeline":
        """Extend with | operator."""
        if isinstance(other, Pipeline):
            return Pipeline(
                name=f"{self.name}|{other.name}",
                steps=self.steps + other.steps,
            )
        return Pipeline(
            name=self.name,
            steps=self.steps + [PipelineStep(tool=other, name=other.name)],
        )

    def run(self, initial_input: ToolInput) -> PipelineResult:
        """Execute all steps sequentially, piping output → input."""
        result = PipelineResult(pipeline_name=self.name)
        current_input = initial_input
        t0 = time.perf_counter()

        for step in self.steps:
            ts = time.perf_counter()
            try:
                output = step.tool.run(current_input)
                duration = (time.perf_counter() - ts) * 1000
                step_result = StepResult(
                    step_name=step.name,
                    success=output.success,
                    duration_ms=round(duration, 1),
                    output=output,
                    error=output.error,
                )
                result.steps.append(step_result)

                if not output.success:
                    result.success = False
                    logger.error(f"Pipeline stopped at step '{step.name}': {output.error}")
                    break

                current_input = ToolInput(data=output.data, metadata=output.metadata)
            except Exception as exc:
                duration = (time.perf_counter() - ts) * 1000
                result.steps.append(
                    StepResult(
                        step_name=step.name,
                        success=False,
                        duration_ms=round(duration, 1),
                        error=str(exc),
                    )
                )
                result.success = False
                break

        result.total_duration_ms = round((time.perf_counter() - t0) * 1000, 1)
        if result.steps and result.steps[-1].output:
            result.final_output = result.steps[-1].output

        return result

    def to_dict(self) -> dict[str, Any]:
        """Serialize pipeline definition (for YAML export / visualization)."""
        return {
            "name": self.name,
            "steps": [
                {"name": s.name, "tool": s.tool.name, "config": s.config}
                for s in self.steps
            ],
        }

    def to_yaml(self, path: str | Path) -> None:
        """Export pipeline definition to YAML."""
        Path(path).write_text(yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False))

    @classmethod
    def from_yaml(
        cls,
        path: str | Path,
        tool_registry: dict[str, BaseTool],
    ) -> "Pipeline":
        """Load pipeline from YAML definition + a tool registry."""
        data = yaml.safe_load(Path(path).read_text())
        pipeline = cls(name=data.get("name", "pipeline"))
        for step_def in data.get("steps", []):
            tool_name = step_def["tool"]
            if tool_name not in tool_registry:
                raise ValueError(f"Unknown tool '{tool_name}'. Available: {list(tool_registry)}")
            pipeline.add(
                tool=tool_registry[tool_name],
                name=step_def.get("name", tool_name),
                **step_def.get("config", {}),
            )
        return pipeline

    def __repr__(self) -> str:
        names = " → ".join(s.name for s in self.steps)
        return f"<Pipeline {self.name!r}: {names}>"
