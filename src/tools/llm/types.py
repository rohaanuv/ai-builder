"""Shared LLM tool input/output models."""

from __future__ import annotations

from pydantic import Field

from ai_builder.core.tool import ToolInput, ToolOutput


class LLMInput(ToolInput):
    """Input: prompt text in ``data``, optional ``metadata['context']`` for RAG."""

    data: str = Field(default="", description="User prompt")


class LLMOutput(ToolOutput):
    """Output: generated text in ``data``."""

    data: str = Field(default="", description="Generated response")
