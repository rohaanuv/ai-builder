"""Anthropic Claude on AWS Bedrock (see env: ANTHROPIC_MODEL, AWS_REGION, optional bearer)."""

from __future__ import annotations

import os

from ai_builder.tools.llm.config import LLMConfig
from ai_builder.tools.llm.tool import LLMTool


def connect_bedrock(
    model: str = "",
    *,
    aws_region: str = "",
    aws_access_key_id: str = "",
    aws_secret_access_key: str = "",
    aws_session_token: str = "",
    aws_bearer_token: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    system_prompt: str = "You are a helpful assistant.",
) -> LLMTool:
    """Uses ``ANTHROPIC_MODEL`` when ``model`` is empty; honors ``CLAUDE_CODE_MAX_OUTPUT_TOKENS`` at runtime."""
    resolved_model = model or os.getenv("ANTHROPIC_MODEL", "") or os.getenv("ANTHROPIC_SMALL_FAST_MODEL", "")
    cfg = LLMConfig(
        provider="bedrock",
        model=resolved_model,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
        aws_region=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        aws_bearer_token=aws_bearer_token or os.getenv("AWS_BEARER_TOKEN_BEDROCK", ""),
    )
    _ = os.getenv("CLAUDE_CODE_USE_BEDROCK", "")  # documented hook for tooling; no-op here
    return LLMTool(cfg)


connectBedrock = connect_bedrock
