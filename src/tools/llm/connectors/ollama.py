"""Local Ollama via OpenAI-compatible HTTP API."""

from __future__ import annotations

from ai_builder.tools.llm.config import LLMConfig
from ai_builder.tools.llm.tool import LLMTool


def connect_ollama(
    model: str = "llama3.2",
    *,
    base_url: str = "http://localhost:11434",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    system_prompt: str = "You are a helpful assistant.",
) -> LLMTool:
    return LLMTool(
        LLMConfig(
            provider="ollama",
            model=model,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        ),
    )


connectOllama = connect_ollama
