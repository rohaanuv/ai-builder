"""Configuration for the web search tool."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class WebSearchConfig(BaseModel):
    provider: Literal["tavily", "serpapi"] = Field(default="tavily")
    api_key: str = Field(default="", description="API key (falls back to env var)")
    max_results: int = Field(default=5, ge=1, le=20)

    model_config = {"extra": "allow"}
