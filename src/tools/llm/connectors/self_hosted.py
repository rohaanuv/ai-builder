"""Self-hosted OpenAI-compatible servers (vLLM, LiteLLM, etc.)."""

from __future__ import annotations

from ai_builder.tools.llm.config import LLMConfig
from ai_builder.tools.llm.tool import LLMTool


def connect_self_hosted_llm(
    model: str,
    base_url: str,
    *,
    api_key: str = "",
    auth_token: str = "",
    username: str = "",
    password: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    system_prompt: str = "You are a helpful assistant.",
) -> LLMTool:
    return LLMTool(
        LLMConfig(
            provider="self_hosted",
            model=model,
            base_url=base_url.rstrip("/"),
            api_key=api_key,
            auth_token=auth_token,
            username=username,
            password=password,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        ),
    )


connectSelfHostedLLM = connect_self_hosted_llm
