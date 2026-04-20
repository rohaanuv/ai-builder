"""Shim: use ``ai_builder.tools.llm.tool`` or ``ai_builder.tools.llm`` instead."""

from ai_builder.tools.llm.tool import LLMTool, tool
from ai_builder.tools.llm.types import LLMInput, LLMOutput

__all__ = ["LLMTool", "LLMInput", "LLMOutput", "tool"]
