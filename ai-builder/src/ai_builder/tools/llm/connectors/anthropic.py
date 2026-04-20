"""Anthropic Messages API (direct API key)."""

from __future__ import annotations

from ai_builder.tools.llm.config import LLMConfig
from ai_builder.tools.llm.tool import LLMTool


def connect_anthropic(
    model: str = "claude-sonnet-4-20250514",
    *,
    api_key: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    system_prompt: str = "You are a helpful assistant.",
) -> LLMTool:
    return LLMTool(
        LLMConfig(
            provider="anthropic",
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        ),
    )


connectAnthropic = connect_anthropic
