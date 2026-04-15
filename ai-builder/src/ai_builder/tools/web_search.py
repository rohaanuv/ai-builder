"""Web search tool — search the web via Tavily or SerpAPI."""

from __future__ import annotations

import logging
import os
from typing import Any, Literal

from pydantic import BaseModel, Field

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput

logger = logging.getLogger(__name__)


class WebSearchConfig(BaseModel):
    provider: Literal["tavily", "serpapi"] = Field(default="tavily")
    api_key: str = Field(default="", description="API key (falls back to env var)")
    max_results: int = Field(default=5, ge=1, le=20)

    model_config = {"extra": "allow"}


class WebSearchInput(ToolInput):
    data: str = Field(default="", description="Search query")


class WebSearchOutput(ToolOutput):
    data: list[dict[str, Any]] = Field(default_factory=list, description="Search results")


class WebSearchTool(BaseTool[WebSearchInput, WebSearchOutput]):
    """Search the web and return structured results."""

    name = "web_search"
    description = "Search the web using Tavily or SerpAPI"
    version = "1.0.0"

    def __init__(self, config: WebSearchConfig | None = None) -> None:
        self.config = config or WebSearchConfig()

    def execute(self, inp: WebSearchInput) -> WebSearchOutput:
        query = inp.data if isinstance(inp.data, str) else ""
        if not query:
            return WebSearchOutput(data=[], success=False, error="No query")

        if self.config.provider == "tavily":
            return self._search_tavily(query)
        return WebSearchOutput(data=[], success=False, error=f"Provider {self.config.provider} not yet implemented")

    def _search_tavily(self, query: str) -> WebSearchOutput:
        try:
            from tavily import TavilyClient
        except ImportError:
            return WebSearchOutput(data=[], success=False, error="Install tavily-python: pip install tavily-python")

        key = self.config.api_key or os.getenv("TAVILY_API_KEY", "")
        if not key:
            return WebSearchOutput(data=[], success=False, error="TAVILY_API_KEY not set")

        client = TavilyClient(api_key=key)
        resp = client.search(query, max_results=self.config.max_results)

        results = [
            {"title": r.get("title", ""), "url": r.get("url", ""),
             "content": r.get("content", ""), "score": r.get("score", 0)}
            for r in resp.get("results", [])
        ]

        return WebSearchOutput(data=results, metadata={"query": query, "provider": "tavily"})
