"""
llm — Language model text generation tool.

Input:  LLMInput(data="prompt text")      -> user prompt (optional context in metadata)
Output: LLMOutput(data="generated text")  -> model response

Requires: openai / anthropic (optional deps)
"""

from ai_builder.tools.llm.config import LLMConfig
from ai_builder.tools.llm.main import LLMTool, LLMInput, LLMOutput

__all__ = ["LLMTool", "LLMConfig", "LLMInput", "LLMOutput"]
