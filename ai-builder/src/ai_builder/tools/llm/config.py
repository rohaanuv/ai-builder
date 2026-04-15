"""Configuration for the LLM tool."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """Configuration for the LLM tool."""

    provider: Literal["openai", "anthropic", "ollama"] = Field(
        default="openai", description="LLM provider",
    )
    model: str = Field(default="gpt-4o-mini", description="Model identifier")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1)
    system_prompt: str = Field(default="You are a helpful assistant.")

    api_key: str = Field(default="", description="API key (falls back to env var)")
    base_url: str = Field(default="", description="Custom API base URL (for Ollama, etc.)")

    model_config = {"extra": "allow"}
