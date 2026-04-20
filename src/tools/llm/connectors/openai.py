"""OpenAI Chat Completions."""

from __future__ import annotations

from ai_builder.tools.llm.config import LLMConfig
from ai_builder.tools.llm.tool import LLMTool


def connect_openai(
    model: str = "gpt-4o-mini",
    *,
    api_key: str = "",
    base_url: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    system_prompt: str = "You are a helpful assistant.",
) -> LLMTool:
    return LLMTool(
        LLMConfig(
            provider="openai",
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        ),
    )


connectOpenAI = connect_openai
