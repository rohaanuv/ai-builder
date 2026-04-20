"""Shared input/output and config models for all document loaders."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from ai_builder.core.tool import ToolInput, ToolOutput


class LoaderInput(ToolInput):
    """Input: path to a directory or single file."""

    data: str = Field(default="data/raw", description="Source directory or file path")


class LoaderOutput(ToolOutput):
    """Output: list of {text, source, filename, format, chars} dicts."""

    data: list[dict[str, Any]] = Field(default_factory=list)


class LoaderConfig(BaseModel):
    """Configuration for directory walking."""

    source_dir: str = Field(default="data/raw", description="Directory to load documents from")
    supported_formats: list[str] = Field(
        default_factory=list,
        description="File extensions to process (e.g. ['.pdf'])",
    )
    recursive: bool = Field(default=True, description="Recurse into subdirectories")

    model_config = {"extra": "allow"}
